"""
Motor de copy persuasiva da Elih.

Arquitetura em duas camadas:

1. **Regras (sempre roda).** Cada bloco de texto é montado a partir de atributos
   que o parser leu literalmente do PDF. Se o atributo não existe, o bloco não
   aparece — é assim que garantimos que a proposta nunca promete cobertura que
   o plano não tem.

2. **IA (opcional).** Se houver OPENAI_API_KEY, o modelo reescreve os textos no
   tom da Elih. Ele recebe uma lista fechada de fatos e é proibido de introduzir
   números novos; a saída passa por `_valida_reescrita`, que rejeita qualquer
   resposta que invente valor monetário, percentual, prazo ou contagem.

   A escolha do modelo é de custo/benefício: a tarefa é reescrever texto curto
   com restrição rígida, não raciocinar. Um modelo "mini" resolve por uma fração
   do preço — e a validação determinística cobre o resto.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from .parser import Cotacao

MODELO = os.getenv("ELIH_MODELO_IA", "gpt-4o-mini")


def chave_ia() -> str | None:
    return os.getenv("OPENAI_API_KEY") or None


def ia_ativa() -> bool:
    """
    A camada de IA está DESLIGADA por padrão.

    Foi desativada quando a conta da OpenAI ficou sem crédito. Deixar ligada
    nesse estado é pior que desligar: cada geração tentava a API, esperava o
    429 e só então caía na copy de regras — segundos a mais por proposta para
    chegar exatamente no mesmo texto.

    A copy de regras é a versão revisada por humano e cobre tudo sozinha; o
    refino por IA sempre foi um acabamento opcional.

    Para religar: ter crédito na conta e definir ELIH_IA=1 no ambiente.
    """
    if os.getenv("ELIH_IA", "0").strip().lower() not in ("1", "true", "sim", "on"):
        return False
    return bool(chave_ia())


# --------------------------------------------------------------------------
# Camada 1 — regras
# --------------------------------------------------------------------------

def badges(cot: Cotacao) -> list[dict[str, str]]:
    """Selos do topo da página do plano. Só entram atributos confirmados."""
    out: list[dict[str, str]] = []
    if cot.abrangencia:
        out.append({"label": cot.abrangencia, "tipo": "abrangencia"})
    if cot.coparticipacao:
        tipo = "positivo" if cot.coparticipacao.startswith("Sem") else "neutro"
        out.append({"label": cot.coparticipacao, "tipo": tipo})
    if cot.tem_obstetricia:
        out.append({"label": "Com obstetrícia", "tipo": "positivo"})
    if cot.tem_reembolso:
        out.append({"label": "Com reembolso", "tipo": "positivo"})
    if cot.tem_remissao:
        out.append({"label": "Com remissão", "tipo": "positivo"})
    if cot.adesao:
        out.append({"label": cot.adesao, "tipo": "neutro"})
    return out


ABRANGENCIA_TEXTO = {
    "Nacional": "Atendimento na rede credenciada da operadora em todo o território nacional.",
    "Estadual": "Atendimento na rede credenciada da operadora em todo o estado.",
    "Regional": "Atendimento na rede credenciada da operadora dentro da região contratada.",
}


def resumo_plano(cot: Cotacao, rede: dict, coluna_idx: int = 0, limite: int = 7) -> list[str]:
    """
    Frases curtas que resumem o que o cliente está contratando, na ordem em que
    mais pesam na decisão. `limite` corta o rabo quando a página aperta.
    """
    linhas: list[str] = []
    col = cot.colunas[coluna_idx] if cot.colunas else None

    if col:
        acomod = "quarto privativo" if "apto" in col.acomodacao.lower() else col.acomodacao.lower()
        linhas.append(f"Produto {col.plano}, com acomodação em {acomod}.")

    if cot.abrangencia:
        linhas.append(ABRANGENCIA_TEXTO[cot.abrangencia])

    if rede["total_hospitais"] or rede["total_laboratorios"]:
        linhas.append(
            f"Na região de {rede['regiao'].title()}: "
            f"{rede['total_hospitais']} hospitais e {rede['total_laboratorios']} "
            f"laboratórios e centros de diagnóstico credenciados."
        )

    if cot.coparticipacao == "Sem coparticipação":
        linhas.append("Sem coparticipação: o valor mensal é o que você paga, use quanto usar.")
    elif cot.coparticipacao == "Coparticipação parcial":
        linhas.append(
            "Coparticipação parcial: mensalidade mais baixa, com participação apenas "
            "nos procedimentos previstos em contrato."
        )
    elif cot.coparticipacao == "Com coparticipação":
        linhas.append(
            "Com coparticipação: mensalidade mais baixa, com participação nos "
            "procedimentos previstos em contrato."
        )

    if cot.tem_obstetricia:
        linhas.append("Segmentação com obstetrícia — cobertura de parto incluída.")
    if cot.tem_reembolso:
        linhas.append("Livre escolha com reembolso conforme a tabela da operadora.")
    if cot.tem_remissao:
        linhas.append(
            "Com cláusula de remissão: em caso de falecimento do titular, os "
            "dependentes seguem cobertos pelo prazo previsto em contrato."
        )
    return linhas[:limite]


# Compromissos de serviço da própria Elih — são promessas do corretor, não do
# plano, e por isso não passam pela regra de "só o que está no PDF". Edite aqui
# para mudar o texto em todas as propostas.
DIFERENCIAIS_ELIH = [
    {
        "titulo": "Você fala direto comigo",
        "texto": "Sem 0800 e sem robô. Da dúvida à contratação e depois dela, é a mesma pessoa.",
    },
    {
        "titulo": "Recomendação com critério",
        "texto": "Comparo as operadoras e mostro o porquê da escolha — não só o preço mais baixo.",
    },
    {
        "titulo": "Acompanho até a carteirinha",
        "texto": "Protocolo, análise, emissão e renovação. Você não fica sozinho com a operadora.",
    },
]


def _valor_total(cot: Cotacao, idx: int = 0) -> str | None:
    return cot.colunas[idx].total if cot.colunas and idx < len(cot.colunas) else None


PRIORIDADE = [
    "preco", "carencia", "rede", "reembolso", "abrangencia",
    "coparticipacao", "vigencia", "adesao",
]


def objecoes(
    cot: Cotacao, rede: dict, ctx: dict[str, Any], coluna_idx: int = 0, limite: int = 4
) -> list[dict[str, str]]:
    """
    Quebras de objeção montadas por atributo. Cada resposta usa apenas dados
    que estão no PDF ou informação de processo que o próprio corretor controla
    (documentação, carta de permanência). Nada de promessa de cobertura.
    """
    col = cot.colunas[coluna_idx] if cot.colunas else None
    out: list[dict[str, str]] = []

    # 1. Preço — sempre a primeira objeção real
    if col and col.per_capita:
        menor = min(col.per_capita, key=lambda r: _num(r["valor"]))
        out.append(
            {
                "chave": "preco",
                "objecao": "“Achei o valor alto.”",
                "resposta": (
                    f"O valor não é um número único: cada vida entra na sua faixa etária. "
                    f"Nesta cotação a menor faixa fica em {menor['valor']} por mês"
                    + (f", e o total do grupo é {col.total}." if col.total else ".")
                    + " Uma única internação particular costuma custar mais do que um ano "
                    "inteiro de mensalidade."
                ),
            }
        )

    # 2. Rede — só cita nomes que estão no PDF
    if rede["hospitais"]:
        nomes = ", ".join(h["nome"] for h in rede["hospitais"][:3])
        out.append(
            {
                "chave": "rede",
                "objecao": "“Não conheço a rede desse plano.”",
                "resposta": (
                    f"Em {rede['regiao'].title()} a rede credenciada inclui "
                    f"{rede['total_hospitais']} hospitais — entre eles {nomes} — e "
                    f"{rede['total_laboratorios']} laboratórios. A lista por cidade "
                    "está na página de rede credenciada desta proposta."
                ),
            }
        )

    # 3. Carência — depende da situação do cliente
    if ctx.get("possui_plano"):
        out.append(
            {
                "chave": "carencia",
                "objecao": "“Vou ter que cumprir carência tudo de novo.”",
                "resposta": (
                    "Não. Como você já tem plano ativo, entramos com o aproveitamento de "
                    "carência: com a carta de permanência e as carteirinhas do plano atual, "
                    "o tempo já cumprido é considerado na migração. Eu cuido desse processo "
                    "junto à operadora."
                ),
            }
        )
    else:
        out.append(
            {
                "chave": "carencia",
                "objecao": "“E se eu precisar usar logo depois de contratar?”",
                "resposta": (
                    "Urgência e emergência têm prazo de carência reduzido, e consultas e "
                    "exames simples liberam bem antes dos procedimentos de maior porte. "
                    "Eu te passo a tabela de carências da operadora antes de você assinar — "
                    "sem surpresa."
                ),
            }
        )

    # 4. Reembolso — só se o produto tiver, com os valores reais do PDF
    if cot.tem_reembolso and cot.reembolsos:
        exemplo = cot.reembolsos[0]
        out.append(
            {
                "chave": "reembolso",
                "objecao": "“Quero continuar com meu médico particular.”",
                "resposta": (
                    "Este produto tem livre escolha com reembolso. Você paga o profissional "
                    "de sua confiança e a operadora devolve conforme a tabela — por exemplo, "
                    f"{_curto(exemplo['procedimento'])}: até {exemplo['valores'][0]}. "
                    "A tabela completa está na proposta."
                ),
            }
        )

    # 5. Abrangência
    if cot.abrangencia == "Nacional":
        out.append(
            {
                "chave": "abrangencia",
                "objecao": "“E se eu viajar ou precisar de atendimento em outro estado?”",
                "resposta": (
                    "A abrangência deste produto é nacional: a rede credenciada da operadora "
                    "atende em todo o território nacional, não só em São Paulo."
                ),
            }
        )
    elif cot.abrangencia in ("Regional", "Estadual"):
        out.append(
            {
                "chave": "abrangencia",
                "objecao": "“E se eu precisar de atendimento fora da região?”",
                "resposta": (
                    f"A abrangência contratada é {cot.abrangencia.lower()} — é justamente o que "
                    "segura o preço nesse patamar. Se atendimento fora da área for uma "
                    "necessidade real sua, eu coto a versão nacional do mesmo produto para "
                    "você comparar lado a lado."
                ),
            }
        )

    # 6. Coparticipação
    if cot.coparticipacao == "Sem coparticipação":
        out.append(
            {
                "chave": "coparticipacao",
                "objecao": "“Vou pagar a mais toda vez que usar?”",
                "resposta": (
                    "Não neste produto. Ele é sem coparticipação: a mensalidade é o valor "
                    "fechado, independentemente de quantas consultas ou exames você fizer."
                ),
            }
        )
    elif cot.coparticipacao in ("Com coparticipação", "Coparticipação parcial"):
        out.append(
            {
                "chave": "coparticipacao",
                "objecao": "“Coparticipação não vai encarecer na prática?”",
                "resposta": (
                    "A coparticipação é o que reduz a mensalidade fixa. Para quem usa o plano "
                    "de forma pontual, o custo anual costuma ficar abaixo do plano sem "
                    "coparticipação. Eu faço essa conta com o seu perfil de uso antes de você "
                    "decidir."
                ),
            }
        )

    # 7. Adesão compulsória
    if cot.adesao == "Compulsório":
        out.append(
            {
                "chave": "adesao",
                "objecao": "“Preciso colocar todo mundo da empresa?”",
                "resposta": (
                    "Este produto é de adesão compulsória: o grupo elegível entra junto — e é "
                    "exatamente isso que garante o preço de tabela empresarial, bem abaixo do "
                    "individual. Eu monto o grupo com você."
                ),
            }
        )

    # 8. Vigência da tabela
    vigencia = next((c for c in cot.chips if c.lower().startswith("até")), None)
    if vigencia:
        out.append(
            {
                "chave": "vigencia",
                "objecao": "“Vou pensar e te retorno mês que vem.”",
                "resposta": (
                    f"Sem problema — só um alerta honesto: esta tabela é válida {vigencia.lower()}. "
                    "Depois dessa data a operadora republica os valores e a cotação precisa ser "
                    "refeita. Se fizer sentido, garantimos as condições de hoje."
                ),
            }
        )

    out.sort(key=lambda o: PRIORIDADE.index(o["chave"]) if o["chave"] in PRIORIDADE else 99)
    return out[:limite]


def proximos_passos(ctx: dict[str, Any]) -> dict[str, Any]:
    """Checklist de documentos — muda conforme o cliente já tem plano ou não."""
    base = [
        "RG ou CNH de todos os beneficiários",
        "Comprovante de endereço do titular",
        "E-mail do titular",
        "Peso e altura de todos os beneficiários",
    ]

    doc_cnpj = ctx.get("tipo_cnpj")
    if doc_cnpj == "mei":
        base.append("Certificado do MEI (CCMEI)")
    elif doc_cnpj == "ltda":
        base.append("Contrato social (empresa limitada)")

    passos = [
        {
            "titulo": "Você confirma o plano escolhido",
            "texto": "Me responda por WhatsApp qual das opções faz mais sentido. "
                     "Qualquer dúvida antes disso, é só chamar.",
        },
        {
            "titulo": "Você me envia os documentos",
            "texto": "Pode mandar tudo por WhatsApp, em foto mesmo. "
                     "A lista completa está aqui do lado.",
        },
        {
            "titulo": "Eu monto e protocolo a proposta",
            "texto": "Preencho os formulários da operadora, revisão inclusa, e te envio "
                     "para assinatura digital.",
        },
        {
            "titulo": "Operadora analisa e emite as carteirinhas",
            "texto": "Acompanho o protocolo do começo ao fim e te aviso a cada etapa "
                     "até a vigência começar.",
        },
    ]

    if ctx.get("possui_plano"):
        base += [
            "Carteirinhas do plano atual (físicas ou digitais)",
            "Carta de permanência do plano atual",
        ]
        passos.insert(
            2,
            {
                "titulo": "Eu solicito o aproveitamento de carência",
                "texto": "Com a carta de permanência e as carteirinhas, formalizo junto à "
                         "operadora o aproveitamento do tempo que você já cumpriu.",
            },
        )

    return {
        "documentos": base,
        "passos": passos,
        "aproveitamento_carencia": bool(ctx.get("possui_plano")),
    }


def _num(valor: str) -> float:
    v = re.sub(r"[^\d,]", "", valor).replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return float("inf")


def _curto(texto: str, limite: int = 46) -> str:
    texto = re.split(r"\s+-\s+", texto)[0]
    return texto if len(texto) <= limite else texto[: limite - 1].rstrip() + "…"


# --------------------------------------------------------------------------
# Camada 2 — refinamento por IA (opcional)
# --------------------------------------------------------------------------

PROMPT = """Você é redator sênior da Elih Seguros, corretora de planos de saúde em São Paulo.
Escreve para o cliente final: dono de pequena empresa, RH, profissional autônomo.

