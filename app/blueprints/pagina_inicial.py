from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app as app
from flask_babel import _
from app.utils.auth import valida_id, valida_data_nascimento, consulta_usuario_id, codifica_id, verifica_resposta_usuario
import datetime
import time
pagina_inicial = Blueprint('pagina_inicial', __name__)

@pagina_inicial.route('/', methods=['GET', 'POST'])
def pagina_inicial_view():
    
    lang_url = request.args.get('lang')
    if not lang_url:
        lang = session.get('lang', 'pt')
    else:
        lang = request.args.get('lang')
    session.clear()
    session['lang'] = lang

    if request.method == 'POST':
        user_id = request.form['user_id']
        data_nascimento = request.form['data_nascimento'] 
        if not user_id or not data_nascimento:
            flash(_("Preencha todos os campos"), "warning")
            return redirect(url_for('pagina_inicial.pagina_inicial_view', lang=lang))
                        
        #Verifica se o ID existe
        if valida_id(user_id):  
            #Usa o id respondido no formulário para ser codificado mas consulta o banco antes
            usuario = consulta_usuario_id(user_id)
            #Verifica se a data de nascimento respondida está correta
            if valida_data_nascimento(usuario, data_nascimento):
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
                fk_pais = usuario[15]
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
                    'fk_pais': fk_pais,
                    'id_usuario':user_id
                }
                #Verica se o usuário já respondeu na semana
                usuario_respondeu_semana = verifica_resposta_usuario(user_id)
                if usuario_respondeu_semana == True:
                    return redirect(url_for('pagina_final.pagina_final_view', lang=lang))
                return redirect(url_for('responder.responder_view', lang=lang))

        return redirect(url_for('pagina_inicial.pagina_inicial_view',lang=lang))
    return render_template('pagina_inicial.html', lang=lang)
