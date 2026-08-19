"""
Extração determinística de cotações geradas pela plataforma agencialink.com.

Regra de ouro deste módulo: ele NUNCA infere, arredonda ou reescreve um dado.
Tudo que sai daqui é texto literal do PDF de origem. Qualquer atributo que não
esteja escrito no PDF sai como None e é perguntado ao usuário na interface.

O layout do gerador é estável e os papéis de cada linha são identificáveis por
(cor da fonte, peso, coordenada x):

    x=23  cor 7107965  regular  -> nome do prestador
    x>450 cor 2172201  regular  -> tipos de atendimento do prestador
    x=23  cor 6513507  bold     -> categoria (Hospitais / Laboratórios / Rede Própria)
    x=31  cor 6709595  bold     -> cidade ou zona
    x=23  cor 2172201  bold     -> macro-região (SÃO PAULO, ABCD, INTERIOR, ...)
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any

import fitz  # PyMuPDF

COLOR_PROVIDER = 7107965
COLOR_TYPES = 2172201
COLOR_CATEGORY = 6513507
COLOR_CITY = 6709595

CATEGORIAS = {"Hospitais", "Laboratórios", "Rede Própria", "Clínicas", "Odontologia"}

LEGENDA_TIPOS = {
    "HOSP": "Internação eletiva",
    "H": "Internação eletiva",
    "MAT": "Maternidade",
    "M": "Maternidade",
    "PS": "Pronto-socorro",
    "PSI": "Pronto-socorro infantil",
    "AMB": "Ambulatório",
    "PA": "Pronto-atendimento",
    "LAB": "Laboratório",
    "CRED": "Rede própria credenciada",
}


def _norm(s: str) -> str:
    """Minúsculas sem acento, para comparações tolerantes."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


def _limpa(s: str) -> str:
    """
    Remove os glifos FontAwesome (private use area) que o gerador injeta e a
    barra invertida de escape que sobra em nomes como "Sta. Barbara D\\'Oeste"
    no PDF de origem. Nenhuma das duas carrega informação.
    """
    s = "".join(c for c in s if not (0xE000 <= ord(c) <= 0xF8FF))
    s = s.replace("\\'", "'").replace('\\"', '"')
    return re.sub(r"\s{2,}", " ", s).strip()


def _chips(bruto: str) -> list[str]:
    """No PDF cada chip é precedido de um ícone FontAwesome (private use area).
    Usar esses glifos como delimitadores é o único jeito estável de separá-los."""
    partes = re.split(r"[-]+", bruto)
    return [_limpa(p).strip(" -|") for p in partes if _limpa(p).strip(" -|")]


@dataclass
class Linha:
    page: int
    x0: float
    y0: float
    x1: float
    text: str
    color: int
    bold: bool
    size: float
    raw: str = ""


@dataclass
class Prestador:
    nome: str
    tipos: str = ""

    @property
    def tipos_legenda(self) -> list[str]:
        out = []
        for t in re.split(r"[,/]", re.sub(r"\[\d+\]", "", self.tipos)):
            t = t.strip().rstrip(".").upper()
            if t and t in LEGENDA_TIPOS:
                out.append(LEGENDA_TIPOS[t])
        return out


@dataclass
class BlocoCidade:
    cidade: str
    regiao: str
    categorias: dict[str, list[Prestador]] = field(default_factory=dict)

    def add(self, categoria: str, prestador: Prestador) -> None:
        self.categorias.setdefault(categoria, []).append(prestador)


@dataclass
class ColunaPlano:
    """Uma coluna de preço = um produto + um tipo de acomodação."""

    plano: str
    acomodacao: str
    valores_por_idade: list[dict[str, str]] = field(default_factory=list)
    total: str | None = None
    per_capita: list[dict[str, str]] = field(default_factory=list)
    tx_iof: str | None = None


