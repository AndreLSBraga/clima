from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app as app, jsonify
from datetime import datetime
from app.utils.auth import valida_id, valida_id_novo, valida_email_novo, consulta_gestor_cadastrado, usuario_is_gestor
from app.utils.db_consultas import (consulta_dados_gestor, consulta_usuario_id, consulta_usuarios_por_unidade, consulta_fk_dimensao, 
    consulta_todos_gestores, consulta_pesquisa_gestor, consulta_pesquisa_usuario, quantidade_perguntas_pesquisa, quantidade_perguntas_mega_pulso,
    get_perfil_gestor, get_todas_perguntas, consulta_categorias, consulta_fk_categoria_pela_desc_categoria )
from app.utils.db_dml import (processar_diferencas, criar_usuario, processar_diferencas_gestor, criar_gestor, reset_senha_gestor, update_qtd_perguntas,
                              update_perfil_adm_geral, update_perguntas_mega_pulso, update_pergunta, insert_pergunta, select_max_fk_pergunta,
                              insert_categoria, select_max_fk_categoria)
from app.utils.configuracoes import gera_tabela, gera_dados_modal_selecao, verificar_alteracao, gera_tabela_gestores
from flask_babel import _
import json

configuracoes = Blueprint('configuracoes', __name__)
configuracoes_usuario = Blueprint('configuracoes_usuario', __name__)
configuracoes_gestor = Blueprint('configuracoes_gestor', __name__)
configuracoes_salvar_alteracoes = Blueprint('configuracoes_salvar_alteracoes', __name__)
configuracoes_reset_senha = Blueprint('configuracoes_reset_senha', __name__)
configuracoes_pesquisa_gestor = Blueprint('configuracoes_pesquisa_gestor', __name__)
configuracoes_pesquisa = Blueprint('configuracoes_pesquisa', __name__)

@configuracoes.route('/configuracoes', methods = ['GET', 'POST'])
def configuracoes_view():
    perfil = session['perfil']
    if 'logged_in' not in session:
        flash(_("É necessário fazer login primeiro."), "error")
        return redirect(url_for('gestor.gestor_view'))
    return render_template('configuracoes.html', perfil= perfil)

@configuracoes_usuario.route('/configuracoes_usuario', methods = ['GET', 'POST'])
def configuracoes_usuario_view():
    perfil = session['perfil']
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
    return render_template('configuracoes_usuario.html',perfil=perfil, usuarios = dados_usuarios, pagina = pagina, total_paginas = total_paginas, selecao = dados_modal)

@configuracoes_usuario.route('/pesquisar_usuario', methods=['GET'])
def pesquisar_usuario():
    perfil = session['perfil']
    global_id_pesquisa = request.args.get('globalId')
    globalId_gestor = session['id_gestor']
    dados_gestor= consulta_usuario_id(globalId_gestor)
    fk_unidade = dados_gestor[10]
    dados_modal = gera_dados_modal_selecao()

    usuarios = consulta_pesquisa_usuario(global_id_pesquisa, fk_unidade)
    if not usuarios:
        return render_template('configuracoes_usuario.html', perfil = perfil, usuarios = None, pagina = 1, total_paginas = 1, selecao = dados_modal)
    
    # Paginando os resultados
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10
    inicio = (pagina - 1) * por_pagina
    final = inicio + por_pagina
    usuarios_paginados = usuarios[inicio:final]
    dados_usuarios = gera_tabela(usuarios_paginados)
    total_usuarios = len(usuarios)
    total_paginas = (total_usuarios + por_pagina - 1) // por_pagina
    
    # Retorna apenas o HTML da tabela
    return render_template('configuracoes_usuario.html', usuarios = dados_usuarios, pagina = pagina, total_paginas = total_paginas, selecao = dados_modal, modo = 'pesquisa')

@configuracoes_gestor.route('/configuracoes_gestor', methods = ['GET', 'POST'])
def configuracoes_gestor_view():
    perfil = session['perfil']
    if 'logged_in' not in session:
        flash(_("É necessário fazer login primeiro."), "error")
        return redirect(url_for('gestor.gestor_view'))
    
    gestores = consulta_todos_gestores()
    # Página atual e número de itens por página
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10
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

    return render_template('configuracoes_gestor.html', perfil=perfil, gestores = dados_gestores, pagina = pagina, total_paginas = total_paginas, selecao = dados_modal, modo='visualizacao')

