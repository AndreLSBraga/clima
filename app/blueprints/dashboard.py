from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from app.utils.db_consultas import consulta_dados_respostas, consulta_dados_gestor, consulta_time_por_fk_gestor
from app.utils.db_consultas import consulta_sugestoes_por_gestor, consulta_fk_categoria_geral, consulta_desc_categoria_pelo_fk_categoria
from app.utils.db_notas_consultas import consulta_promotores, consulta_intervalo_respostas
from app.utils.dashboard import gera_cards, gera_cards_detalhe, gera_informacoes_respostas, processa_sugestoes
from app.utils.dashboard import gera_grafico, gera_card_gestor_liderado, gera_main_cards, gera_cards_categoria
from datetime import datetime
import json
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
    nome_dashboard = nome_completo_gestor[0].title() + ' ' + nome_completo_gestor[ultimo_nome].title()
    ids_time = consulta_time_por_fk_gestor(fk_gestor)

    intervalo_datas = []
    intervalos_selecionados = []
    datas_min_max = [None, None]
    #Gera intervalo de datas que vão estar possíveis de filtrar
    dados_intervalo_datas = consulta_intervalo_respostas()
    for intervalo in dados_intervalo_datas:
        data = intervalo[0]
        intervalo_datas.append(data)

    intervalos_param = request.args.get('intervalos')
    app.logger.debug(intervalos_param)
    if intervalos_param:
        datas_filtro = []
        intervalos_selecionados = json.loads(intervalos_param)
        #Função de retirar data miníma e máxima do filtro
        for intervalo in intervalos_selecionados:
            inicio, fim = intervalo.split(' - ')
            datas_filtro.append(datetime.strptime(inicio, '%d/%m/%y').date())
            datas_filtro.append(datetime.strptime(fim, '%d/%m/%y').date())

        datas_min_max = [min(datas_filtro), max(datas_filtro)]
    else:
        datas_min_max = [None, None]


    nota_geral = consulta_promotores(datas_min_max, fk_gestor)[0]
    nota_nps = consulta_promotores(datas_min_max, fk_gestor, 29)[0]
    nota_pulsa = consulta_promotores(datas_min_max, fk_gestor, 59)[0]
    grafico_geral = gera_grafico(datas_min_max, fk_gestor)
    dados_main_cards = {
        'nome': nome_dashboard,
        'card1': gera_main_cards(nota_geral),
        'card2': gera_main_cards(nota_nps),
        'card3': gera_main_cards(nota_pulsa)
    }
    
    
    dados_main_grafico = [{
        'semanas': grafico_geral[0],
        'notas': grafico_geral[1],
        'aderencia': grafico_geral[2]
    }]

    cards = gera_cards(datas_min_max, fk_gestor)
    return render_template('dashboard.html', perfil = perfil, dados=dados_main_cards, cards=cards, grafico = dados_main_grafico, intervalos = intervalo_datas, intervalos_selecionados= intervalos_selecionados)

@dashboard_categoria.route('/dashboard/detalhes-categoria:<int:card_id>', methods = ['GET', 'POST'])
def detalhes_categoria_view(card_id):
    datas_min_max = [None, None]
    intervalos_param = request.args.get('intervalos')

    if intervalos_param:
        datas_filtro = []
        intervalos_selecionados = json.loads(intervalos_param)
        #Função de retirar data miníma e máxima do filtro
        for intervalo in intervalos_selecionados:
            inicio, fim = intervalo.split(' - ')
            datas_filtro.append(datetime.strptime(inicio, '%d/%m/%y').date())
            datas_filtro.append(datetime.strptime(fim, '%d/%m/%y').date())
        datas_min_max = [min(datas_filtro), max(datas_filtro)]
    else:
        datas_min_max = [None, None]
    fk_gestor = session['fk_gestor']
    categoria_info = gera_cards_categoria(datas_min_max, fk_gestor, card_id)
    cards_perguntas = gera_cards_detalhe(datas_min_max, fk_gestor, card_id)

    if cards_perguntas:
        return jsonify({
            'categoria': categoria_info,
            'perguntas': cards_perguntas
        })
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
    nome_dashboard = nome_completo_gestor[0].title() + ' ' + nome_completo_gestor[ultimo_nome].title()
    ids_time = consulta_time_por_fk_gestor(fk_gestor)
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
    #Pra cada gestor na lista dos gestores
    for indice, gestor in enumerate(lista_gestores):
        cards_gestores.append(gera_card_gestor_liderado(gestor, indice))
    return render_template('dash_gestores.html', perfil = perfil, dados_gestor = dados_gestor, cards_gestores = cards_gestores)