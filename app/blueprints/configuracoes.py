from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from config import SENHA_PRIMEIRO_ACESSO
from datetime import datetime
from app.utils.auth import valida_id, usuario_is_gestor, verifica_senha, codifica_senha, valida_id_novo, valida_email_novo
from app.utils.db_consultas import consulta_dados_gestor, consulta_usuario_id, consulta_usuarios_por_unidade, consulta_fk_dimensao, consulta_todos_gestores
from app.utils.db_dml import update_senha_gestor,processar_diferencas, criar_usuario, processar_diferencas_gestor, criar_gestor
from app.utils.configuracoes import gera_tabela, gera_dados_modal_selecao, verificar_alteracao, gera_tabela_gestores

configuracoes = Blueprint('configuracoes', __name__)
configuracoes_usuario = Blueprint('configuracoes_usuario', __name__)
configuracoes_gestor = Blueprint('configuracoes_gestor', __name__)
configuracoes_salvar_alteracoes = Blueprint('configuracoes_salvar_alteracoes', __name__)

@configuracoes.route('/configuracoes', methods = ['GET', 'POST'])
def configuracoes_view():
    if 'logged_in' not in session:
        flash("É necessário fazer login primeiro.", "error")
        return redirect(url_for('gestor.gestor_view'))
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
    
    # Página atual e número de itens por página
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10
    gestores = consulta_todos_gestores()
    # Paginando os resultados
    inicio = (pagina - 1) * por_pagina
    final = inicio + por_pagina
    gestores_paginados = gestores[inicio:final]
    
    dados_gestores = gera_tabela_gestores(gestores_paginados)
    total_gestores = len(gestores)
    total_paginas = (total_gestores + por_pagina - 1) // por_pagina
    
    dados_modal = {
        'perfis':['gestor', 'administrador']
    }
    app.logger.debug(dados_gestores)
    return render_template('configuracoes_gestor.html', gestores = dados_gestores, pagina = pagina, total_paginas = total_paginas, selecao = dados_modal)

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
    
@configuracoes_salvar_alteracoes.route('/salvar_alteracoes_gestor', methods=['POST'])
def salvar_alteracoes_gestor():  
    dados_formulario = request.json    
    tipo = dados_formulario.get('tipo')
    globalId_original = dados_formulario.get('globalIdOriginal')
    globalId_novo = dados_formulario.get('globalId')
    #Verifica as informações digitadas
    if not globalId_novo:
        return jsonify({"message":"Preencha os dados obrigatórios.", "status": "error"})
    
    #Verifica se o usuário já existe
    if not globalId_original == globalId_novo:
        if valida_id(globalId_novo):
            return jsonify({"message":"Já existe usuário com esse ID cadastrado.<br> Procure pelo ID nas configurações de usuários.", "status": "error"})
    #Verifica se o ID é apenas números e se são 8 caracteres
    if not valida_id_novo(globalId_novo):
        return jsonify({"message":"Os dados informados no campo 'Global ID' não segue algum dos padrões necessários.<br>Tem mais ou menos que 8 números ou não tem apenas números", "status": "error"})
    
    dados = (
        int(dados_formulario.get('globalId')),
        dados_formulario.get('nome'),
        dados_formulario.get('perfil')
        )
    #Baseado no ID do formulário, consulta o usuário no banco
    dados_gestor = consulta_dados_gestor(globalId_original)
    chaves = ("globalId", "nome", "perfil")

    if tipo == 'edicao':
        #Se o usuário não existir, mensagem de ID Alterado
        if not dados_gestor:
            return jsonify({"message":"Abra novamente a tela de edição, o ID foi alterado.", "status": "warning"})
        
        dados_gestor = dados_gestor[1], dados_gestor[2], dados_gestor[5]
        dados_alteracao = dados
        dicionario_dados_gestor= dict(zip(chaves, dados_gestor))
        dicionario_dados_alteracao = dict(zip(chaves, dados_alteracao))
        #Verifica se houve alterações nos dados
        if dicionario_dados_gestor == dicionario_dados_alteracao:
            return jsonify({"message": "Não houve alteração nos dados do usuário", "status": "warning"})
        else:
            alteracoes = verificar_alteracao(dicionario_dados_gestor, dicionario_dados_alteracao)
            app.logger.debug(alteracoes)
            resultado_diferencas = processar_diferencas_gestor(alteracoes, globalId_original)
        return resultado_diferencas
    
    
    if tipo == 'criacao':
        dicionario_dados_criacao = dict(zip(chaves, dados))
        resultado_criar = criar_gestor(dicionario_dados_criacao)
        return resultado_criar