@configuracoes_salvar_alteracoes.route('/salvar_alteracoes', methods=['POST'])
def salvar_alteracoes():  
    perfil = session['perfil']
    dados_formulario = request.json
    tipo = dados_formulario.get('tipo')
    globalId_original = dados_formulario.get('globalIdOriginal')
    globalId_novo = dados_formulario.get('globalId')
    #Verifica as informações digitadas
    if not globalId_novo:
        return jsonify({"message":_("Preencha os dados obrigatórios."), "status": "error"})
    id_gestor = dados_formulario.get('id_gestor')
    
    #Verifica se o usuário já existe
    if not globalId_original == globalId_novo:
        if valida_id(globalId_novo):
            return jsonify({"message":_("Já existe usuário com esse ID cadastrado.<br> Procure pelo ID nas configurações de usuários."), "status": "error"})
    #Verifica se o ID é apenas números e se são 8 caracteres
    if not valida_id_novo(globalId_novo):
        return jsonify({"message":_("Os dados informados no campo 'Global ID' não segue algum dos padrões necessários.<br>Tem mais ou menos que 8 números ou não tem apenas números"), "status": "error"})
    #Verifica se o email digitado é válido
    if not valida_email_novo(dados_formulario.get('email')):
        return jsonify({"message":_("Os dados informados no campo 'Email' não segue algum dos padrões necessários.<br>Não está digitado corretamente como @ambev.com ou @ab-inbev.com"), "status": "error"})
    #Verificar se o ID do gestor é o ID de um gestor existente na base de gestores
    if not consulta_dados_gestor(id_gestor):
        return jsonify({"message":_("Os dados informados no campo 'ID Gestor' não existe na base de gestores.<br>Entre em contato com a área de gente da unidade."), "status": "error"})

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
    app.logger.debug(dados)
    #Baseado no ID do formulário, consulta o usuário no banco
    dados_usuario = consulta_usuario_id(globalId_original)
    chaves = ("globalId", "email", "nome", "data_nascimento", "data_ultima_movimentacao", "data_contratacao", "fk_banda", "fk_tipo_cargo", "fk_fte", "fk_cargo","fk_unidade", "fk_area", "fk_subarea", "fk_gestor", "fk_genero")
        
    if tipo == 'edicao':
        #Se o usuário não existir, mensagem de ID Alterado
        if not dados_usuario:
            return jsonify({"message":_("Abra novamente a tela de edição, o ID foi alterado."), "status": "warning"})
        
        dados_alteracao = dados
        dicionario_dados_usuario = dict(zip(chaves, dados_usuario))
        dicionario_dados_alteracao = dict(zip(chaves, dados_alteracao))
        #Verifica se houve alterações nos dados
        if dicionario_dados_usuario == dicionario_dados_alteracao:
            return jsonify({"message": _("Não houve alteração nos dados do usuário"), "status": "warning"})
        else:
            alteracoes = verificar_alteracao(dicionario_dados_usuario, dicionario_dados_alteracao)
            resultado_diferencas = processar_diferencas(alteracoes, globalId_original)
        return resultado_diferencas
    
    if tipo == 'criacao':
        dicionario_dados_criacao = dict(zip(chaves, dados))
        app.logger.debug(dicionario_dados_criacao)
        resultado_criar = criar_usuario(dicionario_dados_criacao)
        return resultado_criar
    
@configuracoes_reset_senha.route('/reset_senha_gestor', methods=['POST'])
def reset_senha():
    dados_reset = request.json  # Recebe os dados JSON do front-end
    globalId = dados_reset.get('globalId')  # Obtém o 'globalId' do JSON
    
    if not globalId:
        return jsonify({"message": "globalId não fornecido", "status": "error"})
    reset_senha_gestor(globalId)  # A função para resetar a senha do gestor
    
    # Retorna uma resposta JSON com status de sucesso
    return jsonify({"message": _("A senha do gestor foi alterada"), "status": "success"})
    
