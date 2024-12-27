from app.utils.db import get_db  # Importando a função get_db
from flask import current_app as app, jsonify
from datetime import datetime
import uuid
from config import SENHA_PRIMEIRO_ACESSO

def insert_resposta(dados_usuario, resposta, tipo):
    #Informações do usuário
    data_contratacao = converte_datas(dados_usuario['data_contratacao'])
    data_nascimento = converte_datas(dados_usuario['data_nascimento'])
    data_ultima_movimentacao = converte_datas(dados_usuario['data_ultima_movimentacao'])
    data_hora = dados_usuario.get('data_hora', None)
    fk_area = dados_usuario.get('fk_area', None)
    fk_banda = dados_usuario.get('fk_banda', None)
    fk_cargo = dados_usuario.get('fk_cargo', None)
    fk_fte = dados_usuario.get('fk_fte', None)
    fk_gestor = dados_usuario.get('fk_gestor', None)
    fk_genero = dados_usuario.get('fk_genero', None)
    fk_subarea = dados_usuario.get('fk_subarea', None)
    fk_tipo_cargo = dados_usuario.get('fk_tipo_cargo', None)
    fk_unidade = dados_usuario.get('fk_unidade', None)
    #Informações da resposta
    fk_pergunta = resposta.get('fk_pergunta',None)
    fk_categoria = resposta.get('fk_categoria', None)
    valor_resposta = resposta.get('resposta', None)
    
    db = get_db()
    cursor = db.cursor()

    if tipo == 'resposta':
        cursor.execute(
            '''
            INSERT INTO respostas 
                (
                    data_hora, data_contratacao, data_nascimento, data_ultima_movimentacao,
                    fk_area, fk_banda, fk_cargo, fk_fte, fk_gestor, fk_genero, fk_subarea,
                    fk_tipo_cargo, fk_unidade, fk_pergunta, fk_categoria, resposta 
                )
            VALUES 
                (
                    %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ''',
                (
                    data_hora, data_contratacao, data_nascimento, data_ultima_movimentacao,
                    fk_area, fk_banda, fk_cargo, fk_fte, fk_gestor, fk_genero, fk_subarea,
                    fk_tipo_cargo, fk_unidade, fk_pergunta, fk_categoria, valor_resposta 
                )
            )
        db.commit()

    elif tipo == 'sugestao':
        auto_identificacao = resposta.get('auto_identificacao_sugestao', None)
        if auto_identificacao == 1:
            globalId = dados_usuario.get('id_usuario', None)
        else:
            globalId = None
        texto_sugestao = resposta.get('sugestao', None)
        id_sugestao = uuid.uuid4().hex
        cursor.execute(
            '''
            INSERT INTO sugestoes 
                (
                    id_sugestao, data_hora, data_contratacao, data_nascimento, data_ultima_movimentacao,
                    fk_area, fk_banda, fk_cargo, fk_fte, fk_gestor, fk_genero, fk_subarea,
                    fk_tipo_cargo, fk_unidade, fk_pergunta, fk_categoria, texto_sugestao, respondido,
                    auto_identificacao, globalId, resposta
                )
            VALUES 
                (
                    %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
                ''',
                (
                    id_sugestao, data_hora, data_contratacao, data_nascimento, data_ultima_movimentacao,
                    fk_area, fk_banda, fk_cargo, fk_fte, fk_gestor, fk_genero, fk_subarea,
                    fk_tipo_cargo, fk_unidade, fk_pergunta, fk_categoria, texto_sugestao, 0,
                    auto_identificacao, globalId, valor_resposta
                )
            )
        db.commit()
        cursor.close()

def insert_usuario_respondeu(dados_usuario):
    
    globalId = dados_usuario.get('id_usuario', None)
    data = dados_usuario.get('data_hora', None)
    data_formatada = data.date()
    
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
            '''
            INSERT INTO usuario_respondeu
                (
                    globalId, data 
                )
            VALUES 
                (
                    %s, %s
                )
                ''',
                (
                    globalId, data_formatada
                )
            )
    
    db.commit()
    cursor.close()

def converte_datas(data_str):
    formato = '%a, %d %b %Y %H:%M:%S GMT'
    date_datetime = datetime.strptime(data_str, formato)
    date_data = date_datetime.date()

    return date_data

def update_senha_gestor(senha, fk_gestor):
    db = get_db()
    cursor = db.cursor()
    #Atualiza senha nova no banco
    cursor.execute('UPDATE gestores SET senha = %s, primeiro_acesso = 1 WHERE fk_gestor = %s',(senha, fk_gestor))
    db.commit()
    cursor.close()

