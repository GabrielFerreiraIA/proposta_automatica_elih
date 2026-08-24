"""
Confere as logos das operadoras antes de entrarem na proposta.

    python scripts/checar_logos.py

Verifica cada arquivo em Logos_Operadoras/ e assets/logos_operadoras/ e aponta
o que quebraria no PDF. O problema mais grave é silencioso: um SVG que referencia
a fonte da marca em vez de trazer o texto em curvas renderiza com uma fonte
qualquer do sistema — sai errado sem gerar erro nenhum.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.parser import OPERADORAS, _norm  # noqa: E402
from app.renderer import PASTAS_LOGOS, _imagens, encontra_logo_operadora  # noqa: E402

# Slot da logo na página do plano (ver .operadora-logo em proposta.css).
SLOT_MM = (40, 14)
PROPORCAO_IDEAL = SLOT_MM[0] / SLOT_MM[1]
PESO_MAX_KB = 300

# Sem cores ANSI: o terminal padrão do Windows nem sempre as interpreta e o
# relatório fica poluído de códigos de escape.


def _dimensoes(arq: Path) -> tuple[float, float] | None:
    if arq.suffix.lower() == ".svg":
        try:
            raiz = ElementTree.parse(arq).getroot()
        except ElementTree.ParseError:
            return None
        vb = raiz.get("viewBox")
        if vb:
            partes = re.split(r"[\s,]+", vb.strip())
            if len(partes) == 4:
                return float(partes[2]), float(partes[3])
        larg, alt = raiz.get("width"), raiz.get("height")
        if larg and alt:
            try:
                return float(re.sub(r"[^\d.]", "", larg)), float(re.sub(r"[^\d.]", "", alt))
            except ValueError:
                return None
        return None

    from PIL import Image

    with Image.open(arq) as im:
        return float(im.size[0]), float(im.size[1])


def _problemas(arq: Path) -> list[tuple[str, str]]:
    """Devolve [(gravidade, mensagem)] — 'erro' quebra, 'aviso' só piora."""
    achados: list[tuple[str, str]] = []
    kb = arq.stat().st_size / 1024

    if arq.suffix.lower() == ".svg":
        bruto = arq.read_text(encoding="utf-8", errors="ignore")

        if re.search(r"<text[\s>]", bruto):
            achados.append((
                "erro",
                "tem <text>: a fonte da marca não existe no servidor e o Chromium "
                "troca por uma fonte qualquer. Converta o texto em curvas.",
            ))
        if re.search(r'href\s*=\s*["\']https?://', bruto):
            achados.append((
                "erro",
                "referencia arquivo externo (http): a geração do PDF roda offline "
                "e isso não vai carregar.",
            ))
        if "viewBox" not in bruto:
            achados.append((
                "aviso",
                "sem viewBox: pode não escalar direito no slot. Reexporte com viewBox.",
            ))
        if re.search(r'data:image/(png|jpe?g)', bruto):
            achados.append((
                "aviso",
                "tem imagem rasterizada embutida — perde a vantagem do vetor e pesa mais.",
            ))
    elif arq.suffix.lower() in {".jpg", ".jpeg"}:
        achados.append((
            "aviso",
            "JPG não tem transparência: vira um retângulo branco sobre a coluna navy "
            "do comparativo. Prefira PNG ou SVG.",
        ))
    else:
        from PIL import Image

        with Image.open(arq) as im:
            transparente = im.mode in ("RGBA", "LA") or "transparency" in im.info
        if not transparente:
            achados.append((
                "aviso",
                "sem canal alfa: fundo chapado aparece sobre a coluna navy do comparativo.",
            ))

    if kb > PESO_MAX_KB:
        achados.append((
            "aviso",
            f"{kb:.0f} KB — acima de {PESO_MAX_KB} KB. Cada logo vira base64 dentro do PDF.",
        ))

    dim = _dimensoes(arq)
    if dim is None:
        achados.append(("erro", "não consegui ler as dimensões do arquivo."))
    else:
        larg, alt = dim
        prop = larg / alt if alt else 0
        if arq.suffix.lower() != ".svg" and alt < 165:
            achados.append((
                "aviso",
                f"altura de {alt:.0f}px: abaixo dos 165px que o slot precisa a 300dpi. "
                "Reexporte com 400-600px de altura.",
            ))
        if prop and prop < 1.6:
            ocupa = prop / PROPORCAO_IDEAL * 100
            achados.append((
                "aviso",
                f"proporção {prop:.2f}:1 é quadrada demais para o slot ({PROPORCAO_IDEAL:.2f}:1) — "
                f"ocupa só {ocupa:.0f}% da largura e fica menor que as outras. "
                "Use a versão horizontal da marca.",
            ))

    if not any(_norm(o).replace("-", "") in _norm(arq.stem).replace("-", "") for o in OPERADORAS):
        achados.append((
            "aviso",
            "o nome do arquivo não contém nenhuma operadora conhecida — a logo pode "
            "nunca ser encontrada. Veja a lista no fim do relatório.",
        ))

    return achados


def main() -> int:
    arquivos = _imagens(PASTAS_LOGOS, {".svg"})
    if not arquivos:
        print("Nenhuma logo encontrada em:")
        for pasta in PASTAS_LOGOS:
            print(f"  {pasta}")
        return 1

    erros = avisos = 0
    print(f"\n{len(arquivos)} logo(s) encontrada(s)\n")

    for arq in arquivos:
        achados = _problemas(arq)
        graves = [m for g, m in achados if g == "erro"]
        leves = [m for g, m in achados if g == "aviso"]
        erros += len(graves)
        avisos += len(leves)

        dim = _dimensoes(arq)
        medida = f"{dim[0]:.0f}x{dim[1]:.0f} ({dim[0] / dim[1]:.2f}:1)" if dim else "?"
        icone = "[X]" if graves else ("[!]" if leves else "[ok]")
        print(f" {icone:4} {arq.name}  {medida}")
        for m in graves:
            print(f"      ERRO  {m}")
        for m in leves:
            print(f"      aviso {m}")

    # OPERADORAS traz variantes de grafia da mesma marca ("SulAmérica" e
    # "Sulamerica"); no relatório interessa a operadora, não a grafia.
    unicas: dict[str, str] = {}
    for op in OPERADORAS:
        unicas.setdefault(_norm(op).replace(" ", ""), op)

    com, sem = [], []
    for op in unicas.values():
        achou = encontra_logo_operadora(op)
        (com if achou else sem).append((op, achou))

    print("\nCobertura por operadora:")
    for op, achou in com:
        print(f"  [ok] {op:26} {achou.name}")
    if sem:
        print("\n  Sem logo (entram com selo tipográfico):")
        print("   ", ", ".join(op for op, _ in sem))

    print(f"\n{erros} erro(s), {avisos} aviso(s).")
    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
