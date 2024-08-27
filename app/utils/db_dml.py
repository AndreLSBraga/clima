from app.utils.db import get_db  # Importando a função get_db
from flask import current_app as app
from datetime import datetime
import uuid

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
                    auto_identificacao, globalId
                )
            VALUES 
                (
                    %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s
                )
                ''',
                (
                    id_sugestao, data_hora, data_contratacao, data_nascimento, data_ultima_movimentacao,
                    fk_area, fk_banda, fk_cargo, fk_fte, fk_gestor, fk_genero, fk_subarea,
                    fk_tipo_cargo, fk_unidade, fk_pergunta, fk_categoria, texto_sugestao, 0,
                    auto_identificacao, globalId
                )
            )
        db.commit()
        cursor.close()

def insert_usuario_respondeu(dados_usuario):
    
    globalId = dados_usuario.get('id_usuario', None)
    data = dados_usuario.get('data_hora', None)
    data_formatada = data.date()
    app.logger.debug(globalId, data, data_formatada)
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