# Imagem oficial do Playwright: já traz o Chromium e todas as libs de sistema
# que ele precisa para renderizar (fontes, freetype, nss). Manter a tag alinhada
# com a versão do playwright em requirements.txt.
FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install chromium

COPY app ./app
COPY assets ./assets

RUN mkdir -p /app/output/_uploads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD sh -c 'python -c "import sys,urllib.request; urllib.request.urlopen(sys.argv[1]).read()" "http://127.0.0.1:${PORT:-8000}/api/saude"'

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
