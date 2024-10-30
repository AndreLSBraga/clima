from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from app.utils.db_consultas import consulta_dados_respostas, consulta_dados_gestor, consulta_time_por_fk_gestor
from app.utils.db_consultas import consulta_sugestoes_por_gestor, consulta_fk_categoria_geral
from app.utils.dashboard import gera_cards, gera_cards_detalhe, gera_media_quantidade_datas_respostas, processa_sugestoes
from app.utils.dashboard import gera_grafico, gera_card_gestor_liderado

dashboard = Blueprint('dashboard', __name__)
dashboard_categoria = Blueprint('dashboard_categoria', __name__)
dashboard_sugestoes = Blueprint('dashboard_sugestoes', __name__)
dashboard_gestores = Blueprint('dashboard_gestores', __name__)

@dashboard.route('/dashboard', methods = ['GET', 'POST'])
def dashboard_view():
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
    perfil = session['perfil']
    id_gestor = session['id_gestor']
    fk_gestor = session['fk_gestor']
    
    nome_completo_gestor = consulta_dados_gestor(id_gestor)[2].split(" ")
    ultimo_nome = len(nome_completo_gestor)-1
    nome_dashboard = nome_completo_gestor[0] + ' ' + nome_completo_gestor[ultimo_nome]
    ids_time = consulta_time_por_fk_gestor(fk_gestor)

    if ids_time:
        tamanho_time = len(ids_time)
    else:
        tamanho_time = 0

    respostas = consulta_dados_respostas(fk_gestor)
    if respostas:
        qtd_respostas = len(respostas)
    else:
        qtd_respostas = 0
    
    #Criar lógica para não exibir resultados se o tamanho do time for menor que 3 ou não tiver respostas
    if not respostas or tamanho_time < 3 or qtd_respostas < 30:
        dados_main_cards = [{
            'nome': nome_dashboard,
            'nota_media': 0,
            'size_bar': 0,
            'qtd_respostas': qtd_respostas,
            'data_min': '-',
            'data_max': '-',

            'nota_media_nps': 0,
            'size_bar_nps': 0,
            'qtd_respostas_nps': 0,
            'data_min_nps': '-',
            'data_max_nps': '-',

            'nota_media_eficacia': 0,
            'size_bar_eficacia': 0,
            'qtd_respostas_eficacia': 0,
            'data_min_eficacia': '-',
            'data_max_eficacia': '-'
            }]
        
        dados_main_grafico = [{
            'semanas': [],
            'notas': [],
            'aderencia': []
        }]

        cards = gera_cards(None)
        return render_template('dashboard.html', perfil = perfil, dados=dados_main_cards, cards=cards, grafico = dados_main_grafico)

    nota_geral = gera_media_quantidade_datas_respostas(respostas, None, None, fk_gestor)
    nota_nps = gera_media_quantidade_datas_respostas(respostas, None, 29, fk_gestor) #fk_pergunta
    nota_pulsa = gera_media_quantidade_datas_respostas(respostas, None, 59, fk_gestor) #fk_categoria
    grafico_geral = gera_grafico(fk_gestor)
    dados_main_cards = [{
        'nome': nome_dashboard,
        'nota_media': nota_geral[0],
        'size_bar':nota_geral[1],
        'qtd_respostas': nota_geral[2],
        'data_min':nota_geral[3],
        'data_max': nota_geral[4],

        'nota_media_nps': nota_nps[0],
        'size_bar_nps':nota_nps[1],
        'qtd_respostas_nps': nota_nps[2],
        'data_min_nps':nota_nps[3],
        'data_max_nps': nota_nps[4],

        'nota_media_eficacia': nota_pulsa[0],
        'size_bar_eficacia':nota_pulsa[1],
        'qtd_respostas_eficacia': nota_pulsa[2],
        'data_min_eficacia':nota_pulsa[3],
        'data_max_eficacia': nota_pulsa[4]
        }]
    
    dados_main_grafico = [{
        'semanas': grafico_geral[0],
        'notas': grafico_geral[1],
        'aderencia': grafico_geral[2]
    }]

    cards = gera_cards(respostas)
    return render_template('dashboard.html', perfil = perfil, dados=dados_main_cards, cards=cards, grafico = dados_main_grafico)

