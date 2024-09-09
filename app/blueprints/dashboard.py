from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from app.utils.db_consultas import consulta_dados_respostas, consulta_dados_gestor, consulta_time_por_fk_gestor
from app.utils.dashboard import processa_respostas, gera_cards, gera_cards_detalhe
dashboard = Blueprint('dashboard', __name__)
dashboard_categoria = Blueprint('dashboard_categoria', __name__)

@dashboard.route('/dashboard', methods = ['GET', 'POST'])
def dashboard_view():    
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
    perfil = session['perfil']
    id_gestor = session['id_gestor']
    fk_gestor = session['fk_gestor']
    
    nome_completo_gestor = consulta_dados_gestor(id_gestor)[2].split(" ")
    ultimo_nome_completo = len(nome_completo_gestor)-1
    nome_dashboard = nome_completo_gestor[0] + ' ' + nome_completo_gestor[ultimo_nome_completo]
    
    respostas = consulta_dados_respostas(fk_gestor)
    nota_geral = processa_respostas(respostas, None, None, fk_gestor)
    nota_nps = processa_respostas(respostas, None, 53) #fk_pergunta
    nota_pulsa = processa_respostas(respostas, 11) #fk_categoria
    cards = gera_cards(respostas)

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
        'semanas': nota_geral[5],
        'notas': nota_geral[6],
        'aderencia': nota_geral[7]
    }]
    
    return render_template('dashboard.html', perfil = perfil, dados=dados_main_cards, cards=cards, grafico = dados_main_grafico)

@dashboard_categoria.route('/dashboard/detalhes-categoria:<int:card_id>', methods = ['GET', 'POST'])
def detalhes_categoria_view(card_id):
    
    fk_gestor = session['fk_gestor']
    respostas = consulta_dados_respostas(fk_gestor)
    cards_perguntas = gera_cards_detalhe(respostas, card_id)
    if cards_perguntas:
        return jsonify(cards_perguntas)
    else:
        return jsonify({"error": "Categoria não encontrada"}), 404