SUA TAREFA
Reescrever os textos recebidos para ficarem mais persuasivos e mais fáceis de ler,
mantendo 100% dos fatos. Reescreva TODOS os itens — devolver um texto igual ao que
recebeu é considerado falha. Mude a construção das frases, a ordem das ideias e as
palavras; mantenha apenas os fatos e os números.

COMO REESCREVER
- Abra pelo que interessa ao cliente, não pelo jargão do plano.
- Frases curtas e voz ativa. Corte advérbio e rodeio.
- Concreto vence adjetivo: nada de "excelente cobertura" ou "as melhores condições".
- Resumo: no máximo 1 frase por item. Objeções: no máximo 3 frases por resposta.
- Fale "você". Sem emoji, sem exclamação, sem "!!!", sem CAPS.
- Não venda com medo. Não prometa nada que o texto original não afirme.

TOM DA MARCA
Consultivo e direto — um consultor de confiança explicando, nunca um vendedor
empurrando nem um banco falando difícil.
Exemplos do tom certo: "Sem 0800 e sem robôs. Você fala direto com quem resolve."
/ "Mais do que um plano. Uma orientação certa para sua escolha."

REGRAS INVIOLÁVEIS
1. Proibido acrescentar informação que não esteja no texto recebido.
2. Proibido número novo. Todo valor em R$, percentual, prazo, data ou contagem na
   sua resposta precisa aparecer idêntico no texto original. Não arredonde, não
   converta, não some, não calcule "por dia" ou "por ano".
