from flask import current_app as app, flash
from app.utils.db import get_db  # Importando a função get_db

def valida_id(user_id,data_nascimento_formulario):
    #Verifica se ID é número
    if not user_id.isdigit():
        flash("Digite apenas números no ID.","error")
        return False
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE globalId = %s', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    #Se encontrar o id, verifica se a data está correta
    if result:
        data_nascimento = result[3]
        #Compara data nascimento do formulário com a data de nascimento do banco
        if(data_nascimento == data_nascimento):
            return True
        else:
            flash("Dados preenchidos não conferem.<br>Verifique os dados preenchidos.","warning")
            return False
    #Se não, o id não existe na base
    else:
        flash("Usuário não está cadastrado.<br>Entre em contato com seu gestor<br> ou time de gente da unidade.","error")
        return False