def reset_senha_gestor(globalId):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE gestores set senha =%s, primeiro_acesso = %s WHERE globalId = %s',(SENHA_PRIMEIRO_ACESSO, None, globalId))
    db.commit()
    cursor.close()

def processar_diferencas(diferencas, global_id):
    resultados = {
        "success": [],
        "error": []
    }
    status_global = "success"

    # Mapeia as chaves para suas funções de atualização correspondentes
    acoes = {
        "globalId": lambda dados: atualizar_usuario('globalId', dados, global_id),
        "email": lambda dados: atualizar_usuario('email', dados, global_id),
        "nome": lambda dados: atualizar_usuario('nome', dados, global_id),
        "data_nascimento": lambda dados: atualizar_usuario('data_nascimento', dados, global_id),
        "data_ultima_movimentacao": lambda dados: atualizar_usuario('data_ultima_movimentacao', dados, global_id),
        "data_contratacao": lambda dados: atualizar_usuario('data_contratacao', dados, global_id),
        "fk_banda": lambda dados: atualizar_usuario('fk_banda', dados, global_id),
        "fk_tipo_cargo": lambda dados: atualizar_usuario('fk_tipo_cargo', dados, global_id),
        "fk_fte": lambda dados: atualizar_usuario('fk_fte', dados, global_id),
        "fk_cargo": lambda dados: atualizar_usuario('fk_cargo', dados, global_id),
        "fk_unidade": lambda dados: atualizar_usuario('fk_unidade', dados, global_id),
        "fk_area": lambda dados: atualizar_usuario('fk_area', dados, global_id),
        "fk_subarea": lambda dados: atualizar_usuario('fk_subarea', dados, global_id),
        "fk_gestor": lambda dados: atualizar_usuario('fk_gestor', dados, global_id),
        "fk_genero": lambda dados: atualizar_usuario('fk_genero', dados, global_id)
    }

    for chave, dados in diferencas.items():
        if chave in acoes:
            resultado = acoes[chave](dados)
            if resultado["status"] == "success":
                resultados["success"].append(chave)
            else:
                resultados["error"].append(chave)
                status_global = "error"  # Atualiza o status global se houver erro

            if chave == 'globalId':
                # Atualiza a variável global_id após a alteração do globalId
                global_id = dados.get('novo')

    # Construir a mensagem final com base nos resultados
    if status_global == "success":
        mensagem_final = f"Os campos '{', '.join(resultados['success'])}' foram alterados com sucesso."
    else:
        campos_sucesso = ", ".join(resultados['success'])
        campos_erro = ", ".join(resultados['error'])
        mensagem_final = f"Os campos {campos_sucesso} foram alterados com sucesso. " \
                         f"Ocorreu um erro nos campos: {campos_erro}."

    return jsonify({
        "message": mensagem_final,
        "status": status_global
    })

def processar_diferencas_gestor(diferencas, global_id):
    resultados = {
        "success": [],
        "error": []
    }
    status_global = "success"

    # Mapeia as chaves para suas funções de atualização correspondentes
    acoes = {
        "globalId": lambda dados: atualizar_gestor('globalId', dados, global_id),
        "nome": lambda dados: atualizar_gestor('gestor_nome', dados, global_id),
        "perfil": lambda dados: atualizar_gestor('perfil', dados, global_id)
    }
    for chave, dados in diferencas.items():
        if chave in acoes:
            resultado = acoes[chave](dados)
            if resultado["status"] == "success":
                resultados["success"].append(chave)
            else:
                resultados["error"].append(chave)
                status_global = "error"  # Atualiza o status global se houver erro

            if chave == 'globalId':
                # Atualiza a variável global_id após a alteração do globalId
                global_id = dados.get('novo')

    # Construir a mensagem final com base nos resultados
    if status_global == "success":
        mensagem_final = f"Os campos '{', '.join(resultados['success'])}' foram alterados com sucesso."
    else:
        campos_sucesso = ", ".join(resultados['success'])
        campos_erro = ", ".join(resultados['error'])
        mensagem_final = f"Os campos {campos_sucesso} foram alterados com sucesso. " \
                         f"Ocorreu um erro nos campos: {campos_erro}."

    return jsonify({
        "message": mensagem_final,
        "status": status_global
    })

