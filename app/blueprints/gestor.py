from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from config import SENHA_PRIMEIRO_ACESSO
from datetime import datetime
from app.utils.auth import valida_id, usuario_is_gestor, verifica_senha, codifica_senha, valida_id_novo, valida_email_novo
from app.utils.db_consultas import consulta_dados_gestor, consulta_usuario_id, consulta_usuarios_por_unidade, consulta_fk_dimensao
from app.utils.db_dml import update_senha_gestor,processar_diferencas, criar_usuario
from app.utils.configuracoes import gera_tabela, gera_dados_modal_selecao, verificar_alteracao

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
        perfil = dados_gestor[5]
        
        session['fk_gestor'] = fk_gestor
        session['id_gestor'] = id_gestor
        session['perfil'] = perfil
        session['logged_in'] = True

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
    app.logger.debug(session == {})
    
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
    perfil = session['perfil']
    return render_template('dashboard.html', perfil = perfil)

@configuracoes.route('/configuracoes', methods = ['GET', 'POST'])
def configuracoes_view():
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))

    globalId_gestor = session['id_gestor']
    return render_template('configuracoes.html')

@configuracoes_usuario.route('/configuracoes_usuario', methods = ['GET', 'POST'])
def configuracoes_usuario_view():
    
    #Se não tiver globalId, voltar para tela inicial
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
    
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
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
    return render_template('configuracoes_gestor.html')

@configuracoes_salvar_alteracoes.route('/salvar_alteracoes', methods=['POST'])
def salvar_alteracoes():  
    dados_formulario = request.json    
    tipo = dados_formulario.get('tipo')
    globalId_original = dados_formulario.get('globalIdOriginal')
    globalId_novo = dados_formulario.get('globalId')
    #Verifica as informações digitadas
    if not globalId_novo:
        return jsonify({"message":"Preencha os dados obrigatórios.", "status": "error"})
    id_gestor = dados_formulario.get('id_gestor')
    
    #Verifica se o usuário já existe
    if not globalId_original == globalId_novo:
        if valida_id(globalId_novo):
            return jsonify({"message":"Já existe usuário com esse ID cadastrado.<br> Procure pelo ID nas configurações de usuários.", "status": "error"})
    #Verifica se o ID é apenas números e se são 8 caracteres
    if not valida_id_novo(globalId_novo):
        return jsonify({"message":"Os dados informados no campo 'Global ID' não segue algum dos padrões necessários.<br>Tem mais ou menos que 8 números ou não tem apenas números", "status": "error"})
    #Verifica se o email digitado é válido
    if not valida_email_novo(dados_formulario.get('email')):
        return jsonify({"message":"Os dados informados no campo 'Email' não segue algum dos padrões necessários.<br>Não está digitado corretamente como @ambev.com.br ou @ab-inbev.com", "status": "error"})
    #Verificar se o ID do gestor é o ID de um gestor existente na base de gestores
    if not consulta_dados_gestor(id_gestor):
        return jsonify({"message":"Os dados informados no campo 'ID Gestor' não existe na base de gestores.<br>Entre em contato com a área de gente da unidade.", "status": "error"})

    data_nascimento = dados_formulario.get('data_nascimento')
    data_ultima_movimentacao = dados_formulario.get('data_ultima_movimentacao')
    data_contratacao = dados_formulario.get('data_contratacao')
    dados = (
        int(dados_formulario.get('globalId')),
        dados_formulario.get('email'),
        dados_formulario.get('nome'),
        datetime.strptime(data_nascimento, '%Y-%m-%d').date(),
        datetime.strptime(data_ultima_movimentacao, '%Y-%m-%d').date(),
        datetime.strptime(data_contratacao, '%Y-%m-%d').date(),
        consulta_fk_dimensao('bandas', 'fk_banda', 'descricao_banda' , dados_formulario.get('banda'))[0],
        consulta_fk_dimensao('tipo_cargos', 'fk_tipo_cargo', 'descricao_tipo_cargo', dados_formulario.get('tipo_cargo'))[0],
        consulta_fk_dimensao('ftes', 'fk_fte', 'descricao_fte', dados_formulario.get('fte'))[0],
        consulta_fk_dimensao('cargos','fk_cargo', 'descricao_cargo', dados_formulario.get('cargo'))[0],
        consulta_fk_dimensao('unidades','fk_unidade', 'Unidade', dados_formulario.get('unidade'))[0],
        consulta_fk_dimensao('areas', 'fk_area', 'descricao_area', dados_formulario.get('area'))[0],
        consulta_fk_dimensao('subareas', 'fk_subarea', 'descricao_subarea', dados_formulario.get('subarea'))[0],
        consulta_fk_dimensao('gestores', 'fk_gestor', 'globalId', dados_formulario.get('id_gestor'))[0],
        consulta_fk_dimensao('generos', 'fk_genero', 'genero', dados_formulario.get('genero'))[0]
        )
    #Baseado no ID do formulário, consulta o usuário no banco
    dados_usuario = consulta_usuario_id(globalId_original)
    chaves = ("globalId", "email", "nome", "data_nascimento", "data_ultima_movimentacao", "data_contratacao", "fk_banda", "fk_tipo_cargo", "fk_fte", "fk_cargo","fk_unidade", "fk_area", "fk_subarea", "fk_gestor", "fk_genero")
        
    if tipo == 'edicao':
        #Se o usuário não existir, mensagem de ID Alterado
        if not dados_usuario:
            return jsonify({"message":"Abrea novamente a tela de edição, o ID foi alterado.", "status": "warning"})
        
        dados_alteracao = dados
        dicionario_dados_usuario = dict(zip(chaves, dados_usuario))
        dicionario_dados_alteracao = dict(zip(chaves, dados_alteracao))
        #Verifica se houve alterações nos dados
        if dicionario_dados_usuario == dicionario_dados_alteracao:
            return jsonify({"message": "Não houve alteração nos dados do usuário", "status": "warning"})
        else:
            alteracoes = verificar_alteracao(dicionario_dados_usuario, dicionario_dados_alteracao)
            resultado_diferencas = processar_diferencas(alteracoes, globalId_original)
        return resultado_diferencas
    
    if tipo == 'criacao':
        dicionario_dados_criacao = dict(zip(chaves, dados))
        resultado_criar = criar_usuario(dicionario_dados_criacao)
        app.logger.debug(resultado_criar)
        return resultado_criar

@configura_senha.route('/configura_senha', methods = ['GET', 'POST'])
def configura_senha_view():
    if 'logged_in' not in session:
        flash('É necessário fazer login primeiro',"warning")
        redirect(url_for('gestor.gestor_view'))
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