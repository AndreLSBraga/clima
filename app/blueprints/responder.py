from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app
from app.utils.consulta_perguntas import consulta_fk_pergunta_categoria, consulta_texto_perguntas, cria_grupos_perguntas  # Importando a função get_db
import random

responder = Blueprint('responder', __name__)

@responder.route('/responder', methods=['GET', 'POST'])
def responder_view():
    fk_perguntas_categorias = consulta_fk_pergunta_categoria()
    grupo_perguntas = cria_grupos_perguntas(fk_perguntas_categorias)

    #Sorteia as perguntas que serão selecionadas
    if 'perguntas_selecionadas' not in session or session['perguntas_selecionadas'] == []:
        perguntas_selecionadas = []
        session['pergunta_atual'] = 0
        for grupo in grupo_perguntas.values():
            selecionadas = random.sample(grupo, min(1, len(grupo)))
            perguntas_selecionadas += selecionadas
        if len(perguntas_selecionadas) >= 10:
            session['perguntas_selecionadas'] = random.sample(perguntas_selecionadas, 10)
        else:
            session['perguntas_selecionadas'] = perguntas_selecionadas

    num_pergunta = session['pergunta_atual']
    perguntas_selecionadas = session['perguntas_selecionadas']
    fk_pergunta_atual = perguntas_selecionadas[num_pergunta]
    texto_pergunta = consulta_texto_perguntas(fk_pergunta_atual)

    if num_pergunta >= len(perguntas_selecionadas):
        return redirect(url_for('pagina_final.pagina_final_view'))
    
    if request.method == 'POST':
        if 'anterior' in request.form:
            if num_pergunta > 0:
                num_pergunta = num_pergunta - 1
                session['pergunta_atual'] = num_pergunta
    

    return render_template('responder.html', pergunta = texto_pergunta, pergunta_num = num_pergunta+1, total_perguntas = 10)