@dataclass
class Cotacao:
    arquivo: str = ""
    origem: str = ""  # nome do PDF de onde este bloco veio
    vendedor_nome: str | None = None
    vendedor_email: str | None = None
    vendedor_site: str | None = None
    vendedor_telefone: str | None = None

    titulo: str | None = None
    titulo_tabela: str | None = None
    operadora: str | None = None
    segmento: str | None = None
    referencia: str | None = None
    taxa_inscricao: str | None = None
    uf: str | None = None

    linha_condicoes: str | None = None
    chips: list[str] = field(default_factory=list)
    vidas_total: str | None = None

    colunas: list[ColunaPlano] = field(default_factory=list)
    regioes: dict[str, list[BlocoCidade]] = field(default_factory=dict)
    reembolsos: list[dict[str, Any]] = field(default_factory=list)
    reembolso_colunas: list[str] = field(default_factory=list)
    notas_rede: list[str] = field(default_factory=list)
    legenda: str | None = None
    disclaimer: list[str] = field(default_factory=list)

    # Atributos derivados só quando explicitamente escritos no PDF.
    abrangencia: str | None = None
    coparticipacao: str | None = None
    tem_obstetricia: bool = False
    tem_reembolso: bool = False
    tem_remissao: bool = False
    adesao: str | None = None  # Compulsório / Livre adesão

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# --------------------------------------------------------------------------
# Leitura bruta
# --------------------------------------------------------------------------

def _linhas(doc: fitz.Document) -> list[Linha]:
    out: list[Linha] = []
    for pno, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                bruto = "".join(s["text"] for s in line["spans"])
                txt = _limpa(bruto)
                if not txt:
                    continue
                span = line["spans"][0]
                out.append(
                    Linha(
                        page=pno,
                        x0=line["bbox"][0],
                        y0=line["bbox"][1],
                        x1=line["bbox"][2],
                        text=txt.strip(),
                        color=span["color"],
                        bold="Bold" in span["font"],
                        size=round(span["size"], 1),
                        raw=bruto,
                    )
                )
    return out


def _palavras(page: fitz.Page) -> list[tuple[float, float, float, float, str]]:
    out = []
    for w in page.get_text("words"):
        t = _limpa(w[4])
        if t:
            out.append((w[0], w[1], w[2], w[3], t))
    return out


# --------------------------------------------------------------------------
# Posição no documento e delimitação de blocos
# --------------------------------------------------------------------------

def _pos(l: Linha) -> tuple[int, float]:
    """Ordem de leitura absoluta: página e depois altura."""
    return (l.page, l.y0)


def _marcador(linhas: list[Linha], rotulo: str) -> tuple[int, float] | None:
    """Posição do primeiro rótulo de seção em negrito à esquerda da página."""
    for l in sorted(linhas, key=_pos):
        if l.bold and l.x0 < 40 and l.text.startswith(rotulo):
            return _pos(l)
    return None


# --------------------------------------------------------------------------
# Cabeçalho / vendedor
# --------------------------------------------------------------------------

