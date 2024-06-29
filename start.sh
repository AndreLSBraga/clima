#!/bin/sh

# Espere até que o banco de dados esteja pronto
echo "Aguardando o banco de dados estar disponível..."
while ! nc -z db 3306; do
  sleep 1
done

# Executa o script de criação do banco de dados (se necessário)
#python criar_db.py

# Inicia o servidor Flask
flask run --host=0.0.0.0
