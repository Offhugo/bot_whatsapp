# Python 3.13 é a versão em que este projeto está sendo executado no ambiente de desenvolvimento.
# Se a sua máquina usa outra versão, ajuste aqui e teste localmente.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala dependências primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# O Render define a variável PORT. O valor padrão 10000 é usado só se ela não existir.
# A forma "shell" (sh -c) é necessária para expandir ${PORT}.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