def _parse_cabecalho(cot: Cotacao, bloco: list[Linha], globais: list[Linha]) -> None:
    """
    Dados do vendedor vêm do topo da página 1 (valem para o documento inteiro).
    Título, referência e condições comerciais são lidos dentro do bloco, porque
    num PDF com várias operadoras cada bloco tem os seus.
    """
    for l in [l for l in globais if l.page == 0]:
        t = l.text.strip()
        if l.y0 < 40 and l.size > 10 and l.x0 > 80:
            cot.vendedor_nome = t
        elif "@" in t and l.y0 < 80:
            cot.vendedor_email = t
        elif t.startswith(("http", "www")) and l.y0 < 80:
            cot.vendedor_site = t
        elif l.y0 < 90 and re.fullmatch(r"[\s\(\)\d\.\-\+]{8,}", t):
            cot.vendedor_telefone = t

    marco = _marcador(bloco, "Valores")
    antes = [l for l in bloco if marco is None or _pos(l) < marco]

    # Título grande e centralizado do bloco (pode quebrar em 2 linhas)
    grandes = [l for l in antes if l.size > 10 and l.x0 > 100]
    if grandes:
        ultima = max(l.page for l in grandes)
        cot.titulo_tabela = " ".join(
            l.text for l in sorted([g for g in grandes if g.page == ultima], key=lambda l: l.y0)
        )

    # Título curto em negrito, à esquerda — é o que traz operadora e UF
    titulos = [
        l for l in antes
        if l.bold and l.x0 < 40 and l.size < 10 and ("|" in l.text or " - " in l.text)
    ]
    cot.titulo = titulos[-1].text if titulos else cot.titulo_tabela

    for l in antes:
        if l.text.startswith("Referência"):
            m = re.search(r"Referência\s*-\s*([^-]+?)\s*-", l.text)
            if m:
                cot.referencia = m.group(1).strip()
            m = re.search(r"Taxa de inscrição:\s*(.+)$", l.text)
            if m:
                cot.taxa_inscricao = m.group(1).strip()
        elif re.match(r"^(SAÚDE|ODONTO|VIDA)", l.text.upper()):
            cot.segmento = l.text

    if cot.titulo:
        cot.operadora = _detecta_operadora(cot.titulo)
        m = re.search(r"-\s*([A-Z]{2})\s*$", cot.titulo)
        if m:
            cot.uf = m.group(1)

    # Condições comerciais e chips ficam entre "Valores" e a tabela de preços
    fim = _marcador(bloco, "Tabela Per Capita") or _marcador(bloco, "Rede")
    janela = [
        l for l in bloco
        if marco is not None and _pos(l) > marco and (fim is None or _pos(l) < fim)
    ]
    for l in janela:
        if l.bold and l.x0 < 40 and "|" in l.text:
            cot.linha_condicoes = l.text
        if l.color == 11184810 and l.x0 < 40:
            cot.chips = [c for c in _chips(l.raw) if c]


OPERADORAS = [
    "Amil", "Bradesco", "SulAmérica", "Sulamerica", "Porto Seguro", "Notredame",
    "NotreDame Intermédica", "Hapvida", "Unimed", "Omint", "Care Plus", "Alice",
    "Ameplan", "Blue Med", "São Cristóvão", "Trasmontano", "Prevent Senior",
    "Seguros Unimed", "Classes Laboriosas", "Santa Helena", "Biovida", "GreenLine",
    "Medsênior", "MedSenior", "Salutar", "Vision Med", "Qsaúde", "QSaúde",
]


def _detecta_operadora(titulo: str) -> str | None:
    alvo = _norm(titulo)
    achados = [o for o in OPERADORAS if _norm(o) in alvo]
    if not achados:
        return titulo.split()[0] if titulo else None
    return max(achados, key=len)


# --------------------------------------------------------------------------
# Tabela de valores
# --------------------------------------------------------------------------

def _linhas_por_y(itens, tol: float = 3.0):
    """Agrupa itens (x0,y0,...,texto) em faixas horizontais."""
    itens = sorted(itens, key=lambda w: (w[1], w[0]))
    linhas: list[list] = []
    for w in itens:
        if linhas and abs(w[1] - linhas[-1][0][1]) <= tol:
            linhas[-1].append(w)
        else:
            linhas.append([w])
    return [sorted(l, key=lambda w: w[0]) for l in linhas]