@configuracoes_salvar_alteracoes.route('/salvar_alteracoes_gestor', methods=['POST'])
def salvar_alteracoes_gestor():  
    dados_formulario = request.json    
    tipo = dados_formulario.get('tipo')
    globalId_original = dados_formulario.get('globalIdOriginal')
    globalId_novo = dados_formulario.get('globalId')
    #Verifica as informações digitadas
    if not globalId_novo:
        return jsonify({"message":_("Preencha os dados obrigatórios."), "status": "error"})
    #Verifica se o ID é apenas números e se são 8 caracteres
    if not valida_id_novo(globalId_novo):
        return jsonify({"message":_("Os dados informados no campo 'Global ID' não segue algum dos padrões necessários.<br>Tem mais ou menos que 8 números ou não tem apenas números"), "status": "error"})
    
    #Verifica se o usuário já existe
    if not globalId_original == globalId_novo:
        if not valida_id(globalId_novo):
            return jsonify({"message":_("Não existe usuário cadastrado para o id informado.<br> Crie o usuário antes de cadastrar o gestor."), "status": "error"})
    
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
            return jsonify({"message":_("Abra novamente a tela de edição, o ID foi alterado."), "status": "warning"})
        
        dados_gestor = dados_gestor[1], dados_gestor[2], dados_gestor[5]
        dados_alteracao = dados
        dicionario_dados_gestor= dict(zip(chaves, dados_gestor))
        dicionario_dados_alteracao = dict(zip(chaves, dados_alteracao))
        #Verifica se houve alterações nos dados
        if dicionario_dados_gestor == dicionario_dados_alteracao:
            return jsonify({"message": _("Não houve alteração nos dados do usuário"), "status": "warning"})
        else:
            alteracoes = verificar_alteracao(dicionario_dados_gestor, dicionario_dados_alteracao)
            resultado_diferencas = processar_diferencas_gestor(alteracoes, globalId_original)
        return resultado_diferencas
    
    if tipo == 'criacao':
        gestor_existe = consulta_gestor_cadastrado(globalId_novo)
        if gestor_existe:
            return jsonify({"message": _("Já existe um gestor cadastrado com o ID informado"), "status": "error"})
        
        dicionario_dados_criacao = dict(zip(chaves, dados))
        resultado_criar = criar_gestor(dicionario_dados_criacao)
        return resultado_criar
    
@configuracoes_gestor.route('/pesquisar_gestor', methods=['GET'])
def pesquisar_gestor():
    perfil = session['perfil']
    global_id_pesquisa = request.args.get('globalId')
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10

    gestores = consulta_pesquisa_gestor(global_id_pesquisa)
    if not gestores:
        return render_template('configuracoes_gestor.html',perfil=perfil,  gestores = None, pagina = 1,total_paginas = 1, selecao = None,  modo='pesquisa')
    # Paginando os resultados
    inicio = (pagina - 1) * por_pagina
    final = inicio + por_pagina
    gestores_paginados = gestores[inicio:final]

    # Gera a tabela HTML
    dados_gestores = gera_tabela_gestores(gestores_paginados)
    total_gestores = len(gestores)
    total_paginas = (total_gestores + por_pagina - 1) // por_pagina
    dados_modal = {
        'perfis':['gestor', 'administrador']
    }

    # Retorna apenas o HTML da tabela
    return render_template('configuracoes_gestor.html',perfil=perfil,gestores = dados_gestores, pagina = pagina, total_paginas = total_paginas, selecao = dados_modal, modo='pesquisa')

