#!/bin/sh

echo "Aguardando o banco de dados estar disponível..."
while ! nc -z db 3306; do
  sleep 1
done

echo "Iniciando o servidor Flask..."
flask run --host=0.0.0.0
