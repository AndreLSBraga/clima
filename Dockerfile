# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Instale o netcat
RUN apt-get update && apt-get install -y netcat-openbsd

# Defina o diretório de trabalho
WORKDIR /app

# Instale as dependências do Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copie o restante do código da aplicação para o contêiner
COPY . .

# Defina a variável de ambiente para o Flask
ENV FLASK_APP=app


# Exponha a porta que o Flask usa
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["sh", "start.sh"]