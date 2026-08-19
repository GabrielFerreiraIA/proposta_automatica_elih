"""
Regenera app/static/css/fontes.css com Plus Jakarta Sans + Nunito embutidas.

Rode só quando quiser trocar de fonte ou de peso:

    python scripts/gerar_fontes.py

Por que embutir em vez de usar @import do Google Fonts: com @import, a geração
do PDF passa a depender de rede em tempo de execução. Numa VPS sem saída para a
internet, ou só com DNS lento, o Chromium fica esperando e a geração falha por
timeout. Embutido, o render é offline e determinístico.
"""

from __future__ import annotations

import base64
import re
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Plus+Jakarta+Sans:wght@600;700;800&family=Nunito:wght@400;600;700;800&display=swap"
)
# O PDF é em português: latin e latin-ext bastam. Cirílico, grego e vietnamita
# só engordariam o arquivo sem nunca serem usados.
SUBCONJUNTOS = ("latin", "latin-ext")
DESTINO = Path(__file__).resolve().parent.parent / "app" / "static" / "css" / "fontes.css"

CABECALHO = """/* =========================================================================
   Elih Seguros - fontes embutidas (Plus Jakarta Sans + Nunito, latin)

   Gerado por scripts/gerar_fontes.py. NAO editar a mao.

   Embutir em base64 mantem a geracao do PDF 100%% offline: sem isso, o Chromium
   espera o Google Fonts e a geracao falha por timeout em rede lenta ou ausente.
   ========================================================================= */

"""


def baixar(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def main() -> None:
    css = baixar(URL).decode()
    blocos = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)

    faces, total = [], 0
    for subconjunto, face in blocos:
        if subconjunto not in SUBCONJUNTOS:
            continue
        url = re.search(r"url\((https://[^)]+\.woff2)\)", face).group(1)
        dados = baixar(url)
        total += len(dados)
        face = face.replace(url, f"data:font/woff2;base64,{base64.b64encode(dados).decode()}")
        faces.append(f"/* {subconjunto} */\n{face}")

    DESTINO.write_text(CABECALHO + "\n\n".join(faces) + "\n", encoding="utf-8")
    print(f"{len(faces)} faces | woff2 {total / 1024:.0f} KB | {DESTINO.name} "
          f"{DESTINO.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
