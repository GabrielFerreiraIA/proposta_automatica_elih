"""
Montagem da proposta: dados do parser + copy do motor -> HTML -> PDF.

O PDF é gerado pelo Chromium (Playwright) para que o resultado impresso seja
idêntico ao que se vê no navegador — inclusive Plus Jakarta Sans e Nunito, que
são baixadas do Google Fonts na primeira geração e ficam em cache.

Todo asset local (logos, capa, CSS) entra no HTML como data URI. Isso evita
depender de servidor de arquivos e faz o HTML intermediário ser portátil.
"""

from __future__ import annotations

import base64
import datetime as dt
import io
from difflib import SequenceMatcher
import mimetypes
import re
import unicodedata
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

from . import copy_engine
from .parser import Cotacao, Documento, resumo_rede

BASE = Path(__file__).resolve().parent
RAIZ = BASE.parent
STATIC = BASE / "static"
ASSETS = RAIZ / "assets"

# Pastas onde procuramos capa e logos de operadora, em ordem de prioridade.
# `assets/` é a canônica (é o volume montado no Docker); as demais existem para
# que arquivos largados na raiz do projeto funcionem sem precisar mover nada.
PASTAS_CAPA = [ASSETS / "capa", RAIZ / "Capa", RAIZ / "capa"]
PASTAS_LOGOS = [
    ASSETS / "logos_operadoras",
    RAIZ / "Logos_Operadoras",
    RAIZ / "logos_operadoras",
]
IMAGENS = {".png", ".jpg", ".jpeg", ".webp"}

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]

