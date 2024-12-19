from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from config import SENHA_PRIMEIRO_ACESSO
from datetime import datetime
from app.utils.auth import valida_id, usuario_is_gestor, verifica_senha, codifica_senha, valida_id_novo, valida_email_novo
from app.utils.db_consultas import consulta_dados_gestor, consulta_usuario_id, consulta_usuarios_por_unidade, consulta_fk_dimensao
from app.utils.db_dml import update_senha_gestor,processar_diferencas, criar_usuario
from app.utils.configuracoes import gera_tabela, gera_dados_modal_selecao, verificar_alteracao
from flask_babel import _

gestor = Blueprint('gestor', __name__)
configuracoes = Blueprint('configuracoes', __name__)
configuracoes_usuario = Blueprint('configuracoes_usuario', __name__)
configuracoes_gestor = Blueprint('configuracoes_gestor', __name__)
configuracoes_salvar_alteracoes = Blueprint('configuracoes_salvar_alteracoes', __name__)
configura_senha = Blueprint('configura_senha', __name__)

@gestor.route('/gestor', methods = ['GET', 'POST'])
def gestor_view():
    lang = session.get('lang', 'pt')   
    if request.method == 'POST':
        user_id = request.form['username']
        senha_formulario = request.form['password']
                
        #Valida se usuario é gestor e o id existe
        if not valida_id(user_id) or not usuario_is_gestor(user_id):
            return render_template('gestor.html', lang=lang)

        dados_gestor = consulta_dados_gestor(user_id)
        fk_gestor = dados_gestor[0]
        id_gestor = dados_gestor[1]
        senha_banco = dados_gestor[3]
        primeiro_acesso = dados_gestor[4]
        perfil = dados_gestor[5]
        
        session['fk_gestor'] = fk_gestor
        session['id_gestor'] = id_gestor
        session['perfil'] = perfil
        session['logged_in'] = True

        if not primeiro_acesso:
            if senha_formulario != SENHA_PRIMEIRO_ACESSO:
                flash(_("A senha digitada está incorreta.<br>Tente novamente com a senha correta"), "error")
                return render_template('gestor.html', lang=lang)
            return redirect(url_for('configura_senha.configura_senha_view', lang=lang))
        
        senha_correta = verifica_senha(senha_formulario, senha_banco)
        if not senha_correta:
            flash(_("A senha digitada está incorreta.<br>Tente novamente com a senha correta"), "error")
            return render_template('gestor.html', lang=lang)
        
        return redirect(url_for('dashboard.dashboard_view', lang=lang))

    return render_template('gestor.html', lang=lang)

@configura_senha.route('/configura_senha', methods = ['GET', 'POST'])
def configura_senha_view():
    lang = session.get('lang', 'pt')
    if 'logged_in' not in session:
        flash(_('É necessário fazer login primeiro'),"warning")
        redirect(url_for('gestor.gestor_view', lang=lang))
    fk_gestor = session['fk_gestor']

    if request.method == 'POST':
        senha_padrao = request.form.get('senha_padrao')
        senha_nova = request.form.get('senha_nova')
        senha_confirmacao = request.form.get('senha_confirmacao')

        if senha_padrao != SENHA_PRIMEIRO_ACESSO:
            flash(_("A senha padrão está incorreta.<br>Tente novamente com a senha correta"), "error")
            return render_template('configura_senha.html', lang=lang)
        
        if senha_nova != senha_confirmacao:
            flash(_("As senhas digitadas não conferem.<br>Digite as senhas corretamente"), "error")
            return render_template('configura_senha.html', lang=lang)
        
        senha_codificada = codifica_senha(senha_nova)
        update_senha_gestor(senha_codificada, fk_gestor)
        flash(_('Senha nova cadastrada'),"success")
        return redirect(url_for('gestor.gestor_view', lang=lang))

    return render_template('configura_senha.html', lang=lang)