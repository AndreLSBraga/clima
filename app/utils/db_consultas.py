from app.utils.db import get_db  # Importando a função get_db
from flask import current_app as app

def consulta_usuario_id(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE globalId = %s', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result
    else:
        return None

def consulta_usuario_resposta_data(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT WEEK(data,1) FROM usuario_respondeu WHERE globalId = %s ORDER BY data desc LIMIT 1',(user_id,))
        result = cursor.fetchone()[0]
        app.logger.debug(result)
        cursor.close()
        if result:
                return result
        else:
                return None
        
def consulta_fk_pergunta_categoria():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_pergunta, fk_categoria FROM perguntas')
        result = cursor.fetchall()
        cursor.close()
        return result

def consulta_fk_categoria(fk_pergunta):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_categoria FROM perguntas WHERE fk_pergunta = %s',(fk_pergunta,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result

def consulta_texto_perguntas(fk_pergunta):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT texto_pergunta FROM perguntas WHERE fk_pergunta = %s',(fk_pergunta,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result