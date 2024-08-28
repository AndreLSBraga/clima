from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from config import SENHA_PRIMEIRO_ACESSO
from app.utils.auth import valida_id, usuario_is_gestor, verifica_senha, codifica_senha
from app.utils.db_consultas import consulta_dados_gestor, consulta_usuario_id, consulta_usuarios_por_unidade, consulta_fk_dimensao
from app.utils.db_dml import update_senha_gestor
from app.utils.configuracoes import gera_tabela, gera_dados_modal_selecao

gestor = Blueprint('gestor', __name__)
dashboard = Blueprint('dashboard', __name__)
configuracoes = Blueprint('configuracoes', __name__)
configuracoes_usuario = Blueprint('configuracoes_usuario', __name__)
configuracoes_gestor = Blueprint('configuracoes_gestor', __name__)
configuracoes_salvar_alteracoes = Blueprint('configuracoes_salvar_alteracoes', __name__)
configura_senha = Blueprint('configura_senha', __name__)

@gestor.route('/gestor', methods = ['GET', 'POST'])
def gestor_view():
    if request.method == 'POST':
        user_id = request.form['username']
        senha_formulario = request.form['password']
                
        #Valida se usuario é gestor e o id existe
        if not valida_id(user_id) or not usuario_is_gestor(user_id):
            return render_template('gestor.html')

        dados_gestor = consulta_dados_gestor(user_id)
        fk_gestor = dados_gestor[0]
        id_gestor = dados_gestor[1]
        senha_banco = dados_gestor[3]
        primeiro_acesso = dados_gestor[4]
        
        session['fk_gestor'] = fk_gestor
        session['id_gestor'] = id_gestor
        if not primeiro_acesso:
            if senha_formulario != SENHA_PRIMEIRO_ACESSO:
                flash("A senha digitada está incorreta.<br>Tente novamente com a senha correta", "error")
                return render_template('gestor.html')
            return redirect(url_for('configura_senha.configura_senha_view'))
        
        senha_correta = verifica_senha(senha_formulario, senha_banco)
        if not senha_correta:
            flash("A senha digitada está incorreta.<br>Tente novamente com a senha correta", "error")
            return render_template('gestor.html')
        
        return redirect(url_for('dashboard.dashboard_view'))

    return render_template('gestor.html')

@dashboard.route('/dashboard', methods = ['GET', 'POST'])
def dashboard_view():

    return render_template('dashboard.html')

@configuracoes.route('/configuracoes', methods = ['GET', 'POST'])
def configuracoes_view():
    globalId_gestor = session['id_gestor']
    return render_template('configuracoes.html')

@configuracoes_usuario.route('/configuracoes_usuario', methods = ['GET', 'POST'])
def configuracoes_usuario_view():
    globalId_gestor = session['id_gestor']
    dados_gestor= consulta_usuario_id(globalId_gestor)
    fk_unidade = dados_gestor[10]
    
    # Página atual e número de itens por página
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10
    usuarios_unidade_gestor = consulta_usuarios_por_unidade(fk_unidade)
    # Paginando os resultados
    inicio = (pagina - 1) * por_pagina
    final = inicio + por_pagina
    usuarios_paginados = usuarios_unidade_gestor[inicio:final]

    dados_usuarios = gera_tabela(usuarios_paginados)

    total_usuarios = len(usuarios_unidade_gestor)
    total_paginas = (total_usuarios + por_pagina - 1) // por_pagina
    
    dados_modal = gera_dados_modal_selecao()
    
    return render_template('configuracoes_usuario.html', usuarios = dados_usuarios, pagina = pagina, total_paginas = total_paginas, selecao = dados_modal)

@configuracoes_gestor.route('/configuracoes_gestor', methods = ['GET', 'POST'])
def configuracoes_gestor_view():

    return render_template('configuracoes_gestor.html')

@configuracoes_salvar_alteracoes.route('/salvar_alteracoes', methods=['POST'])
def salvar_alteracoes():  
    dados_alteracao = request.json
    tipo = dados_alteracao.get('tipo')
    global_id = dados_alteracao.get('globalId')
    email = dados_alteracao.get('email')
    nome = dados_alteracao.get('nome')
    data_nascimento = dados_alteracao.get('data_nascimento')
    data_ultima_movimentacao = dados_alteracao.get('data_ultima_movimentacao')
    data_contratacao = dados_alteracao.get('data_contratacao')
    fk_banda = consulta_fk_dimensao('bandas', 'fk_banda', 'descricao_banda' , dados_alteracao.get('banda'))[0]
    fk_tipo_cargo = consulta_fk_dimensao('tipo_cargos', 'fk_tipo_cargo', 'descricao_tipo_cargo', dados_alteracao.get('tipo_cargo'))[0]
    fk_fte = consulta_fk_dimensao('ftes', 'fk_fte', 'descricao_fte', dados_alteracao.get('fte'))[0]
    fk_cargo = consulta_fk_dimensao('cargos','fk_cargo', 'descricao_cargo', dados_alteracao.get('cargo'))[0]
    fk_unidade = consulta_fk_dimensao('unidades','fk_unidade', 'Unidade', dados_alteracao.get('unidade'))[0]
    fk_area = consulta_fk_dimensao('areas', 'fk_area', 'descricao_area', dados_alteracao.get('area'))[0]
    fk_subarea = consulta_fk_dimensao('subareas', 'fk_subarea', 'descricao_subarea', dados_alteracao.get('subarea'))[0]
    fk_gestor = consulta_fk_dimensao('gestores', 'fk_gestor', 'globalId', dados_alteracao.get('id_gestor'))[0]
    fk_genero = consulta_fk_dimensao('generos', 'fk_genero', 'genero', dados_alteracao.get('genero'))[0]

    app.logger.debug(dados_alteracao)

    dados_usuario = consulta_usuario_id(global_id)

    return jsonify({'message': 'Dados salvos com sucesso!'}), 200

@configura_senha.route('/configura_senha', methods = ['GET', 'POST'])
def configura_senha_view():
    fk_gestor = session['fk_gestor']

    if request.method == 'POST':
        senha_padrao = request.form.get('senha_padrao')
        senha_nova = request.form.get('senha_nova')
        senha_confirmacao = request.form.get('senha_confirmacao')

        if senha_padrao != SENHA_PRIMEIRO_ACESSO:
            flash("A senha padrão está incorreta.<br>Tente novamente com a senha correta", "error")
            return render_template('configura_senha.html')
        
        if senha_nova != senha_confirmacao:
            flash("As senhas digitadas não conferem.<br>Digite as senhas corretamente", "error")
            return render_template('configura_senha.html')
        
        senha_codificada = codifica_senha(senha_nova)
        update_senha_gestor(senha_codificada, fk_gestor)
        flash('Senha nova cadastrada',"success")
        return redirect(url_for('gestor.gestor_view'))

    return render_template('configura_senha.html')