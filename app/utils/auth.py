from flask import current_app as app, flash
from flask_babel import _
from app.utils.db import get_db  # Importando a função get_db
from app.utils.db_consultas import consulta_usuario_id, consulta_usuario_resposta_semana, consulta_usuario_resposta_data # Importando a função get_db
from datetime import datetime, timedelta
import hashlib
import bcrypt

def valida_id(user_id):
    #Verifica se ID é número
    if not user_id.isdigit():
        flash(_("Digite apenas números no ID."),"error")
        return False
    
    usuario = consulta_usuario_id(user_id)
    #Se encontrar o id, verifica se a data está correta
    if usuario:
        return True        
    #Se não, o id não existe na base
    else:
        flash(_("Usuário não está cadastrado.<br>Entre em contato com seu gestor<br> ou time de gente da unidade."),"error")
        return False
    
def valida_data_nascimento(usuario, data_nascimento_formulario):
    if len(data_nascimento_formulario)>10:
        flash(_("Digite uma data de nascimento válida"),"error")
        return False
    data_nascimento = usuario[3]
    data_nascimento_formulario_formatada = datetime.strptime(data_nascimento_formulario, '%Y-%m-%d').date()
    #Compara data nascimento do formulário com a data de nascimento do banco
    if(data_nascimento == data_nascimento_formulario_formatada):
        return True
    else:
        flash(_("Dados preenchidos não conferem.<br>Verifique os dados preenchidos."),"warning")
        return False

def consulta_gestor_cadastrado(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM gestores where globalId = %s',(user_id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return True
    else:
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
               flash(_("Usuário não está cadastrado como gestor.<br>Entre em contato com o time de gente da unidade."),"error")
               return False
def codifica_id(user_id):
    user_id_str = str(user_id)
    user_id_bytes = user_id_str.encode('utf-8')
    id_fantasia = hashlib.sha256(user_id_bytes).hexdigest()
    return id_fantasia

def verifica_resposta_usuario(user_id):

    data_atual = datetime.now().date() #Dia atual
    data_inicio_pesquisa = datetime(2024,9,30).date() #Data de inicio da primeira pesquisa do modelo
    
    #Verifica se a semana da resposta do usuário, é a semana atual
    if data_atual < data_inicio_pesquisa:
        semana_resposta_recente = consulta_usuario_resposta_semana(user_id)
        semana_atual = datetime.now().isocalendar()[1]

        if semana_atual == semana_resposta_recente:
            return True
        else:
            return False

    diferenca_dias = (data_atual - data_inicio_pesquisa).days #Número de dias entre a data atual e o início da pesquisa
    ciclo_atual = diferenca_dias // 14 #Ciclo atual de respostas

    data_ultima_resposta_usuario = consulta_usuario_resposta_data(user_id) #Dia que o usuário respondeu
    if not data_ultima_resposta_usuario:
        return False
    if data_ultima_resposta_usuario < data_inicio_pesquisa:
        # A resposta é antes da pesquisa, então pode responder
        return False
    
    diferenca_dias_resposta_usuario = (data_ultima_resposta_usuario - data_inicio_pesquisa).days    
    ciclo_resposta = diferenca_dias_resposta_usuario // 14  # Ciclo da última resposta
    # Se o ciclo da última resposta for igual ao ciclo atual, o usuário já respondeu nesta quinzena
    if ciclo_atual == ciclo_resposta:
        return True  # Já respondeu nesta quinzena
    else:
        return False  # Ainda não respondeu nesta quinzena, pode responder

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
            dominio = dominio.lower()
            # Verifica se o domínio é um dos permitidos
            if 'ambev.com' in dominio  or 'ab-inbev.com' in dominio:
                return True
        return False
    return False


