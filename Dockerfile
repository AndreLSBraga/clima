# Use a imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo requirements.txt para o contêiner
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install -r requirements.txt

# Copie o restante do código da aplicação para o contêiner
COPY . .

# Defina a variável de ambiente para o Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Exponha a porta que o Flask usa
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["flask", "run"]
