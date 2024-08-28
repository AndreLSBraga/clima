from app.utils.db import get_db  # Importando a função get_db
from flask import current_app as app, flash

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

def consulta_categorias():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT desc_categoria FROM categorias')
        result = cursor.fetchall()
        cursor.close()
        return result

def consulta_fk_categoria_pela_desc_categoria(desc_categoria):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_categoria FROM categorias where desc_categoria = %s',(desc_categoria,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result

def consulta_dados_gestor(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM gestores WHERE globalId = %s',(user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

def consulta_usuarios_por_unidade(fk_unidade):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE fk_unidade = %s ORDER BY globalId asc', (fk_unidade,))
    result = cursor.fetchall()
    cursor.close()
    if result:
        return result
    else:
        return None
    
def consulta_tabela_dimensao(tabela, coluna=None, pesquisa=None):
        query = f'SELECT * FROM {tabela}'
        params = []
        conditions = []
        fetchone = False

        if coluna is not None:
            conditions.append(f'{coluna} = {pesquisa}')
            params.append(coluna)
            fetchone = True
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query)
        if not fetchone:
                result = cursor.fetchall()
        else:
                result = cursor.fetchone()

        cursor.close()
        if result:
                return result
        else:
                return None
        
def consulta_fk_dimensao(tabela, coluna_retorno, coluna_pesquisa, pesquisa):
        query = f'SELECT {coluna_retorno} FROM {tabela}'
        params = []
        conditions = []
        fetchone = False

        if coluna_pesquisa is not None:
                conditions.append(f"{coluna_pesquisa} = '{pesquisa}'")
                params.append(coluna_pesquisa)
                fetchone = True

        if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query)
        if not fetchone:
                result = cursor.fetchall()
        else:
                result = cursor.fetchone()

        cursor.close()
        if result:
                return result
        else:
                return None