_env = Environment(
    loader=FileSystemLoader(BASE / "templates"),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


# Altura em pixels com que cada imagem entra no HTML. O PDF é impresso em
# slots de poucos milímetros: mandar o arquivo original (uma logo de 1600x600
# com 300 KB para um espaço de 14 mm) só infla o HTML e a memória do Chromium.
# Os valores abaixo dão mais de 700 dpi no slot — folga de sobra para impressão.
ALTURA_LOGO_OPERADORA = 400
ALTURA_MARCA_ELIH = 240
ALTURA_CAPA = 2100

_cache_uri: dict[tuple[str, float, int], str] = {}


def _data_uri(caminho: Path | None, altura: int | None = None) -> str | None:
    """
    Imagem como data URI, reduzida para a altura em que será exibida.

    O resultado fica em cache pela data de modificação do arquivo, então trocar
    uma logo continua tendo efeito imediato sem reprocessar a cada geração.
    """
    if not caminho or not caminho.exists():
        return None

    chave = (str(caminho), caminho.stat().st_mtime, altura or 0)
    if chave in _cache_uri:
        return _cache_uri[chave]

    mime = mimetypes.guess_type(caminho.name)[0] or "application/octet-stream"
    dados = caminho.read_bytes()

    # SVG é vetor: reduzir não faz sentido e só estragaria o arquivo.
    if altura and caminho.suffix.lower() != ".svg":
        try:
            from PIL import Image

            with Image.open(io.BytesIO(dados)) as im:
                # Transparência decide o formato: logo precisa de PNG para não
                # virar um retângulo branco sobre a coluna navy; a capa é uma
                # foto opaca de página inteira e em JPEG ocupa uma fração disso.
                tem_alfa = im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info

                if im.height > altura:
                    largura = max(1, round(im.width * altura / im.height))
                    im = im.resize((largura, altura), Image.LANCZOS)

                buf = io.BytesIO()
                if tem_alfa:
                    im.convert("RGBA").save(buf, format="PNG", optimize=True)
                    novo_mime = "image/png"
                else:
                    im.convert("RGB").save(buf, format="JPEG", quality=85, optimize=True)
                    novo_mime = "image/jpeg"

                if buf.tell() < len(dados):
                    dados, mime = buf.getvalue(), novo_mime
        except Exception:  # noqa: BLE001 — imagem exótica entra como está
            pass

    uri = f"data:{mime};base64,{base64.b64encode(dados).decode()}"
    _cache_uri[chave] = uri
    return uri


def _css_pdf() -> str:
    """
    CSS da proposta com as fontes embutidas, entregue inline no HTML.

    Inline em vez de data URI no <link> evita uma segunda camada de base64 sobre
    os ~590 KB de fontes, e mantém o HTML intermediário autocontido.
    """
    fontes = (STATIC / "css" / "fontes.css").read_text(encoding="utf-8")
    folha = (STATIC / "css" / "proposta.css").read_text(encoding="utf-8")
    return fontes + chr(10) + folha


def _slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _imagens(pastas: list[Path], extras: set[str] | None = None) -> list[Path]:
    """
    Imagens das pastas, sem repetir. O Windows não diferencia maiúsculas em
    caminho, então "Logos_Operadoras" e "logos_operadoras" são a mesma pasta e
    sem a deduplicação cada arquivo apareceria duas vezes.
    """
    exts = IMAGENS | (extras or set())
    vistos: set[Path] = set()
    achados: list[Path] = []
    for pasta in pastas:
        if not pasta.exists():
            continue
        for arq in sorted(pasta.iterdir()):
            if not arq.is_file() or arq.suffix.lower() not in exts:
                continue
            chave = arq.resolve()
            if chave in vistos:
                continue
            vistos.add(chave)
            achados.append(arq)
    return achados


def encontra_capa() -> Path | None:
    """Qualquer imagem nas pastas de capa; um arquivo chamado 'capa' tem preferência."""
    candidatos = _imagens(PASTAS_CAPA)
    preferidos = [p for p in candidatos if _slug(p.stem) == "capa"]
    return (preferidos or candidatos or [None])[0]


# Palavras que aparecem no nome de quase toda operadora e não ajudam a
# distinguir uma da outra.
GENERICAS = {"saude", "operadora", "plano", "planos", "logo", "seguro", "s", "sa"}


def _tokens(texto: str) -> set[str]:
    """Palavras significativas do nome, normalizadas."""
    brutas = re.split(r"[^a-z0-9]+", _slug(texto).replace("-", " "))
    return {t for t in brutas if t and t not in GENERICAS and not t.isdigit()}


def _pontua(operadora: str, arquivo: str) -> float:
    """
    Quão bem o nome do arquivo representa esta operadora (0 = não representa).

    Precisa ser tolerante porque o nome do arquivo raramente segue a grafia
    oficial: vem com a ordem invertida ("Unimed_seguros" para "Seguros Unimed"),
    com palavra genérica a mais ("Select_Operadora_Saúde") ou com a grafia
    trocada ("Transmontano" por "Trasmontano").
    """
    alvo, nome = _slug(operadora).replace("-", ""), _slug(arquivo).replace("-", "")
    if not alvo or not nome:
        return 0.0
    if alvo == nome:
        return 100.0

    t_alvo, t_nome = _tokens(operadora), _tokens(arquivo)
    if t_alvo and t_alvo == t_nome:
        return 90.0
    if t_alvo and t_alvo <= t_nome:
        # Todas as palavras da operadora estão no arquivo. Quanto menos sobra no
        # arquivo, mais específico o casamento — "Amil" perde para "Amil Black"
        # quando o arquivo é Amil_Black.
        return 80.0 - len(t_nome - t_alvo)
    if t_nome and t_nome <= t_alvo:
        return 70.0 - len(t_alvo - t_nome)
    if alvo in nome or nome in alvo:
        return 60.0 + min(len(alvo), len(nome)) / 100

    # Última tentativa: grafias quase iguais. O corte alto evita casar marcas
    # diferentes que por acaso se parecem.
    proximidade = SequenceMatcher(None, alvo, nome).ratio()
    return 50.0 + proximidade if proximidade >= 0.88 else 0.0


def encontra_logo_operadora(operadora: str | None) -> Path | None:
    """
    Melhor logo para a operadora, ou None se nenhuma representa bem.

    Avalia todos os arquivos e fica com o de maior pontuação — pegar o primeiro
    que "serve" faria "Amil Black" cair na logo da Amil, já que ela vem antes
    na ordem alfabética e o nome dela é um pedaço do outro.
    """
    if not operadora:
        return None
    melhor, melhor_nota = None, 0.0
    for arq in _imagens(PASTAS_LOGOS, {".svg"}):
        nota = _pontua(operadora, arq.stem)
        if nota > melhor_nota:
            melhor, melhor_nota = arq, nota
    return melhor


def operadoras_disponiveis() -> list[str]:
    return sorted({arq.stem for arq in _imagens(PASTAS_LOGOS, {".svg"})})


def _data_extenso(hoje: dt.date | None = None) -> str:
    hoje = hoje or dt.date.today()
    return f"{hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}"


def _titulo_capa(cot: Cotacao, coluna) -> str:
    plano = coluna.plano if coluna else (cot.operadora or "Plano de saúde")
    return f"{cot.operadora} {plano}" if cot.operadora and cot.operadora not in plano else plano


def _subtitulo_capa(cot: Cotacao, rede: dict, coluna) -> str:
    partes = []
    if coluna and coluna.total:
        partes.append(f"Total de {coluna.total} por mês para o grupo cotado")
    if rede["total_hospitais"]:
        partes.append(
            f"{rede['total_hospitais']} hospitais e {rede['total_laboratorios']} "
            f"laboratórios credenciados em {rede['regiao'].title()}"
        )
    return ". ".join(partes) + "." if partes else "Proposta personalizada de plano de saúde."


def aplica_atributos(bloco: Cotacao, ctx: dict[str, Any], ident: str | None = None) -> None:
    """
    Grava o que o corretor confirmou na tela para os atributos que o PDF não
    declara. `atributos` traz uma entrada por opção ("0:0"), e as chaves soltas
    valem como padrão para a opção principal.
    """
    por_opcao = (ctx.get("atributos") or {}).get(ident, {}) if ident else {}
    for campo in ("abrangencia", "coparticipacao"):
        valor = por_opcao.get(campo) or (ctx.get(campo) if ident in (None, (ctx.get("comparar") or [None])[0]) else None)
        if valor:
            setattr(bloco, campo, valor)


def _monta_planos(doc: Documento, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Descritivo completo de cada opção selecionada, na ordem escolhida."""
    ids = [i for i in (ctx.get("comparar") or []) if doc.opcao(i)]
    planos = []
    for ident in ids[:MAX_PLANOS]:
        bloco, coluna = doc.opcao(ident)
        aplica_atributos(bloco, ctx, ident)
        planos.append(_detalhe_plano(bloco, coluna, ctx))
    return planos


def _monta_comparativo(doc: Documento, ctx: dict[str, Any]) -> dict[str, Any] | None:
    """Tabela lado a lado — só faz sentido com 2+ opções."""
    if len(ctx.get("_planos") or []) < 2:
        return None

    comp = copy_engine.monta_comparativo(ctx["_planos"], recomendado=0)
    comp["leitura"] = comp["leitura"][: int(ctx.get("max_leitura", 4))]
    # As colunas saem na mesma ordem dos planos: devolve o ponto forte para a
    # página dedicada de cada um reforçar o que apareceu na tabela.
    for plano, coluna in zip(ctx["_planos"], comp["colunas"]):
        plano["destaque"] = coluna["destaque"]
        plano["destaque_desc"] = coluna["destaque_desc"]
        plano["recomendado"] = coluna["recomendado"]
    return comp


def _detalhe_plano(bloco: Cotacao, coluna, ctx: dict[str, Any]) -> dict[str, Any]:
    """
    Tudo que a seção dedicada a UM plano precisa: selos, resumo, tabela de
    valores, rede credenciada da região e reembolso.

    Cada plano tem a sua própria rede e a sua própria tabela de reembolso — por
    isso o descritivo é montado por plano, e não uma vez só para a proposta.
    """
    idx = bloco.colunas.index(coluna)
    regiao = ctx.get("regiao") or next(iter(bloco.regioes), "SÃO PAULO")
    rede = resumo_rede(
        bloco,
        regiao,
        limite_hosp=int(ctx.get("limite_hosp", 14)),
        limite_lab=int(ctx.get("limite_lab", 12)),
        cidades=ctx.get("cidades") or None,
    )

    linhas_idade = [r for r in coluna.valores_por_idade if r["faixa"] != "Totais"]
    vidas_total = next(
        (r.get("vidas") for r in coluna.valores_por_idade if r["faixa"] == "Totais"), None
    )
    limite_cidades = int(ctx.get("limite_cidades", 26))
    logo = encontra_logo_operadora(bloco.operadora)

    return {
        "cot": bloco,
        "coluna": coluna,
        "rede": rede,
        "badges": copy_engine.badges(bloco),
        "resumo": copy_engine.resumo_plano(bloco, rede, idx, int(ctx.get("max_resumo", 7))),
        "linhas_idade": linhas_idade,
        "tem_vidas": any(r.get("vidas") for r in linhas_idade),
        "vidas_total": vidas_total,
        # A per capita só agrega quando alguma faixa tem mais de uma vida —
        # caso contrário ela repete a tabela de valores linha por linha.
        "mostrar_per_capita": bool(coluna.per_capita)
        and any((r.get("vidas") or "1") not in ("1", "", None) for r in linhas_idade),
        "vigencia": next((c for c in bloco.chips if c.lower().startswith("até")), None),
        # A região INTERIOR chega a listar 100+ cidades; a proposta mostra as
        # primeiras e sinaliza o restante em vez de estourar a página.
        "cidades_exibidas": rede["cidades"][:limite_cidades],
        "cidades_restantes": max(0, len(rede["cidades"]) - limite_cidades),
        "reembolsos_exibidos": bloco.reembolsos[: int(ctx.get("max_reembolsos", 8))],
        "logo": _data_uri(logo, ALTURA_LOGO_OPERADORA) if logo else None,
    }


def monta_contexto(cot: Cotacao, ctx: dict[str, Any]) -> dict[str, Any]:
    planos: list[dict[str, Any]] = ctx.get("_planos") or []
    if not planos:
        idx = int(ctx.get("coluna_idx", 0))
        coluna = cot.colunas[idx] if idx < len(cot.colunas) else cot.colunas[0]
        aplica_atributos(cot, ctx, (ctx.get("comparar") or [None])[0])
        planos = [_detalhe_plano(cot, coluna, ctx)]

    principal = planos[0]
    # O ajuste de página re-renderiza várias vezes até tudo caber. A copy não
    # muda entre essas tentativas — só o quanto dela cabe —, então ela é montada
    # uma vez e reaproveitada. Sem isso a IA era chamada a cada tentativa: cinco
    # chamadas por proposta, cinco vezes o custo e meio minuto a mais de espera,
    # o bastante para o proxy desistir.
    pronta = ctx.get("_copy_pronta")
    if pronta is None:
        copy = copy_engine.monta_copy(
            principal["cot"],
            principal["rede"],
            ctx,
            principal["cot"].colunas.index(principal["coluna"]),
        )
    else:
        copy = {**pronta, "objecoes": pronta["objecoes"][: int(ctx.get("max_objecoes", 4))]}
    capa = encontra_capa()

    return {
        # `cot` e `coluna` continuam apontando para o plano recomendado: é o que
        # a capa, o rodapé e o bloco de fechamento usam.
        "cot": principal["cot"],
        "coluna": principal["coluna"],
        "rede": principal["rede"],
        "planos": planos,
        "comparativo": ctx.get("_comparativo"),
        "copy": copy,
        "ctx": ctx,
        "vigencia": principal["vigencia"],
        "mostrar_diferenciais": bool(ctx.get("mostrar_diferenciais", True)),
        "titulo_capa": _titulo_capa(principal["cot"], principal["coluna"]),
        "subtitulo_capa": _subtitulo_capa(principal["cot"], principal["rede"], principal["coluna"]),
        "data_emissao": _data_extenso(),
        "capa_url": _data_uri(capa, ALTURA_CAPA) if capa else None,
        "logo_lockup": _data_uri(STATIC / "img" / "elih-lockup-white-on-navy.png", ALTURA_MARCA_ELIH),
        "logo_wordmark": _data_uri(STATIC / "img" / "elih-wordmark-navy.png", ALTURA_MARCA_ELIH),
        "logo_mark": _data_uri(STATIC / "img" / "elih-mark-circle.png", ALTURA_MARCA_ELIH),
        "css_inline": _css_pdf(),
    }


def render_html(cot: Cotacao, ctx: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    dados = monta_contexto(cot, ctx)
    return _env.get_template("proposta.html").render(**dados), dados


MEDE_OVERFLOW = """
() => Array.from(document.querySelectorAll('.page')).map(p => {
  const limite = p.getBoundingClientRect().bottom - parseFloat(getComputedStyle(p).paddingBottom);
  let excesso = 0;
  p.querySelectorAll('*').forEach(el => {
    if (el.offsetParent === null) return;
    excesso = Math.max(excesso, el.getBoundingClientRect().bottom - limite);
  });
  return Math.round(excesso);
})
"""


def render_pdf(html: str, destino: Path) -> Path:
    """Gera o PDF a partir de um HTML já pronto, sem auto-ajuste."""
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        try:
            _imprime(navegador, html, destino)
        finally:
            navegador.close()
    return destino


# Acima de 4 colunas a tabela comparativa deixa de ser legível numa folha A4.
MAX_PLANOS = 4


def _imprime(navegador, html: str, destino: Path) -> tuple[list[int], int]:
    """Imprime e devolve (transbordo por página, nº de páginas do PDF gerado)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    pagina = navegador.new_page(viewport={"width": 900, "height": 1273})
    try:
        pagina.set_content(html, wait_until="load")
        try:
            pagina.wait_for_function("document.fonts.status === 'loaded'", timeout=8000)
        except Exception:  # noqa: BLE001 — fonte é melhoria, não bloqueio
            pass
        overflow = pagina.evaluate(MEDE_OVERFLOW)
        pagina.pdf(
            path=str(destino),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        # Medir só o DOM não basta: quando um bloco com `break-inside: avoid`
        # não cabe, o Chromium o joga para uma página impressa nova sem que a
        # altura do DOM mude. O PDF ganha páginas e a medição não vê nada. Por
        # isso conferimos o arquivo de verdade.
        with fitz.open(destino) as pdf:
            paginas = pdf.page_count
        return overflow, paginas
    finally:
        pagina.close()


# Cada página tem seus próprios controles de densidade. Ajustar tudo junto numa
# escada só faz uma página apertada cortar conteúdo das outras — e pior, se a
# página do plano transborda, nenhum nível da escada a conserta. Por isso os
# controles são agrupados por página e avançam de forma independente.
NIVEIS: dict[str, list[dict[str, Any]]] = {
    "plano": [
        {"max_resumo": 7, "mostrar_diferenciais": True},
        {"max_resumo": 6, "mostrar_diferenciais": True},
        {"max_resumo": 5, "mostrar_diferenciais": True},
        {"max_resumo": 5, "mostrar_diferenciais": False},
        {"max_resumo": 4, "mostrar_diferenciais": False},
        {"max_resumo": 3, "mostrar_diferenciais": False},
    ],
    "rede": [
        {"limite_hosp": 14, "limite_lab": 12, "limite_cidades": 26, "max_reembolsos": 8},
        {"limite_hosp": 12, "limite_lab": 11, "limite_cidades": 24, "max_reembolsos": 7},
        {"limite_hosp": 11, "limite_lab": 10, "limite_cidades": 22, "max_reembolsos": 6},
        {"limite_hosp": 10, "limite_lab": 9, "limite_cidades": 18, "max_reembolsos": 5},
        {"limite_hosp": 9, "limite_lab": 8, "limite_cidades": 15, "max_reembolsos": 4},
        {"limite_hosp": 8, "limite_lab": 7, "limite_cidades": 12, "max_reembolsos": 4},
        {"limite_hosp": 6, "limite_lab": 5, "limite_cidades": 10, "max_reembolsos": 3},
    ],
    "fechamento": [
        {"max_objecoes": 4},
        {"max_objecoes": 3},
        {"max_objecoes": 2},
    ],
    "comparativo": [
        {"max_leitura": 4},
        {"max_leitura": 3},
        {"max_leitura": 2},
        {"max_leitura": 0},
    ],
}


def _grupos_das_paginas(tem_comparativo: bool, n_planos: int) -> list[str | None]:
    """
    Qual grupo de controles governa cada página, na ordem impressa:
    capa, comparativo (se houver), depois duas páginas por plano
    (valores e rede), e o fechamento.
    """
    grupos: list[str | None] = [None]
    if tem_comparativo:
        grupos.append("comparativo")
    for _ in range(n_planos):
        grupos += ["plano", "rede"]
    grupos.append("fechamento")
    return grupos


def _ajusta(base: dict[str, Any], niveis: dict[str, int]) -> dict[str, Any]:
    ctx = dict(base)
    for grupo, nivel in niveis.items():
        ctx.update(NIVEIS[grupo][min(nivel, len(NIVEIS[grupo]) - 1)])
    return ctx


def gera_proposta(
    origem: Documento | Cotacao, ctx: dict[str, Any], destino: Path
) -> tuple[Path, dict[str, Any]]:
    """
    Renderiza a proposta e mede o transbordo real de cada página no Chromium.
    A página que transbordar tem a própria densidade reduzida, sem penalizar as
    outras — assim a rede do Interior não come as quebras de objeção.
    """
    if isinstance(origem, Documento):
        ids = ctx.get("comparar") or []
        principal = origem.opcao(ids[0]) if ids and origem.opcao(ids[0]) else None
        cot = principal[0] if principal else origem.principal
        if principal:
            ctx = {**ctx, "coluna_idx": cot.colunas.index(principal[1])}
        documento = origem
    else:
        cot = origem
        documento = None

    destino.parent.mkdir(parents=True, exist_ok=True)
    niveis = {g: 0 for g in NIVEIS}

    with sync_playwright() as pw:
        navegador = pw.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        try:
            dados: dict[str, Any] = {}
            copy_pronta: dict[str, Any] | None = None
            for _ in range(sum(len(v) for v in NIVEIS.values())):
                tentativa = _ajusta(ctx, niveis)
                if documento is not None:
                    tentativa["_planos"] = _monta_planos(documento, tentativa)
                    tentativa["_comparativo"] = _monta_comparativo(documento, tentativa)
                tentativa["_copy_pronta"] = copy_pronta
                html, dados = render_html(cot, tentativa)
                # A primeira tentativa usa o nível mais completo: guardamos a copy
                # dela (já refinada pela IA) para as tentativas seguintes.
                if copy_pronta is None:
                    copy_pronta = dados["copy"]
                esperadas = len(_grupos_das_paginas(
                    bool(tentativa.get("_comparativo")), len(dados["planos"])
                ))
                overflow, paginas = _imprime(navegador, html, destino)
                dados["overflow"] = overflow
                dados["paginas"] = paginas
                dados["niveis"] = dict(niveis)

                grupos = _grupos_das_paginas(
                    bool(tentativa.get("_comparativo")), len(dados["planos"])
                )
                apertadas = {
                    grupos[i]
                    for i, excesso in enumerate(overflow)
                    if excesso > 0 and i < len(grupos) and grupos[i]
                }
                # Páginas a mais no PDF significam que algo não coube, mas sem
                # saber onde: aperta tudo que ainda dá para apertar.
                if paginas > esperadas and not apertadas:
                    apertadas = {g for g in NIVEIS if niveis[g] < len(NIVEIS[g]) - 1}

                dados["paginas_esperadas"] = esperadas
                if not apertadas and paginas <= esperadas:
                    return destino, dados
                if not apertadas or all(niveis[g] >= len(NIVEIS[g]) - 1 for g in apertadas):
                    break  # já está no mínimo; nada mais a reduzir
                for g in apertadas:
                    niveis[g] = min(niveis[g] + 1, len(NIVEIS[g]) - 1)

            return destino, dados
        finally:
            navegador.close()


def nome_arquivo(origem: Documento | Cotacao, ctx: dict[str, Any]) -> str:
    if isinstance(origem, Documento):
        ids = ctx.get("comparar") or []
        alvo = origem.opcao(ids[0]) if ids and origem.opcao(ids[0]) else None
        cot = alvo[0] if alvo else origem.principal
        plano = alvo[1].plano if alvo else (cot.colunas[0].plano if cot and cot.colunas else "plano")
        sufixo = "-comparativo" if len(ids) > 1 else ""
    else:
        cot = origem
        idx = int(ctx.get("coluna_idx", 0))
        plano = cot.colunas[idx].plano if idx < len(cot.colunas) else "plano"
        sufixo = ""
    partes = ["proposta", _slug(cot.operadora or "") if cot else "", _slug(plano), _slug(ctx.get("regiao", ""))]
    return "-".join(p for p in partes if p)[:104] + sufixo + ".pdf"