3. Não prometa cobertura, carência, rede ou reembolso que não esteja escrito.
4. Não invente nome de hospital, laboratório, operadora ou produto.
5. Mesma quantidade de itens, mesma ordem, mesma estrutura JSON.

Devolva SOMENTE um objeto JSON com exatamente as mesmas chaves e o mesmo número
de itens que recebeu: {"resumo": [...], "objecoes": [{"chave", "objecao", "resposta"}]}.
Preserve o campo "chave" de cada objeção sem alterar."""


def _taxa_reescrita(original: dict, novo: dict) -> float:
    """Fração de itens que o modelo realmente reescreveu."""
    antes = original["resumo"] + [o["resposta"] for o in original["objecoes"]]
    depois = novo["resumo"] + [o["resposta"] for o in novo["objecoes"]]
    if not antes:
        return 0.0
    return sum(1 for a, b in zip(antes, depois) if a.strip() != b.strip()) / len(antes)


def refina_com_ia(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    Reescreve resumo e objeções no tom da marca. Devolve (payload, status).
    Qualquer falha — sem chave, erro de rede, resposta inválida — mantém a copy
    das regras e reporta o motivo, sem quebrar a geração.
    """
    if not ia_ativa():
        return payload, "regras curadas (IA desligada)"
    chave = chave_ia()

    entrada = {"resumo": payload["resumo"], "objecoes": payload["objecoes"]}
    try:
        from openai import OpenAI

        cliente = OpenAI(api_key=chave, timeout=45.0, max_retries=2)
        resp = cliente.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(entrada, ensure_ascii=False, indent=2),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        dados = json.loads(resp.choices[0].message.content or "{}")
    except Exception as exc:  # noqa: BLE001 — degradar é melhor que falhar
        return payload, f"regras (IA indisponível: {type(exc).__name__})"

    if not _valida_reescrita(entrada, dados):
        return payload, f"regras ({MODELO} reprovado na validação)"

    taxa = _taxa_reescrita(entrada, dados)
    if taxa < 0.34:
        # O modelo devolveu quase tudo igual: não vale trocar a copy de regras,
        # que é a versão revisada por humano, por uma cópia dela.
        return payload, f"regras ({MODELO} devolveu o texto praticamente igual)"

    payload["resumo"] = dados["resumo"]
    payload["objecoes"] = dados["objecoes"]
    return payload, f"IA {MODELO} + validação ({taxa:.0%} reescrito)"