def _parse_valores(cot: Cotacao, doc: fitz.Document, bloco: list[Linha]) -> None:
    marco = _marcador(bloco, "Valores")
    if marco is None:
        return
    pg, y_valores = marco

    per_capita = _marcador(bloco, "Tabela Per Capita")
    rede = _marcador(bloco, "Rede")
    palavras = _palavras(doc[pg])
    fundo = doc[pg].rect.height

    def limite(marcador: tuple[int, float] | None, padrao: float) -> float:
        """Fim da faixa vertical: o próximo marcador, se estiver na mesma página."""
        if marcador is None or marcador[0] != pg:
            return padrao
        return marcador[1]

    def faixa(y_ini: float, y_fim: float):
        return _linhas_por_y([w for w in palavras if y_ini < w[1] < y_fim])

    cot.colunas = _tabela_precos(faixa(y_valores, limite(per_capita, min(y_valores + 220, fundo))))

    if per_capita is not None and per_capita[0] == pg:
        pc = _tabela_precos(
            faixa(per_capita[1], limite(rede, min(per_capita[1] + 220, fundo)))
        )
        for col in cot.colunas:
            igual = next(
                (c for c in pc if c.plano == col.plano and c.acomodacao == col.acomodacao), None
            )
            if igual:
                col.per_capita = [
                    {"faixa": r["faixa"], "valor": r["valor"]} for r in igual.valores_por_idade
                ]

    if cot.colunas:
        cot.vidas_total = next(
            (
                r.get("vidas")
                for r in cot.colunas[0].valores_por_idade
                if r.get("faixa", "").lower() == "totais"
            ),
            None,
        )


def _tabela_precos(rows: list[list]) -> list[ColunaPlano]:
    """Reconstrói as colunas de preço a partir das linhas geométricas."""
    if not rows:
        return []

    def txt(cel) -> str:
        return " ".join(w[4] for w in cel)

    # cabeçalho de campos: a linha que contém "Idade"
    idx_head = next((i for i, r in enumerate(rows) if any(w[4] == "Idade" for w in r)), None)
    if idx_head is None:
        return []

    head = _agrupa_celulas(rows[idx_head])
    acomod = [c for c in head if txt(c) not in ("Idade", "Vidas")]
    if not acomod:
        return []

    # nome dos planos: linhas acima do cabeçalho
    planos = []
    for r in rows[:idx_head]:
        for cel in _agrupa_celulas(r):
            planos.append(((cel[0][0] + cel[-1][2]) / 2, txt(cel)))

    colunas: list[ColunaPlano] = []
    for cel in acomod:
        centro = (cel[0][0] + cel[-1][2]) / 2
        nome = min(planos, key=lambda p: abs(p[0] - centro))[1] if planos else "Plano"
        colunas.append(ColunaPlano(plano=nome, acomodacao=txt(cel), valores_por_idade=[]))

    tem_vidas = any(txt(c) == "Vidas" for c in head)
    x_vidas = next(((c[0][0] + c[-1][2]) / 2 for c in head if txt(c) == "Vidas"), None)

    for r in rows[idx_head + 1 :]:
        celulas = _agrupa_celulas(r)
        if not celulas:
            continue
        rotulo = txt(celulas[0])
        resto = celulas[1:]

        vidas = None
        if tem_vidas and resto:
            centro = (resto[0][0][0] + resto[0][-1][2]) / 2
            if x_vidas is not None and abs(centro - x_vidas) < 40:
                vidas = txt(resto[0])
                resto = resto[1:]

        for i, cel in enumerate(resto):
            if i >= len(colunas):
                break
            valor = txt(cel)
            col = colunas[i]
            if rotulo.lower().startswith("totais"):
                col.total = valor
                col.valores_por_idade.append({"faixa": "Totais", "vidas": vidas, "valor": valor})
            elif rotulo.lower().startswith("tx/iof"):
                col.tx_iof = valor
            else:
                col.valores_por_idade.append({"faixa": rotulo, "vidas": vidas, "valor": valor})

    return colunas


def _agrupa_celulas(row: list, gap: float = 12.0) -> list[list]:
    """Quebra uma linha de palavras em células onde houver espaço horizontal grande."""
    celulas: list[list] = []
    for w in row:
        if celulas and w[0] - celulas[-1][-1][2] < gap:
            celulas[-1].append(w)
        else:
            celulas.append([w])
    return celulas


# --------------------------------------------------------------------------
# Rede credenciada
# --------------------------------------------------------------------------

