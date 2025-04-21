FROM python:3.10-slim

WORKDIR /app

# Copiar os arquivos necessários
COPY hunterbot_mvp.py .
COPY scraper_modular.py .
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta do Streamlit
EXPOSE 8501

# Comando para executar o aplicativo
CMD ["streamlit", "run", "hunterbot_mvp.py", "--server.port=8501", "--server.address=0.0.0.0"]
