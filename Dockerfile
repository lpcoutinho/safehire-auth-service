FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Instalar dependências direto no ambiente final de forma limpa
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY app/ ./app/

# Configurar o usuário não-root (UID 1000 padrão)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]