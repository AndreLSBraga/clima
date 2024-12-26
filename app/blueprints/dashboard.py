from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from app.utils.db_consultas import consulta_dados_respostas, consulta_dados_gestor, consulta_time_por_fk_gestor
from app.utils.db_consultas import consulta_sugestoes_por_gestor, consulta_fk_categoria_geral, consulta_desc_categoria_pelo_fk_categoria, consulta_sugestoes_por_gestor_area
from app.utils.db_notas_consultas import consulta_promotores, consulta_intervalo_respostas, consulta_promotores_area
from app.utils.dashboard import gera_cards, gera_cards_detalhe, gera_informacoes_respostas, processa_sugestoes
from app.utils.dashboard import gera_grafico, gera_tabela_liderados, gera_main_cards, gera_cards_categoria,gera_grafico_area, gera_cards_area, gera_cards_categoria_area, gera_cards_detalhe_area
from flask_babel import _

from datetime import datetime
import json
dashboard = Blueprint('dashboard', __name__)
dashboard_categoria = Blueprint('dashboard_categoria', __name__)
dashboard_sugestoes = Blueprint('dashboard_sugestoes', __name__)
dashboard_area = Blueprint('dashboard_area', __name__)
dashboard_categoria_area = Blueprint('dashboard_categoria_area', __name__)
dashboard_lideres = Blueprint('dashboard_lideres', __name__)

@dashboard.route('/dashboard', methods = ['GET', 'POST'])
def dashboard_view():
    lang = session.get('lang', 'pt')
    fk_pais = 3
    if lang == 'es':
        fk_pais = 1
    
    if 'logged_in' not in session:
        flash(_("É necessário fazer login primeiro."), "error")
        return redirect(url_for('gestor.gestor_view', lang=lang))
    perfil = session['perfil']
    id_gestor = session['id_gestor']
    fk_gestor = session['fk_gestor']
    
    nome_completo_gestor = consulta_dados_gestor(id_gestor)[2].split(" ")
    ultimo_nome = len(nome_completo_gestor)-1
    nome_dashboard = nome_completo_gestor[0].title() + ' ' + nome_completo_gestor[ultimo_nome].title()

    intervalo_datas = []
    intervalos_selecionados = []
    datas_min_max = [None, None]
    #Gera intervalo de datas que vão estar possíveis de filtrar
    dados_intervalo_datas = consulta_intervalo_respostas()
    for intervalo in dados_intervalo_datas:
        data = intervalo[0]
        intervalo_datas.append(data)

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

    cards = gera_cards(datas_min_max, fk_gestor, fk_pais)
    return render_template('dashboard.html',lang=lang, perfil = perfil, dados=dados_main_cards, cards=cards, grafico = dados_main_grafico, intervalos = intervalo_datas, intervalos_selecionados= intervalos_selecionados)

@dashboard_categoria.route('/dashboard/detalhes-categoria:<int:card_id>', methods = ['GET', 'POST'])
def detalhes_categoria_view(card_id):
    lang = session.get('lang', 'pt')
    fk_pais = 3
    if lang == 'es':
        fk_pais = 1
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
    cards_perguntas = gera_cards_detalhe(datas_min_max, fk_gestor, card_id, fk_pais)

    if cards_perguntas:
        return jsonify({
            'categoria': categoria_info,
            'perguntas': cards_perguntas
        })
    else:
        return jsonify({"error": "Categoria não encontrada"}), 404
 
@dashboard_sugestoes.route('/dashboard_sugestoes', methods = ['GET', 'POST'])
def dashboard_sugestoes_view():
    lang = session.get('lang', 'pt')
    fk_pais = 3
    if lang == 'es':
        fk_pais = 1
    if 'logged_in' not in session:
        flash(_("É necessário fazer login primeiro."), "error")
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
    if ids_time:
        tamanho_time = len(ids_time)
    else:
        tamanho_time = 0

    if tamanho_time < 3:
        return render_template('dash_sugestoes.html', perfil= perfil, dados_gestor = dados_gestor)
    
    selecao_sugestao = request.args.get('filtro')
    if selecao_sugestao:
        sugestoes = consulta_sugestoes_por_gestor_area(fk_gestor)
    else:
        sugestoes = consulta_sugestoes_por_gestor(fk_gestor)

    app.logger.debug(sugestoes)
    return render_template('dash_sugestoes.html', perfil = perfil, dados_gestor = dados_gestor, sugestoes = sugestoes)

