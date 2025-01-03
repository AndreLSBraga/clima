from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app
from app.utils.responder import cria_grupos_perguntas, sorteia_perguntas, navegar_perguntas
from app.utils.db_consultas import consulta_fk_pergunta_categoria, consulta_fk_categoria, consulta_texto_perguntas,quantidade_perguntas_pesquisa, consulta_fk_perguntas_mega_pulso, consulta_perguntas_selecionadas
from app.utils.db_dml import insert_resposta,insert_usuario_respondeu
from datetime import datetime
from random import shuffle
from flask_babel import _

responder = Blueprint('responder', __name__)

@responder.route('/responder', methods=['GET', 'POST'])
def responder_view():
    
    #Coloca em uma variável os dados do session
    dados_usuario = session['dados']
    lang_url = request.args.get('lang')
    if not lang_url:
        lang = session.get('lang', 'pt')
    else:
        lang = request.args.get('lang')

    if lang:
        if lang == 'pt':
            fk_pais = 3
        if lang =='es':
            fk_pais = 1

    #Consulta db para trazer as perguntas e categoria
    fk_perguntas_categorias = consulta_fk_pergunta_categoria()
    #Cria grupo de perguntas que serão sorteadas
    grupo_perguntas = cria_grupos_perguntas(fk_perguntas_categorias)

    if 'perguntas_selecionadas' not in session:
        data_atual = datetime.now().date() #Dia atual
        data_inicio_pesquisa = datetime(2024,9,30).date() #Data de inicio da primeira pesquisa do modelo
        diferenca_dias = (data_atual - data_inicio_pesquisa).days #Número de dias entre a data atual e o início da pesquisa
        ciclo_atual = diferenca_dias // 14 #Ciclo atual de respostas
        app.logger.debug(ciclo_atual)
        # Verifica se o ciclo é um ciclo par, ciclos pares = Mega pulso | ciclos impares = Pulso
        if ciclo_atual % 2 == 0:
            perguntas_fixas = consulta_fk_perguntas_mega_pulso()
            shuffle(perguntas_fixas)  # Embaralha a lista de perguntas fixas
            session['pergunta_atual'] = 0
            session['perguntas_selecionadas'] = perguntas_fixas
            session['qtd_perguntas'] = len(perguntas_fixas)
            
        else:
            # Sorteia as perguntas e salva dados da sessão
            session['pergunta_atual'] = 0
            session['qtd_perguntas'] = quantidade_perguntas_pesquisa()
            session['perguntas_selecionadas'] = sorteia_perguntas(grupo_perguntas, quantidade_perguntas_pesquisa())
    
    perguntas_selecionadas = session['perguntas_selecionadas']
    qtd_perguntas = session['qtd_perguntas']
    dados_perguntas_selecionadas = consulta_perguntas_selecionadas(perguntas_selecionadas)
    num_pergunta_atual = session['pergunta_atual']
    fk_pergunta_atual = perguntas_selecionadas[num_pergunta_atual]
    for fk_pergunta_selecionadas, fk_categoria_selecionadas, texto_pergunta_pt, texto_pergunta_es in dados_perguntas_selecionadas:
        if fk_pergunta_selecionadas == fk_pergunta_atual:
            fk_categoria = fk_categoria_selecionadas
            if fk_pais == 3:
                texto_pergunta = texto_pergunta_pt
            else:
                texto_pergunta = texto_pergunta_es
            break;    

    if request.method in ['POST','GET']:
        action = request.form.get('action')
        if num_pergunta_atual >= qtd_perguntas:
            return redirect(url_for('pagina_final.pagina_final_view', lang=lang))

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

            num_pergunta_atual = navegar_perguntas(num_pergunta_atual, botao_clicado, qtd_perguntas)
            
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
            return redirect(url_for('pagina_final.pagina_final_view', lang=lang))

    #Carrega o fk da pergunta e o texto da pergunta
    fk_pergunta_atual = perguntas_selecionadas[num_pergunta_atual]

    for fk_pergunta_selecionadas, fk_categoria_selecionadas, texto_pergunta_pt, texto_pergunta_es in dados_perguntas_selecionadas:
        if fk_pergunta_selecionadas == fk_pergunta_atual:
            fk_categoria = fk_categoria_selecionadas
            if fk_pais == 3:
                texto_pergunta = texto_pergunta_pt
            else:
                texto_pergunta = texto_pergunta_es
            break;
    
    return render_template('responder.html', pergunta = texto_pergunta, pergunta_num = num_pergunta_atual + 1, total_perguntas = qtd_perguntas, lang=lang)