def _parse_rede(cot: Cotacao, bloco: list[Linha]) -> None:
    inicio = _marcador(bloco, "Rede")
    if inicio is None:
        return
    linhas = [l for l in bloco if _pos(l) >= inicio]

    regiao_atual: str | None = None
    cidade_atual: BlocoCidade | None = None
    categoria_atual: str | None = None
    pendente: Prestador | None = None
    fim_da_rede = False

    for l in sorted(linhas, key=lambda l: (l.page, l.y0, l.x0)):
        t = l.text
        if t == "Rede":
            continue
        if t.startswith("Legendas:"):
            cot.legenda = t
            fim_da_rede = True
            continue
        if re.match(r"^\[\d+\]\s*-", t):
            cot.notas_rede.append(t)
            continue
        if fim_da_rede:
            continue

        if l.bold and l.color == COLOR_TYPES and l.x0 < 40:
            regiao_atual = t
            cidade_atual = None
            categoria_atual = None
            cot.regioes.setdefault(regiao_atual, [])
        elif l.bold and l.color == COLOR_CITY:
            if regiao_atual is None:
                regiao_atual = "OUTRAS"
                cot.regioes.setdefault(regiao_atual, [])
            cidade_atual = BlocoCidade(cidade=t, regiao=regiao_atual)
            cot.regioes[regiao_atual].append(cidade_atual)
            categoria_atual = None
        elif l.bold and l.color == COLOR_CATEGORY and l.x0 < 40:
            categoria_atual = t
            if cidade_atual is not None:
                cidade_atual.categorias.setdefault(categoria_atual, [])
        elif l.color == COLOR_PROVIDER and l.x0 < 300:
            pendente = Prestador(nome=t)
            if cidade_atual is not None and categoria_atual:
                cidade_atual.add(categoria_atual, pendente)
        elif l.color == COLOR_TYPES and l.x0 > 400 and pendente is not None:
            pendente.tipos = t
            pendente = None


# --------------------------------------------------------------------------
# Reembolso e rodapé
# --------------------------------------------------------------------------

def _parse_reembolso(cot: Cotacao, doc: fitz.Document, linhas: list[Linha]) -> None:
    """A tabela de reembolso do gerador tem o rótulo 'Reembolsos' ACIMA do
    cabeçalho e nenhuma borda inferior — o fim é o bloco de disclaimer."""
    marco = _marcador(linhas, "Reembolsos")
    if marco is None:
        return
    pno = marco[0]
    da_pagina = [l for l in linhas if l.page == pno]

    y_head = next(
        (l.y0 for l in linhas if l.page == pno and l.text.startswith("Descrição do Procedimento")),
        None,
    )
    if y_head is None:
        return
    y_fim = min(
        [l.y0 for l in da_pagina if l.y0 > y_head and l.size < 7 and len(l.text) > 40] or [1e9]
    )

    palavras = _palavras(doc[pno])

    # Cabeçalho das colunas: pode ocupar 2 linhas, acima e ao lado de "Descrição".
    cab = [w for w in palavras if y_head - 18 <= w[1] <= y_head + 9 and w[0] > 200]
    colunas_x: list[list] = []
    for w in sorted(cab, key=lambda w: w[0]):
        if colunas_x and w[0] - max(c[2] for c in colunas_x[-1]) < 30:
            colunas_x[-1].append(w)
        else:
            colunas_x.append([w])
    cot.reembolso_colunas = [
        " ".join(x[4] for x in sorted(c, key=lambda w: (w[1], w[0]))) for c in colunas_x
    ]

    itens: list[dict[str, Any]] = []
    for r in _linhas_por_y([w for w in palavras if y_head + 10 < w[1] < y_fim]):
        celulas = _agrupa_celulas(r, gap=14)
        if len(celulas) < 2:
            continue
        desc = " ".join(w[4] for w in celulas[0])
        vals = [" ".join(w[4] for w in c) for c in celulas[1:]]
        if not any(v.startswith("R$") for v in vals):
            continue
        itens.append({"procedimento": desc, "valores": vals})
    cot.reembolsos = itens


