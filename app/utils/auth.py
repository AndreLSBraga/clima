from flask import current_app as app, flash
from app.utils.db_consultas import consulta_usuario_id, consulta_usuario_resposta_data # Importando a função get_db
from datetime import datetime
import hashlib
import bcrypt

def valida_id(user_id,data_nascimento_formulario):
    #Verifica se ID é número
    if not user_id.isdigit():
        flash("Digite apenas números no ID.","error")
        return False
    
    usuario = consulta_usuario_id(user_id)
    #Se encontrar o id, verifica se a data está correta
    if usuario:
        data_nascimento = usuario[3]
        data_nascimento_formulario_formatada = datetime.strptime(data_nascimento_formulario, '%Y-%m-%d').date()
        #Compara data nascimento do formulário com a data de nascimento do banco
        if(data_nascimento == data_nascimento_formulario_formatada):
            return True
        else:
            flash("Dados preenchidos não conferem.<br>Verifique os dados preenchidos.","warning")
            return False
    #Se não, o id não existe na base
    else:
        flash("Usuário não está cadastrado.<br>Entre em contato com seu gestor<br> ou time de gente da unidade.","error")
        return False
    
def codifica_id(user_id):
    user_id_str = str(user_id)
    user_id_bytes = user_id_str.encode('utf-8')
    id_fantasia = hashlib.sha256(user_id_bytes).hexdigest()
    return id_fantasia

def verifica_resposta_usuario(user_id):
    semana_resposta_recente = consulta_usuario_resposta_data(user_id)
    semana_atual = datetime.now().isocalendar()[1]
    app.logger.debug(f'Semana resposta:{semana_resposta_recente}, semana atual:{semana_atual}')

    if semana_atual == semana_resposta_recente:
        return True
    else:
        return False