NUMERO = re.compile(r"R\$\s?[\d.,]+|\d+(?:[.,]\d+)?\s?%|\b\d[\d./]*\b")


def _numeros(texto: str) -> set[str]:
    """
    Números do texto, normalizados para comparação.

    A pontuação da frase gruda no número ("R$109,76." no fim de um período), e o
    espaço depois do R$ varia. Sem normalizar isso, uma reescrita legítima que só
    mexe na pontuação seria acusada de inventar valor.
    """
    achados = set()
    for bruto in NUMERO.findall(texto):
        limpo = bruto.replace(" ", "").rstrip(".,;:!?")
        if limpo and limpo not in ("R$",):
            achados.add(limpo)
    return achados


def _valida_reescrita(original: dict, novo: dict) -> bool:
    """Rejeita a saída da IA se ela criou número, ou mudou a estrutura."""
    if set(novo) != set(original):
        return False
    if len(novo.get("resumo", [])) != len(original["resumo"]):
        return False
    if len(novo.get("objecoes", [])) != len(original["objecoes"]):
        return False
    if any(not isinstance(o, dict) or "resposta" not in o for o in novo["objecoes"]):
        return False

    permitidos = _numeros(json.dumps(original, ensure_ascii=False))
    usados = _numeros(json.dumps(novo, ensure_ascii=False))
    return usados.issubset(permitidos)


