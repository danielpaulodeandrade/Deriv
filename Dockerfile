# syntax=docker/dockerfile:1
FROM python:3.14-slim

# Variáveis de ambiente para comportamento determinístico e seguro do Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Criação de usuário e grupo não-root e preparação do diretório de trabalho
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/bash appuser && \
    mkdir -p /app && \
    chown -R appuser:appgroup /app

WORKDIR /app

# Execução como usuário não-root
USER appuser

# Copia código-fonte com posse do appuser
COPY --chown=appuser:appgroup . .

# Instala a aplicação e dependências (incluindo dependências de desenvolvimento/testes)
RUN pip install --user -e ".[dev]"

# Porta padrão da API
EXPOSE 8000

# Comando padrão
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