@dashboard_area.route('/dashboard_area', methods = ['GET', 'POST'])
def dashboard_area_view():
    lang = session.get('lang', 'pt')
    fk_pais = 3
    if lang == 'es':
        fk_pais = 1
    if 'logged_in' not in session:
        flash(_("É necessário fazer login primeiro."), "error")
        return redirect(url_for('gestor.gestor_view'))
    perfil = session['perfil']
    id_gestor = session['id_gestor']
    fk_gestor = session['fk_gestor']
    
    nome_completo_gestor = consulta_dados_gestor(id_gestor)[2].split(" ")
    ultimo_nome = len(nome_completo_gestor)-1
    nome_dashboard = nome_completo_gestor[0].title() + ' ' + nome_completo_gestor[ultimo_nome].title()

    intervalo_datas = []
    intervalos_selecionados = []
    datas_min_max = [None, None]
    #Gera intervalo de datas que vão estar possíveis de filtrar
    dados_intervalo_datas = consulta_intervalo_respostas()
    for intervalo in dados_intervalo_datas:
        data = intervalo[0]
        intervalo_datas.append(data)

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


    nota_geral = consulta_promotores_area(datas_min_max, fk_gestor)[0]
    nota_nps = consulta_promotores_area(datas_min_max, fk_gestor, 29)[0]
    nota_pulsa = consulta_promotores_area(datas_min_max, fk_gestor, 59)[0]
    dados_main_cards = {
        'nome': nome_dashboard,
        'card1': gera_main_cards(nota_geral),
        'card2': gera_main_cards(nota_nps),
        'card3': gera_main_cards(nota_pulsa)
    }

    grafico_geral = gera_grafico_area(datas_min_max, fk_gestor)
    dados_main_grafico = [{
        'semanas': grafico_geral[0],
        'notas': grafico_geral[1],
        'aderencia': grafico_geral[2]
    }]

    cards = gera_cards_area(datas_min_max, fk_gestor, fk_pais)
    return render_template('dashboard_area.html', perfil = perfil, dados=dados_main_cards, cards=cards, grafico = dados_main_grafico, intervalos = intervalo_datas, intervalos_selecionados= intervalos_selecionados)

@dashboard_categoria_area.route('/dashboard_area/detalhes-categoria:<int:card_id>', methods = ['GET', 'POST'])
def detalhes_categoria_area_view(card_id):
    datas_min_max = [None, None]
    intervalos_param = request.args.get('intervalos')
    lang = session.get('lang', 'pt')
    fk_pais = 3
    if lang == 'es':
        fk_pais = 1
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
    categoria_info = gera_cards_categoria_area(datas_min_max, fk_gestor, card_id)
    cards_perguntas = gera_cards_detalhe_area(datas_min_max, fk_gestor, card_id, fk_pais)

    if cards_perguntas:
        return jsonify({
            'categoria': categoria_info,
            'perguntas': cards_perguntas
        })
    else:
        return jsonify({"error": "Categoria não encontrada"}), 404
    
@dashboard_lideres.route('/dashboard_lideres', methods = ['GET', 'POST'])
def dashboard_lideres_view():
    if 'logged_in' not in session:
        flash(_("É necessário fazer login primeiro."), "error")
        return redirect(url_for('gestor.gestor_view'))
    perfil = session['perfil']
    id_gestor = session['id_gestor']
    fk_gestor = session['fk_gestor']
    
    nome_completo_gestor = consulta_dados_gestor(id_gestor)[2].split(" ")
    ultimo_nome = len(nome_completo_gestor)-1
    nome_dashboard = nome_completo_gestor[0].title() + ' ' + nome_completo_gestor[ultimo_nome].title()

    intervalo_datas = []
    intervalos_selecionados = []
    datas_min_max = [None, None]
    #Gera intervalo de datas que vão estar possíveis de filtrar
    dados_intervalo_datas = consulta_intervalo_respostas()
    for intervalo in dados_intervalo_datas:
        data = intervalo[0]
        intervalo_datas.append(data)

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

    dados_main_cards = {
        'nome': nome_dashboard
    }
    dados_gestores = gera_tabela_liderados(datas_min_max, fk_gestor)
    return render_template('dash_gestores.html', perfil = perfil, dados=dados_main_cards, dados_gestores = dados_gestores, intervalos = intervalo_datas, intervalos_selecionados= intervalos_selecionados)