def monta_copy(cot: Cotacao, rede: dict, ctx: dict[str, Any], coluna_idx: int = 0) -> dict[str, Any]:
    payload = {
        "badges": badges(cot),
        "resumo": resumo_plano(cot, rede, coluna_idx, int(ctx.get("max_resumo", 7))),
        "objecoes": objecoes(cot, rede, ctx, coluna_idx, int(ctx.get("max_objecoes", 4))),
        "proximos_passos": proximos_passos(ctx),
        "diferenciais": DIFERENCIAIS_ELIH,
    }
    if ctx.get("usar_ia") and ia_ativa():
        payload, status = refina_com_ia(payload)
    else:
        status = "regras curadas"
    payload["motor"] = status
    return payload


# --------------------------------------------------------------------------
# Comparativo entre operadoras / produtos
# --------------------------------------------------------------------------

def _num_puro(valor: str | None) -> float:
    if not valor:
        return float("inf")
    return _num(valor)


def monta_comparativo(itens: list[dict[str, Any]], recomendado: int = 0) -> dict[str, Any]:
    """
    Monta a tabela lado a lado a partir das opções escolhidas.

    `itens` traz, por opção: cot (Cotacao), coluna (ColunaPlano) e rede (dict).
    Nada aqui recalcula preço — os valores saem literalmente de cada bloco do
    PDF. Faixas etárias que existem num plano e não no outro aparecem como "—".
    """
    if not itens:
        return {}

    # União das faixas, começando pelas do plano recomendado para manter a ordem
    # de leitura que o cliente já viu na cotação original.
    faixas: list[str] = []
    for i in [recomendado] + [n for n in range(len(itens)) if n != recomendado]:
        for r in itens[i]["coluna"].valores_por_idade:
            if r["faixa"] != "Totais" and r["faixa"] not in faixas:
                faixas.append(r["faixa"])

    def valor_da_faixa(item: dict[str, Any], faixa: str) -> str:
        for r in item["coluna"].valores_por_idade:
            if r["faixa"] == faixa:
                return r["valor"]
        return "—"

    def vidas(item: dict[str, Any]) -> str | None:
        for r in item["coluna"].valores_por_idade:
            if r["faixa"] == "Totais":
                return r.get("vidas")
        return None

    colunas = []
    for i, it in enumerate(itens):
        cot, col, rede = it["cot"], it["coluna"], it["rede"]
        colunas.append(
            {
                "recomendado": i == recomendado,
                "vidas": vidas(it),
                "operadora": cot.operadora,
                "logo": it.get("logo"),
                "plano": col.plano,
                "acomodacao": col.acomodacao,
                "total": col.total,
                "faixas": {f: valor_da_faixa(it, f) for f in faixas},
                "atributos": {
                    "Abrangência": cot.abrangencia or "Não informada",
                    "Coparticipação": cot.coparticipacao or "Não informada",
                    "Obstetrícia": "Sim" if cot.tem_obstetricia else "Não",
                    "Reembolso": "Sim" if cot.tem_reembolso else "Não",
                    "Remissão": "Sim" if cot.tem_remissao else "Não",
                    "Adesão": cot.adesao or "—",
                },
                "hospitais": rede["total_hospitais"],
                "laboratorios": rede["total_laboratorios"],
            }
        )

    baratos = sorted(range(len(colunas)), key=lambda i: _num_puro(colunas[i]["total"]))
    for pos, i in enumerate(baratos):
        colunas[i]["mais_barato"] = pos == 0

    aplica_destaques(colunas)

    return {
        "faixas": faixas,
        "atributos": list(colunas[0]["atributos"]),
        "colunas": colunas,
        "recomendado": colunas[recomendado],
        "leitura": _leitura_comparativo(colunas, recomendado),
    }


