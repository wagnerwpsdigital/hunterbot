# Etapa 1: imagem base com Python leve
FROM python:3.10-slim

# Etapa 2: diretório padrão
WORKDIR /app

# Etapa 3: copiar os arquivos do projeto para o container
COPY . /app

# Etapa 4: instalar as dependências via pip
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 5: expor a porta padrão do Streamlit
EXPOSE 8501

# Etapa 6: comando que inicia o app ao rodar o container
CMD ["streamlit", "run", "hunterbot_mvp.py", "--server.port=8501", "--server.address=0.0.0.0"]