def _parse_disclaimer(alvo: Any, linhas: list[Linha]) -> None:
    ultima = max(l.page for l in linhas)
    candidatas = sorted(
        [l for l in linhas if l.page == ultima and len(l.text) > 55 and l.size <= 8],
        key=lambda l: l.y0,
    )
    inicio = next(
        (i for i, l in enumerate(candidatas) if l.text.startswith("As informações referentes")), None
    )
    alvo.disclaimer = [l.text for l in candidatas[inicio:]] if inicio is not None else []


# --------------------------------------------------------------------------
# Atributos declarados no PDF (nunca inventados)
# --------------------------------------------------------------------------

def _parse_atributos(cot: Cotacao) -> None:
    fonte = " | ".join(
        filter(None, [cot.titulo, cot.linha_condicoes, " ".join(cot.chips)]
               + [c.plano for c in cot.colunas])
    )
    n = _norm(fonte)

    if re.search(r"\bnacional\b", n):
        cot.abrangencia = "Nacional"
    elif re.search(r"\bestadual\b", n):
        cot.abrangencia = "Estadual"
    elif re.search(r"\bregional\b", n):
        cot.abrangencia = "Regional"

    if re.search(r"sem\s+copart|s/\s*copart", n):
        cot.coparticipacao = "Sem coparticipação"
    elif re.search(r"copart[.\s]*parcial|parcial", n):
        cot.coparticipacao = "Coparticipação parcial"
    elif re.search(r"\bcopart|com\s+copart|c/\s*copart|\bcp\b", n):
        cot.coparticipacao = "Com coparticipação"

    cot.tem_obstetricia = "obstetricia" in n
    cot.tem_reembolso = "reembolso" in n or bool(cot.reembolsos)
    cot.tem_remissao = "remissao" in n
    if "compulsorio" in n:
        cot.adesao = "Compulsório"
    elif "livre adesao" in n or "adesao livre" in n:
        cot.adesao = "Livre adesão"


# --------------------------------------------------------------------------
# API pública
# --------------------------------------------------------------------------

@dataclass
class Documento:
    """
    Um PDF de cotação. Normalmente traz um bloco só, mas os "mega PDFs" da
    plataforma empilham várias operadoras/produtos no mesmo arquivo — cada um
    com seu próprio título, tabela de valores, rede e reembolso.
    """

    arquivo: str = ""
    blocos: list[Cotacao] = field(default_factory=list)
    disclaimer: list[str] = field(default_factory=list)

    @property
    def principal(self) -> Cotacao | None:
        return self.blocos[0] if self.blocos else None

    @property
    def operadoras(self) -> list[str]:
        vistas: list[str] = []
        for b in self.blocos:
            if b.operadora and b.operadora not in vistas:
                vistas.append(b.operadora)
        return vistas

    def opcoes(self) -> list[dict[str, Any]]:
        """
        Lista plana de tudo que dá para comparar: cada combinação de bloco +
        coluna de preço é uma opção contratável.
        """
        out: list[dict[str, Any]] = []
        for i, b in enumerate(self.blocos):
            for j, c in enumerate(b.colunas):
                out.append(
                    {
                        "id": f"{i}:{j}",
                        "bloco": i,
                        "origem": b.origem,
                        "coluna": j,
                        "operadora": b.operadora,
                        "plano": c.plano,
                        "acomodacao": c.acomodacao,
                        "total": c.total,
                        "abrangencia": b.abrangencia,
                        "coparticipacao": b.coparticipacao,
                        "obstetricia": b.tem_obstetricia,
                        "reembolso": b.tem_reembolso,
                        "remissao": b.tem_remissao,
                        "adesao": b.adesao,
                        "faixas": len([r for r in c.valores_por_idade if r["faixa"] != "Totais"]),
                        "regioes": list(b.regioes),
                    }
                )
        return out

    def opcao(self, ident: str) -> tuple[Cotacao, ColunaPlano] | None:
        try:
            i, j = (int(x) for x in ident.split(":"))
            return self.blocos[i], self.blocos[i].colunas[j]
        except (ValueError, IndexError):
            return None


