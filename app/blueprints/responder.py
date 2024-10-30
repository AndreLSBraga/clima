from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app
from app.utils.responder import cria_grupos_perguntas, sorteia_perguntas, navegar_perguntas
from app.utils.db_consultas import consulta_fk_pergunta_categoria, consulta_fk_categoria, consulta_texto_perguntas
from app.utils.db_dml import insert_resposta,insert_usuario_respondeu
from datetime import datetime
from random import shuffle

responder = Blueprint('responder', __name__)

@responder.route('/responder', methods=['GET', 'POST'])
def responder_view():
    #Coloca em uma variável os dados do session
    dados_usuario = session['dados']
    fk_pais = dados_usuario.get('fk_pais', 3)
    #Consulta db para trazer as perguntas e categoria
    fk_perguntas_categorias = consulta_fk_pergunta_categoria()
    #Cria grupo de perguntas que serão sorteadas
    grupo_perguntas = cria_grupos_perguntas(fk_perguntas_categorias)

    semana_atual = datetime.now().isocalendar()[1]
    
    if 'perguntas_selecionadas' not in session:
        # Verifica se a semana é múltipla de 4 e define perguntas fixas
        if semana_atual % 4 == 0 or semana_atual == 36 or semana_atual == 38 or (semana_atual >=40 and semana_atual <=43):
            perguntas_fixas = [50, 51, 52, 53, 54, 55, 56, 57, 58, 59]
            shuffle(perguntas_fixas)  # Embaralha a lista de perguntas fixas
            session['pergunta_atual'] = 0
            session['perguntas_selecionadas'] = perguntas_fixas
        else:
            # Sorteia as perguntas e salva dados da sessão
            session['pergunta_atual'] = 0
            session['perguntas_selecionadas'] = sorteia_perguntas(grupo_perguntas)
    
    perguntas_selecionadas = session['perguntas_selecionadas']
    num_pergunta_atual = session['pergunta_atual']
    fk_pergunta_atual = perguntas_selecionadas[num_pergunta_atual]
    fk_categoria = consulta_fk_categoria(fk_pergunta_atual)

    if request.method in ['POST','GET']:
        action = request.form.get('action')
        if num_pergunta_atual >= len(perguntas_selecionadas):
            return redirect(url_for('pagina_final.pagina_final_view'))

        if 'respostas' not in session:
            session['respostas'] = []

        if 'pular' in request.form or action == 'pular' or 'proxima' in request.form or action == 'proxima':
            if 'pular' in request.form or action == 'pular':
                resposta = -1
                sugestao = request.form.get('sugestao')
                botao_clicado = 'pular'
            elif 'proxima' in request.form or action == 'proxima':
                botao_clicado = 'proxima'
                resposta = request.form.get('resposta')
                sugestao = request.form.get('sugestao')
            
            check_box_auto_identificacao = request.form.get('auto_identificacao')
            if check_box_auto_identificacao:
                auto_identificacao = 1
            else:
                auto_identificacao = 0

            session['respostas'].append({
                'num_pergunta': num_pergunta_atual,
                'fk_categoria': fk_categoria,
                'fk_pergunta': fk_pergunta_atual,
                'resposta': resposta,
                'sugestao': sugestao,
                'auto_identificacao_sugestao': auto_identificacao
            })

            num_pergunta_atual = navegar_perguntas(num_pergunta_atual, botao_clicado, len(perguntas_selecionadas))
            
            session['pergunta_atual'] = num_pergunta_atual

        elif 'anterior' in request.form:
            botao_clicado = 'anterior'
            if num_pergunta_atual > 0:
                num_pergunta_atual -= 1
                session['respostas'] = [res for res in session['respostas'] if res['num_pergunta'] != num_pergunta_atual]
            session['pergunta_atual'] = num_pergunta_atual

        if 'enviar' in request.form:
            for resposta in session['respostas']:
                insert_resposta(dados_usuario,resposta, 'resposta')
                if resposta['sugestao']:
                    insert_resposta(dados_usuario,resposta, 'sugestao')
            insert_usuario_respondeu(dados_usuario)
            return redirect(url_for('pagina_final.pagina_final_view'))

    #Carrega o fk da pergunta e o texto da pergunta
    fk_pergunta_atual = perguntas_selecionadas[num_pergunta_atual]
    fk_categoria = consulta_fk_categoria(fk_pergunta_atual)
    texto_pergunta = consulta_texto_perguntas(fk_pergunta_atual, fk_pais)
    return render_template('responder.html', pergunta = texto_pergunta, pergunta_num = num_pergunta_atual + 1, total_perguntas = 10)