"""
Gera output/teste-logos.pdf com cada logo nas posições que ela ocupa na proposta.

    python scripts/testar_logos.py

São três contextos, e todos importam:

1. Página do plano  — slot 40 x 14 mm sobre fundo branco.
2. Comparativo      — 7 mm de altura sobre fundo claro.
3. Comparativo (recomendado) — os mesmos 7 mm sobre o navy #011246, onde logo
   sem transparência vira um retângulo branco.

O PDF sai com a mesma folha de estilo da proposta, então o que aparece aqui é
exatamente o que vai aparecer no documento do cliente.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.renderer import (  # noqa: E402
    PASTAS_LOGOS,
    _css_pdf,
    _data_uri,
    _imagens,
    render_pdf,
)

DESTINO = RAIZ / "output" / "teste-logos.pdf"

CSS_EXTRA = """
.folha { padding: 12mm 14mm; }
.tl-titulo {
  font-family: var(--font-display); font-weight: 700; font-size: 16pt;
  letter-spacing: -0.02em; margin-bottom: 1.5mm;
}
.tl-sub { font-size: 8.5pt; color: var(--text-secondary); margin-bottom: 6mm; }
.tl-linha {
  display: grid;
  grid-template-columns: 34mm 46mm 30mm 30mm;
  gap: 3mm; align-items: center;
  padding: 2.4mm 0; border-bottom: 1px solid var(--neutral-100);
  break-inside: avoid;
}
.tl-cab {
  font-family: var(--font-display); font-weight: 600; font-size: 6.8pt;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-tertiary);
  border-bottom: 1px solid var(--border-subtle); padding-bottom: 1.6mm;
}
.tl-nome { font-size: 7.4pt; color: var(--text-secondary); word-break: break-all; }
.tl-nome b { font-family: var(--font-display); font-size: 8.4pt; color: var(--text-primary); display: block; }
.tl-cela { display: flex; align-items: center; justify-content: center; min-height: 15mm; }
.tl-cela--clara { background: var(--neutral-50); border-radius: var(--radius-sm); }
.tl-cela--navy { background: var(--navy-900); border-radius: var(--radius-sm); }
.tl-alerta { color: var(--danger-700); font-size: 7pt; font-weight: 700; }
"""


def _linha(arq: Path, operadora: str | None) -> str:
    uri = _data_uri(arq)
    aviso = "" if operadora else '<span class="tl-alerta">sem operadora correspondente</span>'
    return f"""
    <div class="tl-linha">
      <div class="tl-nome"><b>{operadora or "?"}</b>{arq.name}{aviso}</div>
      <div class="tl-cela"><img class="operadora-logo" src="{uri}" alt=""></div>
      <div class="tl-cela tl-cela--clara"><img class="comp__logo" src="{uri}" alt=""></div>
      <div class="tl-cela tl-cela--navy">
        <img class="comp__logo" src="{uri}" alt="" style="background:#fff;border-radius:3px;padding:1mm 1.6mm">
      </div>
    </div>"""


def main() -> int:
    from app.parser import OPERADORAS, _norm
    from app.renderer import encontra_logo_operadora

    arquivos = _imagens(PASTAS_LOGOS, {".svg"})
    if not arquivos:
        print("Nenhuma logo encontrada.")
        return 1

    # De qual operadora é cada arquivo (usa o mesmo casamento da proposta).
    dono: dict[Path, str] = {}
    vistas: dict[str, str] = {}
    for op in OPERADORAS:
        vistas.setdefault(_norm(op).replace(" ", ""), op)
    for op in vistas.values():
        achou = encontra_logo_operadora(op)
        if achou and achou not in dono:
            dono[achou] = op

    por_pagina = 11
    paginas = []
    for inicio in range(0, len(arquivos), por_pagina):
        lote = arquivos[inicio : inicio + por_pagina]
        linhas = "".join(_linha(a, dono.get(a)) for a in lote)
        paginas.append(f"""
        <section class="page folha">
          <div class="tl-titulo">Teste de logos — {inicio + 1} a {inicio + len(lote)}
            de {len(arquivos)}</div>
          <div class="tl-sub">
            Cada logo nas três posições em que aparece na proposta, com a folha de
            estilo real do PDF. A terceira coluna é a do plano recomendado, onde o
            fundo é navy.
          </div>
          <div class="tl-linha tl-cab">
            <div>Operadora / arquivo</div>
            <div>Página do plano (40 x 14 mm)</div>
            <div>Comparativo (7 mm)</div>
            <div>Comparativo recomendado</div>
          </div>
          {linhas}
        </section>""")

    html = (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        f"<title>Teste de logos</title><style>{_css_pdf()}{CSS_EXTRA}</style></head>"
        f"<body>{''.join(paginas)}</body></html>"
    )

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    render_pdf(html, DESTINO)
    print(f"{len(arquivos)} logos em {len(paginas)} pagina(s) -> {DESTINO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
