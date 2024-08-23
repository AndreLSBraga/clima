from app.utils.db import get_db  # Importando a função get_db
from flask import current_app as app
from datetime import datetime
import uuid

def insert_resposta(dados_usuario, resposta, tipo):
    #Informações do usuário
    data_contratacao = converte_datas(dados_usuario['data_contratacao'])
    data_nascimento = converte_datas(dados_usuario['data_nascimento'])
    data_ultima_movimentacao = converte_datas(dados_usuario['data_ultima_movimentacao'])
    data_hora = dados_usuario['data_hora']
    fk_area = dados_usuario['fk_area']
    fk_banda = dados_usuario['fk_banda']
    fk_cargo = dados_usuario['fk_cargo']
    fk_fte = dados_usuario['fk_fte']
    fk_gestor = dados_usuario['fk_gestor']
    fk_genero = dados_usuario['fk_genero']
    fk_subarea = dados_usuario['fk_subarea']
    fk_tipo_cargo = dados_usuario['fk_tipo_cargo']
    fk_unidade = dados_usuario['fk_unidade']
    #Informações da resposta
    fk_pergunta = resposta['fk_pergunta']
    fk_categoria = resposta['fk_categoria']
    valor_resposta = resposta['resposta']
    
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
        auto_identificacao = resposta['auto_identificacao_sugestao']
        if auto_identificacao == 1:
            globalId = dados_usuario['id_usuario']
        else:
            globalId = None
        texto_sugestao = resposta['sugestao']
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
    
    globalId = dados_usuario['id_usuario']
    data = dados_usuario['data_hora']
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
