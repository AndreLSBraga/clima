from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app as app
from app.utils.auth import valida_id, consulta_usuario_id, codifica_id, verifica_resposta_usuario
import datetime

pagina_inicial = Blueprint('pagina_inicial', __name__)

@pagina_inicial.route('/', methods=['GET', 'POST'])
def pagina_inicial_view():
    
    #Limpa o cache quando acessa a tela da página inicial
    session.clear()

    if request.method == 'POST':
        user_id = request.form['user_id']
        data_nascimento = request.form['data_nascimento'] 
        if not user_id or not data_nascimento:
            flash("Preencha todos os campos", "warning")
        elif valida_id(user_id,data_nascimento):
            #Verica se o usuário já respondeu na semana
            usuario_respondeu_semana = verifica_resposta_usuario(user_id)
            if usuario_respondeu_semana == True:
                return redirect(url_for('pagina_final.pagina_final_view'))
            
            #Usa o id respondido no formulário para ser codificado mas consulta o banco antes
            usuario = consulta_usuario_id(user_id)
            id_resposta = codifica_id(user_id)
            data_nascimento = usuario[3]
            data_ultima_movimentação = usuario[4]
            data_contratacao = usuario[5]
            fk_banda = usuario[6]
            fk_tipo_cargo = usuario[7]
            fk_fte = usuario[8]
            fk_cargo = usuario[9]
            fk_unidade = usuario[10]
            fk_area = usuario[11]
            fk_subarea = usuario[12]
            fk_gestor = usuario[13]
            fk_genero = usuario[14]
            data_hora = datetime.datetime.now()

            #Envia os dados que serão salvos no banco do usuário
            session['dados'] = {
                'id_resposta': id_resposta,
                'data_hora': data_hora,
                'data_nascimento': data_nascimento,
                'data_ultima_movimentacao': data_ultima_movimentação,
                'data_contratacao': data_contratacao, 
                'fk_banda': fk_banda,
                'fk_tipo_cargo': fk_tipo_cargo,
                'fk_fte': fk_fte,
                'fk_cargo': fk_cargo,
                'fk_unidade': fk_unidade,
                'fk_area':fk_area,
                'fk_subarea': fk_subarea,
                'fk_gestor':fk_gestor,
                'fk_genero':fk_genero,
                'id_usuario':user_id
            }
            return redirect(url_for('responder.responder_view'))
        else:
            return render_template('pagina_inicial.html')

    return render_template('pagina_inicial.html')