def atualizar_usuario(coluna, dados_alteracao, global_id):
    novo = dados_alteracao.get('novo')
    db = get_db()
    cursor = db.cursor()
    query = f'''
            UPDATE usuarios SET
                {coluna} = %s
            WHERE 
                globalId = %s
        '''
    cursor.execute(query, (novo, global_id))
    # Verificar o número de linhas afetadas
    if cursor.rowcount > 0:
        status = "success"
        mensagem =  f"Alteração do campo '{coluna}' realizada com sucesso."
    else:
        status = "warning"
        mensagem = f"Nenhuma alteração foi feita no campo '{coluna}'."

    db.commit()
    cursor.close()
    return {
        "status": status,
        "message": mensagem
    }

def atualizar_gestor(coluna, dados_alteracao, global_id):
    
    novo = dados_alteracao.get('novo')
    db = get_db()
    cursor = db.cursor()
    query = f'''
            UPDATE gestores SET
                {coluna} = %s
            WHERE 
                globalId = %s
        '''
    cursor.execute(query, (novo, global_id))
    # Verificar o número de linhas afetadas
    if cursor.rowcount > 0:
        status = "success"
        mensagem =  f"Alteração do campo '{coluna}' realizada com sucesso."
    else:
        status = "warning"
        mensagem = f"Nenhuma alteração foi feita no campo '{coluna}'."

    db.commit()
    cursor.close()
    return {
        "status": status,
        "message": mensagem
    }

def criar_usuario(dados_usuario):

    #Variáveis dos dados usuario
    global_id = dados_usuario.get('globalId')
    email = dados_usuario.get('email')
    nome = dados_usuario.get('nome')
    data_nascimento = dados_usuario.get('data_nascimento')
    data_ultima_movimentacao = dados_usuario.get('data_ultima_movimentacao')
    data_contratacao = dados_usuario.get('data_contratacao')
    fk_banda = dados_usuario.get('fk_banda')
    fk_tipo_cargo = dados_usuario.get('fk_tipo_cargo')
    fk_fte = dados_usuario.get('fk_fte')
    fk_cargo = dados_usuario.get('fk_cargo')
    fk_unidade = dados_usuario.get('fk_unidade')
    fk_area = dados_usuario.get('fk_area')
    fk_subarea = dados_usuario.get('fk_subarea')
    fk_gestor = dados_usuario.get('fk_gestor')
    fk_genero = dados_usuario.get('fk_genero')

    db = get_db()
    cursor = db.cursor()
    query = '''
            INSERT into usuarios 
            (
                globalId, email, nome, data_nascimento, data_ultima_movimentacao, data_contratacao,
                fk_banda, fk_tipo_cargo, fk_fte, fk_cargo, fk_unidade, fk_area,
                fk_subarea, fk_gestor, fk_genero
            )
            values
            (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        '''
    cursor.execute(query, (global_id, email, nome, data_nascimento, data_ultima_movimentacao, data_contratacao, 
                           fk_banda, fk_tipo_cargo, fk_fte, fk_cargo, fk_unidade, fk_area,
                           fk_subarea, fk_gestor, fk_genero
                           ))
    
    if cursor.rowcount > 0:
        db.commit()
        cursor.close()
        return {
            "status": "success",
            "message": "Usuário criado com sucesso."
        }
    else:
        db.rollback()
        cursor.close()
        return {
            "status": "error",
            "message": "Falha ao criar o usuário."
        }

def criar_gestor(dados_gestor):
    #Variáveis dos dados usuario
    global_id = dados_gestor.get('globalId')
    nome = dados_gestor.get('nome')
    perfil = dados_gestor.get('perfil')

    db = get_db()
    cursor = db.cursor()
    query = '''
            INSERT into gestores 
            (
                globalId, gestor_nome, perfil
            )
            values
            (
                %s, %s, %s
            )
        '''
    cursor.execute(query, (global_id, nome, perfil))
    
    if cursor.rowcount > 0:
        db.commit()
        cursor.close()
        return {
            "status": "success",
            "message": "Usuário criado com sucesso."
        }
    else:
        db.rollback()
        cursor.close()
        return {
            "status": "error",
            "message": "Falha ao criar o usuário."
        }

def update_qtd_perguntas(qtd_perguntas):
    db = get_db()
    cursor = db.cursor()
    query = 'UPDATE qtd_perguntas_pesquisa SET qtd_perguntas = %s'
    cursor.execute(query, (qtd_perguntas,))
    db.commit()
    cursor.close