@dashboard_categoria.route('/dashboard/detalhes-categoria:<int:card_id>', methods = ['GET', 'POST'])
def detalhes_categoria_view(card_id):

    fk_gestor = session['fk_gestor']
    respostas = consulta_dados_respostas(fk_gestor)

    ids_time = consulta_time_por_fk_gestor(fk_gestor)

    if ids_time:
        tamanho_time = len(ids_time)
    else:
        tamanho_time = 0
    respostas = consulta_dados_respostas(fk_gestor)
    if respostas:
        qtd_respostas = len(respostas)
    else:
        qtd_respostas = 0
    #Criar lógica para não exibir resultados se o tamanho do time for menor que 3 ou não tiver respostas
    if not respostas or tamanho_time < 3:
        cards_perguntas = gera_cards_detalhe(None, fk_gestor, card_id)
    
    elif qtd_respostas < 30:
            cards_perguntas = gera_cards_detalhe(None, fk_gestor, card_id)
    else:
        cards_perguntas = gera_cards_detalhe(respostas, fk_gestor, card_id)

    if cards_perguntas:
        return jsonify(cards_perguntas)
    else:
        return jsonify({"error": "Categoria não encontrada"}), 404
 
@dashboard_sugestoes.route('/dashboard_sugestoes', methods = ['GET', 'POST'])
def dashboard_sugestoes_view():
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
    perfil = session['perfil']
    id_gestor = session['id_gestor']
    fk_gestor = session['fk_gestor']
    
    nome_completo_gestor = consulta_dados_gestor(id_gestor)[2].split(" ")
    ultimo_nome = len(nome_completo_gestor)-1
    nome_dashboard = nome_completo_gestor[0] + ' ' + nome_completo_gestor[ultimo_nome]
    ids_time = consulta_time_por_fk_gestor(fk_gestor)
    ids_respondentes = consulta_ids_respondentes
    dados_gestor = {
        'nome': nome_dashboard,
    }
    base_sugestoes = consulta_sugestoes_por_gestor(fk_gestor)

    if ids_time:
        tamanho_time = len(ids_time)
    else:
        tamanho_time = 0

    if tamanho_time < 3 or not base_sugestoes:
        return render_template('dash_sugestoes.html', dados_gestor = dados_gestor)
    
    
    sugestoes = processa_sugestoes(base_sugestoes)
    return render_template('dash_sugestoes.html', perfil = perfil, dados_gestor = dados_gestor, sugestoes = sugestoes)

@dashboard_gestores.route('/dashboard_gestores', methods = ['GET', 'POST'])
def dashboard_gestores_view():
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
    perfil = session['perfil']
    id_gestor = session['id_gestor']
    fk_gestor = session['fk_gestor']
    
    nome_completo_gestor = consulta_dados_gestor(id_gestor)[2].split(" ")
    ultimo_nome = len(nome_completo_gestor)-1
    nome_dashboard = nome_completo_gestor[0] + ' ' + nome_completo_gestor[ultimo_nome]
    ids_time = consulta_time_por_fk_gestor(fk_gestor)
    app.logger.debug(ids_time)
    dados_gestor = {
        'nome': nome_dashboard,
    }
    lista_gestores = []
    cards_gestores = []
    #Verifica se existe time
    if ids_time:
        for user_id in ids_time:
            numero_id = user_id[0]
            dados_gestor_liderado = consulta_dados_gestor(numero_id)
            #Se existir os dados do id na base de gestores, adiciona na lista de gestores
            if dados_gestor_liderado:
                fk_gestor_liderado = dados_gestor_liderado[0]
                nome_completo_liderado = consulta_dados_gestor(numero_id)[2].split(" ")
                ultimo_nome_liderado = len(nome_completo_liderado)-1  
                nome_dashboard_liderado = nome_completo_liderado[0] + ' ' + nome_completo_liderado[ultimo_nome_liderado]
                gestor = {
                    'fk_gestor': fk_gestor_liderado,
                    'nome_liderado': nome_dashboard_liderado
                }
                lista_gestores.append(gestor)
    #Se não tiver gestores na lista, já redireciona para a aba sem enviar os dados de notas
    if not lista_gestores:
        return render_template('dash_gestores.html', perfil = perfil, dados_gestor = dados_gestor)
    app.logger.debug(lista_gestores)
    #Pra cada gestor na lista dos gestores
    for indice, gestor in enumerate(lista_gestores):
        cards_gestores.append(gera_card_gestor_liderado(gestor, indice))
    app.logger.debug(cards_gestores)
    return render_template('dash_gestores.html', perfil = perfil, dados_gestor = dados_gestor, cards_gestores = cards_gestores)