def unifica(documentos: list[Documento]) -> Documento:
    """
    Junta vários PDFs numa cotação só.

    Na prática o corretor cota cada operadora separadamente e sai com um PDF por
    operadora; a proposta final precisa dos dois lados. Aqui os blocos de todos
    os arquivos entram numa lista única, mantendo a ordem de envio, e os índices
    de opção ("bloco:coluna") passam a valer para o conjunto.
    """
    juntos = Documento(arquivo=" + ".join(d.arquivo for d in documentos))
    for doc in documentos:
        juntos.blocos.extend(doc.blocos)
        if not juntos.disclaimer:
            juntos.disclaimer = doc.disclaimer
    for bloco in juntos.blocos:
        bloco.disclaimer = juntos.disclaimer
    return juntos


def _fatia_blocos(linhas: list[Linha]) -> list[list[Linha]]:
    """
    Corta o documento nos rótulos "Valores" — há exatamente um por cotação.
    O corte real fica no título que antecede cada "Valores", para que o bloco
    carregue o próprio cabeçalho.
    """
    marcos = [_pos(l) for l in sorted(linhas, key=_pos) if l.bold and l.x0 < 40 and l.text == "Valores"]
    if len(marcos) <= 1:
        return [linhas]

    cortes: list[tuple[int, float]] = [(0, 0.0)]
    for anterior, atual in zip(marcos, marcos[1:]):
        candidatos = [
            _pos(l)
            for l in linhas
            if anterior < _pos(l) < atual and l.size > 10 and l.x0 > 100
        ]
        # O título grande se repete no topo de várias páginas da seção (inclusive
        # na de reembolso). O corte é o ÚLTIMO antes do próximo "Valores" — que é
        # a abertura do bloco seguinte; senão a página de reembolso vaza para ele.
        # Cortamos no topo dessa página para não perder o título curto, que fica
        # acima do grande e é quem traz operadora e UF.
        cortes.append((max(candidatos)[0], 0.0) if candidatos else atual)

    cortes.append((10**6, 0.0))
    return [
        [l for l in linhas if ini <= _pos(l) < fim]
        for ini, fim in zip(cortes, cortes[1:])
    ]


def parse_pdf(caminho: str) -> Documento:
    doc = fitz.open(caminho)
    try:
        linhas = _linhas(doc)
        documento = Documento(arquivo=caminho)
        _parse_disclaimer(documento, linhas)

        nome_origem = Path(caminho).name
        for fatia in _fatia_blocos(linhas):
            cot = Cotacao(arquivo=caminho, origem=nome_origem)
            _parse_cabecalho(cot, fatia, linhas)
            _parse_valores(cot, doc, fatia)
            if not cot.colunas:
                continue
            _parse_rede(cot, fatia)
            _parse_reembolso(cot, doc, fatia)
            _parse_atributos(cot)
            cot.disclaimer = documento.disclaimer
            documento.blocos.append(cot)

        return documento
    finally:
        doc.close()


PRESTIGIO = [
    # Nomes de alto reconhecimento pelo cliente final. Isto só REORDENA a lista
    # extraída do PDF — nenhum prestador é adicionado, removido ou renomeado.
    "einstein", "sirio", "libanes", "oswaldo cruz", "hcor", "samaritano",
    "beneficencia portuguesa", "a. c. camargo", "ac camargo", "sta. catarina",
    "santa catarina", "nove de julho", "9 de julho", "sao luiz", "são luiz",
    "leforte", "sabara", "sabará", "pro matre", "santa joana", "sta. joana",
    "vila nova star", "moriah", "igesp", "santa paula", "sta. paula",
    "alemao", "alemão", "villa lobos", "sao camilo", "são camilo", "notrecare",
    "sta. marcelina", "santa marcelina", "hcfmusp", "das clin", "cruz azul",
    "nipo brasileiro", "bandeirantes", "paulistano", "santa isabel", "sta. isabel",
    "einstein goiania", "premium", "delboni", "fleury", "lavoisier", "salomao zoppi",
    "salomão zoppi", "hermes pardini", "alta excelencia", "cdb", "a+ medicina",
]