def _leitura_comparativo(colunas: list[dict[str, Any]], recomendado: int) -> list[str]:
    """
    Frases que ajudam o cliente a ler a tabela. Só comparam o que está escrito;
    quando o plano recomendado não é o mais barato, a diferença é assumida em
    vez de escondida — é isso que sustenta a recomendação.
    """
    rec = colunas[recomendado]
    fora = [c for i, c in enumerate(colunas) if i != recomendado]
    linhas: list[str] = []

    # Cotações feitas para grupos de tamanhos diferentes não podem ser comparadas
    # pelo total: uma proposta que anuncia "menor mensalidade" comparando 1 vida
    # com 3 induz o cliente ao erro. Avisar é obrigatório, não opcional.
    contagens = {c.get("vidas") for c in colunas if c.get("vidas")}
    if len(contagens) > 1:
        detalhe = ", ".join(
            f"{c['plano']} ({c['vidas']} {'vida' if c['vidas'] == '1' else 'vidas'})"
            for c in colunas
            if c.get("vidas")
        )
        linhas.append(
            "Atenção: as cotações não cobrem o mesmo número de vidas — "
            f"{detalhe}. Os totais mensais não são comparáveis diretamente."
        )

    def nomes(itens: list[dict[str, Any]]) -> str:
        """Nomes sem repetir — dois PDFs podem trazer o mesmo produto."""
        vistos: list[str] = []
        for c in itens:
            if c["plano"] not in vistos:
                vistos.append(c["plano"])
        return ", ".join(vistos)

    if rec.get("mais_barato") and fora:
        linhas.append(
            f"{rec['plano']} é o de menor mensalidade entre as opções cotadas, "
            f"com {rec['total']} para o grupo."
        )
    else:
        barato = next((c for c in colunas if c.get("mais_barato")), None)
        if barato and barato is not rec and rec["total"] and barato["total"]:
            linhas.append(
                f"{barato['plano']} tem a mensalidade mais baixa ({barato['total']}), "
                f"mas a recomendação é {rec['plano']} ({rec['total']}) pelos motivos abaixo."
            )

    melhor_rede = max(colunas, key=lambda c: c["hospitais"])
    if melhor_rede["hospitais"] and len({c["hospitais"] for c in colunas}) > 1:
        linhas.append(
            f"Na região escolhida, {melhor_rede['plano']} tem a rede mais ampla: "
            f"{melhor_rede['hospitais']} hospitais contra "
            f"{min(c['hospitais'] for c in colunas)} da opção com menos cobertura."
        )

    nacionais = [c for c in colunas if c["atributos"]["Abrangência"] == "Nacional"]
    if nacionais and len(nacionais) < len(colunas):
        linhas.append(
            "Abrangência nacional só em: " + nomes(nacionais) + "."
        )

    com_reembolso = [c for c in colunas if c["atributos"]["Reembolso"] == "Sim"]
    if com_reembolso and len(com_reembolso) < len(colunas):
        linhas.append(
            "Livre escolha com reembolso só em: " + nomes(com_reembolso) + "."
        )

    return linhas


