"""
API e interface da ferramenta de propostas da Elih.

Fluxo: upload do PDF da operadora -> análise (`/api/analisar`) -> o corretor
confirma região, situação do cliente e o que o PDF não declarou -> geração
(`/api/gerar`) -> download do PDF remodelado.

A cotação analisada fica em cache de memória por `TTL_SESSAO` para que a
geração não precise reprocessar um PDF de 50+ páginas a cada ajuste.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .parser import Documento, cidades_da_regiao, parse_pdf, unifica
from .renderer import (
    RAIZ,
    encontra_capa,
    encontra_logo_operadora,
    gera_proposta,
    nome_arquivo,
    operadoras_disponiveis,
)

# Carrega OPENAI_API_KEY e ELIH_MODELO_IA do .env da raiz. Em produção as
# variáveis costumam vir do próprio ambiente e o .env simplesmente não existe.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE = Path(__file__).resolve().parent
UPLOADS = RAIZ / "output" / "_uploads"
SAIDAS = RAIZ / "output"
TTL_SESSAO = 60 * 60  # 1 hora
TAMANHO_MAX = 80 * 1024 * 1024  # 80 MB por arquivo — rede completa é pesada
MAX_ARQUIVOS = 5  # o corretor cota até 5 operadoras por proposta

app = FastAPI(title="Elih · Gerador de Propostas", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

_sessoes: dict[str, tuple[float, Documento]] = {}


def _limpa_sessoes() -> None:
    agora = time.time()
    for sid in [s for s, (t, _) in _sessoes.items() if agora - t > TTL_SESSAO]:
        _sessoes.pop(sid, None)
        for antigo in UPLOADS.glob(f"{sid}_*.pdf"):
            antigo.unlink(missing_ok=True)


def _sessao(sid: str) -> Documento:
    _limpa_sessoes()
    if sid not in _sessoes:
        raise HTTPException(404, "Sessão expirada. Envie o PDF novamente.")
    return _sessoes[sid][1]


def _bool(v: Any) -> bool:
    return str(v).lower() in ("1", "true", "sim", "on", "yes")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "tem_ia": bool(os.getenv("OPENAI_API_KEY")),
            "tem_capa": encontra_capa() is not None,
            "logos_operadoras": operadoras_disponiveis(),
        },
    )


@app.get("/manifest.webmanifest", include_in_schema=False)
def manifest():
    return FileResponse(BASE / "static" / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/sw.js", include_in_schema=False)
def service_worker():
    # Servido da raiz para o escopo do service worker cobrir o app inteiro.
    return FileResponse(
        BASE / "static" / "sw.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
    )


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE / "static" / "img" / "favicon.png", media_type="image/png")


@app.get("/api/saude")
def saude():
    return {"ok": True, "ia": bool(os.getenv("OPENAI_API_KEY")), "modelo": os.getenv("ELIH_MODELO_IA", "gpt-4o-mini")}


@app.post("/api/analisar")
async def analisar(arquivos: list[UploadFile] = File(...)):
    """
    Recebe de 1 a 5 PDFs de cotação e devolve tudo unificado.

    Cada operadora costuma ser cotada num PDF separado; a proposta final precisa
    de todas juntas para montar o comparativo. Os blocos entram numa lista única
    na ordem de envio, e cada opção é identificada por "bloco:coluna".
    """
    arquivos = [a for a in arquivos if a.filename]
    if not arquivos:
        raise HTTPException(400, "Envie ao menos um PDF.")
    if len(arquivos) > MAX_ARQUIVOS:
        raise HTTPException(400, f"Máximo de {MAX_ARQUIVOS} PDFs por proposta.")

    sid = uuid.uuid4().hex
    UPLOADS.mkdir(parents=True, exist_ok=True)
    documentos: list[Documento] = []
    lidos: list[dict[str, Any]] = []
    salvos: list[Path] = []

    try:
        for i, arquivo in enumerate(arquivos):
            nome = arquivo.filename or f"arquivo-{i + 1}.pdf"
            if not nome.lower().endswith(".pdf"):
                raise HTTPException(400, f"'{nome}' não é um PDF.")

            conteudo = await arquivo.read()
            if len(conteudo) > TAMANHO_MAX:
                raise HTTPException(413, f"'{nome}' passa de 80 MB.")

            caminho = UPLOADS / f"{sid}_{i}.pdf"
            caminho.write_bytes(conteudo)
            salvos.append(caminho)

            try:
                doc = parse_pdf(str(caminho))
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(422, f"Não consegui ler '{nome}': {exc}") from exc

            if not doc.blocos:
                raise HTTPException(
                    422,
                    f"Não encontrei tabela de valores em '{nome}'. Esta ferramenta "
                    "lê as cotações geradas pela plataforma (agencialink).",
                )

            for bloco in doc.blocos:
                bloco.origem = nome
            documentos.append(doc)
            lidos.append(
                {"nome": nome, "operadoras": doc.operadoras, "planos": len(doc.opcoes())}
            )
    except Exception:
        for caminho in salvos:
            caminho.unlink(missing_ok=True)
        raise

    doc = unifica(documentos)
    _limpa_sessoes()
    _sessoes[sid] = (time.time(), doc)

    # A rede é praticamente igual entre blocos da mesma UF; para o seletor de
    # região usamos a união do que aparece em todos eles.
    regioes: dict[str, list[str]] = {}
    for bloco in doc.blocos:
        for nome_regiao in bloco.regioes:
            atuais = regioes.setdefault(nome_regiao, [])
            for cidade in cidades_da_regiao(bloco, nome_regiao):
                if cidade not in atuais:
                    atuais.append(cidade)

    principal = doc.principal

    return JSONResponse(
        {
            "sessao": sid,
            "arquivos": lidos,
            "vendedor": principal.vendedor_nome,
            "referencia": principal.referencia,
            "segmento": principal.segmento,
            "operadoras": doc.operadoras,
            "blocos": len(doc.blocos),
            "opcoes": [
                {
                    **o,
                    "vigencia": next(
                        (c for c in doc.blocos[o["bloco"]].chips if c.lower().startswith("até")),
                        None,
                    ),
                    "reembolsos": len(doc.blocos[o["bloco"]].reembolsos),
                    "logo": bool(encontra_logo_operadora(o["operadora"])),
                    "faltando": [
                        campo
                        for campo, valor in (
                            ("abrangencia", o["abrangencia"]),
                            ("coparticipacao", o["coparticipacao"]),
                        )
                        if not valor
                    ],
                }
                for o in doc.opcoes()
            ],
            "regioes": [
                {"nome": nome_regiao, "cidades": cidades}
                for nome_regiao, cidades in regioes.items()
            ],
        }
    )


@app.post("/api/gerar")
def gerar(
    sessao: str = Form(...),
    regiao: str = Form(...),
    comparar: str = Form(""),
    cidades: str = Form(""),
    possui_plano: str = Form("nao"),
    tipo_cnpj: str = Form(""),
    atributos: str = Form("{}"),
    usar_ia: str = Form("nao"),
):
    doc = _sessao(sessao)

    ids = [i.strip() for i in comparar.split("|") if i.strip() and doc.opcao(i.strip())]
    if not ids:
        ids = [doc.opcoes()[0]["id"]] if doc.opcoes() else []
    if not ids:
        raise HTTPException(422, "Nenhum plano disponível neste PDF.")

    try:
        por_opcao = json.loads(atributos) or {}
    except json.JSONDecodeError:
        por_opcao = {}

    ctx: dict[str, Any] = {
        "regiao": regiao,
        "comparar": ids,
        "atributos": por_opcao,
        "cidades": [c.strip() for c in cidades.split("|") if c.strip()],
        "possui_plano": _bool(possui_plano),
        "tipo_cnpj": tipo_cnpj or None,
        "usar_ia": _bool(usar_ia) and bool(os.getenv("OPENAI_API_KEY")),
    }

    destino = SAIDAS / f"{sessao}_{nome_arquivo(doc, ctx)}"
    try:
        _, dados = gera_proposta(doc, ctx, destino)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"Falha ao gerar o PDF: {exc}") from exc

    return JSONResponse(
        {
            "url": f"/api/baixar/{destino.name}",
            "nome": nome_arquivo(doc, ctx),
            "motor": dados["copy"]["motor"],
            "objecoes": len(dados["copy"]["objecoes"]),
            "hospitais": dados["rede"]["total_hospitais"],
            "laboratorios": dados["rede"]["total_laboratorios"],
            "comparados": len(ids),
            "paginas": dados.get("paginas", 0),
        }
    )


@app.get("/api/baixar/{nome}")
def baixar(nome: str):
    caminho = (SAIDAS / nome).resolve()
    if caminho.parent != SAIDAS.resolve() or not caminho.exists():
        raise HTTPException(404, "Arquivo não encontrado.")
    return FileResponse(
        caminho,
        media_type="application/pdf",
        filename=nome.split("_", 1)[-1],
    )