@configuracoes_pesquisa.route('/configuracoes_pesquisa', methods = ['GET', 'POST'])
def configuracoes_pesquisa_view():
    perfil = session['perfil']
    if 'logged_in' not in session:
        flash(_("É necessário fazer login primeiro."), "error")
        return redirect(url_for('gestor.gestor_view'))
    lang = session.get('lang', 'pt')
    fk_pais = 3
    if lang == 'es':
        fk_pais = 1
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'alterarQtdPerguntas':
            nova_qtd_perguntas = request.form.get('qtdPerguntas')
            if nova_qtd_perguntas:
                update_qtd_perguntas(nova_qtd_perguntas)
                flash(_(f"Quantidade de perguntas do Pulso atualizada com sucesso. A pesquisa agora terá {nova_qtd_perguntas} perguntas"), "success")
            else:
                flash(_("Falha na atualização da quantidade de perguntas"), "error")

            return redirect(url_for('configuracoes_pesquisa.configuracoes_pesquisa_view'))

        elif action =='incluirNovoAdm':
            novo_global_id = request.form.get('user_id')
            if not valida_id(novo_global_id) or not usuario_is_gestor(novo_global_id):
                return redirect(url_for('configuracoes_pesquisa.configuracoes_pesquisa_view'))
            else:
                if get_perfil_gestor(novo_global_id) == 'administrador_geral':
                    flash(_(f'O perfil do ID {novo_global_id} já está como administrador geral'), "warning")
                else:
                    update_perfil_adm_geral(novo_global_id)
                    flash(_('Novo administrador geral cadastrado'), "success")
            return redirect(url_for('configuracoes_pesquisa.configuracoes_pesquisa_view'))
        
        elif action == 'alterarMegaPulso': 
            checkbox_data = request.form.get('checkboxData')
            perguntas_alteradas = json.loads(checkbox_data)
            perguntas_mega_pulso = []
            for str_fk_pergunta, mega_pulso in perguntas_alteradas.items():
                fk_pergunta = int(str_fk_pergunta)
                update_perguntas_mega_pulso(fk_pergunta, mega_pulso)
                if mega_pulso == 1:
                    perguntas_mega_pulso.append(fk_pergunta)

            flash(_(f"Perguntas Mega Pulso atualizadas, as perguntas do Mega Pulso agora são as perguntas: {perguntas_mega_pulso}"), "success")
            redirect(url_for('configuracoes_pesquisa.configuracoes_pesquisa_view'))
        
        elif action == 'alterarPergunta': 
            fk_pergunta = request.form.get('perguntas', 0)
            novo_texto_pt = request.form.get('textoPerguntaPt', None)
            novo_texto_es = request.form.get('textoPerguntaEs', None)
            nome_categoria = request.form.get('categoria', None)
            fk_categoria = None
            if len(novo_texto_pt) == 0:
                novo_texto_pt = None
            if len(novo_texto_es) == 0:
                novo_texto_es = None
            if nome_categoria:
                fk_categoria = consulta_fk_categoria_pela_desc_categoria(nome_categoria)
            
            if novo_texto_pt == None and novo_texto_es == None and fk_categoria == None:
                flash(_(f"Não foi informado nenhum dado para alteração da pergunta número {fk_pergunta}"), "warning")
                return redirect(url_for('configuracoes_pesquisa.configuracoes_pesquisa_view'))
            
            update_pergunta(fk_pergunta, novo_texto_pt, novo_texto_es, fk_categoria)
            flash(_(f"A pergunta de número {fk_pergunta} foi atualizada com sucesso"), "success")
            redirect(url_for('configuracoes_pesquisa.configuracoes_pesquisa_view'))

        elif action == 'incluirPergunta': 
            novo_texto_pt = request.form.get('textoPerguntaPt', None)
            novo_texto_es = request.form.get('textoPerguntaEs', None)
            nome_categoria = request.form.get('categoria', None)
            fk_categoria = None
            if len(novo_texto_pt) == 0:
                novo_texto_pt = None
            if len(novo_texto_es) == 0:
                novo_texto_es = None
            if nome_categoria:
                fk_categoria = consulta_fk_categoria_pela_desc_categoria(nome_categoria, fk_pais)

            insert_pergunta(novo_texto_pt, novo_texto_es, fk_categoria)
            fk_pergunta =  select_max_fk_pergunta()
            app.logger.debug((fk_pergunta, novo_texto_pt, novo_texto_es, fk_categoria))
            flash(_(f"A pergunta:'{novo_texto_pt}'/'{novo_texto_es}' foi criada com sucesso! A pergunta é o número {fk_pergunta}"), "success")
            redirect(url_for('configuracoes_pesquisa.configuracoes_pesquisa_view'))

        elif action == 'incluirCategoria': 
            novo_texto_pt = request.form.get('textoCategoriaPt', None)
            novo_texto_es = request.form.get('textoCategoriaEs', None)
            
            if len(novo_texto_pt) == 0:
                novo_texto_pt = None
            if len(novo_texto_es) == 0:
                novo_texto_es = None

            insert_categoria(novo_texto_pt, novo_texto_es)
            fk_categoria =  select_max_fk_categoria()
            flash(_(f"A Categoria:'{novo_texto_pt}'/'{novo_texto_es}' foi criada com sucesso! A nova categoria é o número: {fk_categoria}"), "success")
            redirect(url_for('configuracoes_pesquisa.configuracoes_pesquisa_view'))

        else:
            flash(_("Nada aconteceu"), "warning")


    dados_qtd_perguntas = {
        "pulso":quantidade_perguntas_pesquisa(),
        "mega_pulso": quantidade_perguntas_mega_pulso()
    }

    perguntas = get_todas_perguntas(fk_pais)
    categorias = consulta_categorias(fk_pais)
    return render_template('configuracoes_pesquisa.html', perfil= perfil, qtd_perguntas = dados_qtd_perguntas, perguntas = perguntas, categorias = categorias)