# --------------------------------------------------------------------------
# Destaque individual de cada opção
# --------------------------------------------------------------------------

def _media_per_capita(coluna: dict[str, Any]) -> float:
    valores = [_num(v) for v in coluna["faixas"].values() if v and v != "—"]
    return sum(valores) / len(valores) if valores else float("inf")


# Cada critério é (rótulo, explicação curta, função que devolve o índice vencedor
# ou None quando o critério não separa ninguém). A ordem é a prioridade: um plano
# recebe o critério mais forte que ainda estiver livre.
def _criterios(colunas: list[dict[str, Any]]) -> list[tuple[str, str, int | None]]:
    n = len(colunas)

    def unico_com(chave: str, valor: str) -> int | None:
        """Índice do único plano com esse atributo — None se todos ou nenhum têm."""
        quem = [i for i, c in enumerate(colunas) if c["atributos"].get(chave) == valor]
        return quem[0] if len(quem) == 1 and n > 1 else None

    def menor(func) -> int | None:
        vals = [func(c) for c in colunas]
        if len(set(vals)) < 2:
            return None
        return vals.index(min(vals))

    def maior(func) -> int | None:
        vals = [func(c) for c in colunas]
        if len(set(vals)) < 2:
            return None
        return vals.index(max(vals))

    return [
        ("Menor mensalidade", "o total mensal mais baixo entre as opções",
         menor(lambda c: _num_puro(c["total"]))),
        ("Maior rede hospitalar", "mais hospitais credenciados na região escolhida",
         maior(lambda c: c["hospitais"])),
        ("Abrangência nacional", "atendimento na rede da operadora em todo o país",
         unico_com("Abrangência", "Nacional")),
        ("Sem coparticipação", "mensalidade fechada, sem pagar por uso",
         unico_com("Coparticipação", "Sem coparticipação")),
        ("Com reembolso", "livre escolha de médico com reembolso em tabela",
         unico_com("Reembolso", "Sim")),
        ("Com remissão", "dependentes seguem cobertos em caso de falecimento do titular",
         unico_com("Remissão", "Sim")),
        ("Com obstetrícia", "cobertura de parto incluída",
         unico_com("Obstetrícia", "Sim")),
        ("Mais laboratórios", "mais unidades de diagnóstico na região",
         maior(lambda c: c["laboratorios"])),
        ("Menor custo por vida", "a média por faixa etária mais baixa",
         menor(_media_per_capita)),
    ]


def aplica_destaques(colunas: list[dict[str, Any]]) -> None:
    """
    Dá a cada opção o seu ponto forte, para o cliente ver o que cada uma entrega
    em vez de só olhar o preço.

    Nenhum critério é opinião: todos saem de um número ou de um atributo que já
    está na tabela. Quando duas opções empatam num critério, ele não é usado —
    dizer "maior rede" para as duas não ajuda ninguém a decidir.
    """
    livres = set(range(len(colunas)))
    for rotulo, explicacao, vencedor in _criterios(colunas):
        if vencedor is not None and vencedor in livres:
            colunas[vencedor]["destaque"] = rotulo
            colunas[vencedor]["destaque_desc"] = explicacao
            livres.discard(vencedor)

    # Sem nada que o separe dos outros, o plano fica com o próprio perfil.
    for i in livres:
        c = colunas[i]
        colunas[i]["destaque"] = f"Acomodação em {c['acomodacao'].lower().rstrip('.')}"
        colunas[i]["destaque_desc"] = "mesma estrutura das demais opções, sem diferencial isolado"
