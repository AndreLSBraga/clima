from flask import current_app as app, flash
from app.utils.db import get_db  # Importando a função get_db

def consulta_fk_pergunta_categoria():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_pergunta, fk_categoria FROM perguntas')
        result = cursor.fetchall()
        cursor.close()
        return result

def consulta_texto_perguntas(fk_pergunta):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT texto_pergunta FROM perguntas WHERE fk_pergunta = %s',(fk_pergunta,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result

def cria_grupos_perguntas(perguntas):
        grupos_perguntas = {}
        for fk_pergunta, fk_categoria in perguntas:
            if fk_categoria not in grupos_perguntas:
                grupos_perguntas[fk_categoria] = []
            grupos_perguntas[fk_categoria].append(fk_pergunta)
        return grupos_perguntas