def _prestigio(nome: str) -> int:
    """Posição na lista de reconhecimento; menor é mais reconhecido."""
    n = _norm(nome)
    for i, marca in enumerate(PRESTIGIO):
        if marca in n:
            return i
    return len(PRESTIGIO)


def _intercala_por_cidade(itens: list[tuple[str, Any]]) -> list[tuple[str, Any]]:
    """
    Round-robin entre cidades/zonas: evita que a lista resumida fique inteira
    em uma única zona, o que faz o cliente achar que a rede não cobre a dele.
    """
    grupos: dict[str, list] = {}
    for cidade, prest in itens:
        grupos.setdefault(cidade, []).append((cidade, prest))
    saida: list[tuple[str, Any]] = []
    while any(grupos.values()):
        for cidade in list(grupos):
            if grupos[cidade]:
                saida.append(grupos[cidade].pop(0))
            else:
                del grupos[cidade]
    return saida


def cidades_da_regiao(cot: Cotacao, regiao: str) -> list[str]:
    return [b.cidade for b in cot.regioes.get(regiao, [])]


def resumo_rede(
    cot: Cotacao,
    regiao: str,
    limite_hosp: int = 14,
    limite_lab: int = 12,
    cidades: list[str] | None = None,
) -> dict:
    """
    Condensa a rede de uma macro-região para caber em meia página.
    `cidades` restringe o recorte às cidades/zonas que o cliente exigiu.
    """
    blocos = cot.regioes.get(regiao, [])
    if cidades:
        alvo = {_norm(c) for c in cidades}
        blocos = [b for b in blocos if _norm(b.cidade) in alvo] or blocos
    hospitais: list[tuple[str, Prestador]] = []
    labs: list[tuple[str, Prestador]] = []
    propria: list[tuple[str, Prestador]] = []

    for b in blocos:
        for cat, prest in b.categorias.items():
            destino = labs if _norm(cat).startswith("laborat") else (
                propria if "propria" in _norm(cat) else hospitais
            )
            for p in prest:
                destino.append((b.cidade, p))

    def limpa(nome: str) -> str:
        return re.sub(r"\s*\[\d+\]\s*", "", nome).strip()

    def peso(par: tuple[str, Prestador]) -> tuple:
        """Reconhecimento da marca primeiro; depois amplitude de serviços."""
        tipos = par[1].tipos.upper()
        servicos = (
            ("PS" in tipos) * 3 + ("MAT" in tipos) * 2
            + ("HOSP" in tipos) * 2 + ("AMB" in tipos)
        )
        return (_prestigio(par[1].nome), -servicos, par[1].nome)

    hospitais.sort(key=peso)
    labs.sort(key=lambda par: (_prestigio(par[1].nome), par[1].nome))

    return {
        "regiao": regiao,
        "cidades": [b.cidade for b in blocos],
        "total_hospitais": len(hospitais),
        "total_laboratorios": len(labs),
        "total_rede_propria": len(propria),
        "hospitais": [
            {"cidade": c, "nome": limpa(p.nome), "tipos": limpa(p.tipos), "servicos": p.tipos_legenda}
            for c, p in _intercala_por_cidade(hospitais[: limite_hosp * 3])[:limite_hosp]
        ],
        "laboratorios": [
            {"cidade": c, "nome": limpa(p.nome)}
            for c, p in _intercala_por_cidade(labs[: limite_lab * 3])[:limite_lab]
        ],
    }
