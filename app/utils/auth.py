from flask import current_app as app, flash
from app.utils.db import get_db  # Importando a função get_db
from app.utils.db_consultas import consulta_usuario_id, consulta_usuario_resposta_data # Importando a função get_db
from datetime import datetime
import hashlib
import bcrypt

def valida_id(user_id):
    #Verifica se ID é número
    if not user_id.isdigit():
        flash("Digite apenas números no ID.","error")
        return False
    
    usuario = consulta_usuario_id(user_id)
    #Se encontrar o id, verifica se a data está correta
    if usuario:
        return True        
    #Se não, o id não existe na base
    else:
        flash("Usuário não está cadastrado.<br>Entre em contato com seu gestor<br> ou time de gente da unidade.","error")
        return False
    
def valida_data_nascimento(usuario, data_nascimento_formulario):
    data_nascimento = usuario[3]
    data_nascimento_formulario_formatada = datetime.strptime(data_nascimento_formulario, '%Y-%m-%d').date()
    #Compara data nascimento do formulário com a data de nascimento do banco
    if(data_nascimento == data_nascimento_formulario_formatada):
        return True
    else:
        flash("Dados preenchidos não conferem.<br>Verifique os dados preenchidos.","warning")
        return False

def usuario_is_gestor(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM gestores where globalId = %s',(user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
               return True
        else:
               flash("Usuário não está cadastrado como gestor.<br>Entre em contato com o time de gente da unidade.","error")
               return False
        
def codifica_id(user_id):
    user_id_str = str(user_id)
    user_id_bytes = user_id_str.encode('utf-8')
    id_fantasia = hashlib.sha256(user_id_bytes).hexdigest()
    return id_fantasia

def verifica_resposta_usuario(user_id):

    semana_resposta_recente = consulta_usuario_resposta_data(user_id)
    semana_atual = datetime.now().isocalendar()[1]

    if semana_atual == semana_resposta_recente:
        return True
    else:
        return False

def codifica_senha(senha):
    # Gera um salt
    salt = bcrypt.gensalt()
    # Gera o hash da senha com o salt
    senha_codificada = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return senha_codificada

def verifica_senha(senha_digitada, senha_codificada):
    return bcrypt.checkpw(senha_digitada.encode('utf-8'), senha_codificada.encode('utf-8'))

def valida_id_novo(user_id):
    if len(user_id) == 8 and user_id.isdigit():
        return True
    else:
        return False

def valida_email_novo(email):
    # Verifica se a string contém exatamente um '@'
    if '@' in email and email.count('@') == 1:
        # Divide a string em duas partes
        globalId, dominio = email.split('@', 1)        
        # Verifica se a parte antes do '@' não está vazia
        if globalId and dominio:
            # Verifica se o domínio é um dos permitidos
            if dominio == 'ambev.com.br' or dominio == 'ab-inbev.com':
                return True
        return False
    return False


