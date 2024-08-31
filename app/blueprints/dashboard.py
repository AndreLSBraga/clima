from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard', methods = ['GET', 'POST'])
def dashboard_view():
    app.logger.debug(session == {})
    
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
    perfil = session['perfil']


    cards = [
        {'id': 1, 'title': 'Engagment', 'value': 85, 'size': 85, 'qtd_respostas': 50, 'qtd_puladas': 5, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 2, 'title': 'Liderança', 'value': 90, 'size': 90, 'qtd_respostas': 45, 'qtd_puladas': 3, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 3, 'title': 'Funções Desempenhadas', 'value': 75, 'size': 75, 'qtd_respostas': 60, 'qtd_puladas': 7, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 4, 'title': 'Plano de Carreira', 'value': 88, 'size': 88, 'qtd_respostas': 52, 'qtd_puladas': 4, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 5, 'title': 'Ambiente e Ferramentas', 'value': 80, 'size': 80, 'qtd_respostas': 55, 'qtd_puladas': 6, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 6, 'title': 'Salário e Benefícios', 'value': 70, 'size': 70, 'qtd_respostas': 48, 'qtd_puladas': 8, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 7, 'title': 'Feedback e Reconhecimento', 'value': 92, 'size': 92, 'qtd_respostas': 49, 'qtd_puladas': 2, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 8, 'title': 'Comunicação e Colaboração', 'value': 85, 'size': 85, 'qtd_respostas': 51, 'qtd_puladas': 3, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 9, 'title': 'Serviços Gerais', 'value': 77, 'size': 77, 'qtd_respostas': 58, 'qtd_puladas': 6, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 10, 'title': 'Segurança Psicológica', 'value': 82, 'size': 82, 'qtd_respostas': 54, 'qtd_puladas': 5, 'data_min': '15/02', 'data_max': '31/08'},
        {'id': 11, 'title': 'Pulsa Supply', 'value': 88, 'size': 88, 'qtd_respostas': 56, 'qtd_puladas': 4, 'data_min': '15/02', 'data_max': '31/08'}
    ]
    
    dados = [{
            'nome': 'nome_gestor',
            'qtd_respostas': 32,
            'nota_media': 7.32,
            'size_bar':73.2,
            'data_min':'22/03',
            'data_max': '22/03',
        }]

    return render_template('dashboard.html', perfil = perfil, dados=dados, cards=cards)

