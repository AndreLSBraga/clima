#!/bin/sh

echo "Aguardando o banco de dados estar disponível..."
while ! nc -z db 3306; do
  echo "Esperando pelo banco de dados..."
  sleep 1
done

echo "Banco de dados disponível. Executando script de criação do banco de dados..."
python criar_db.py

echo "Iniciando o servidor Flask..."
flask run --host=0.0.0.0
