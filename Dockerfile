# Etapa 1: usar imagem base leve com Python
FROM python:3.10-slim

# Etapa 2: definir diretório de trabalho
WORKDIR /app

# Etapa 3: copiar os arquivos do projeto para dentro do container
COPY . /app

# Etapa 4: instalar dependências listadas no requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 5: expor a porta padrão do Streamlit
EXPOSE 8501

# Etapa 6: comando para iniciar a aplicação
CMD ["streamlit", "run", "hunterbot_mvp.py", "--server.port=8501", "--server.address=0.0.0.0"]
