FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=4499 \
    PATH="/usr/games:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends fortune-mod cowsay \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 wisecow \
    && useradd --system --uid 10001 --gid wisecow --no-create-home wisecow

WORKDIR /app
COPY --chown=wisecow:wisecow server.py ./server.py
COPY --chown=wisecow:wisecow wisecow.sh ./wisecow.sh

USER 10001:10001
EXPOSE 4499
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:4499/healthz', timeout=2)"

CMD ["python3", "server.py"]
