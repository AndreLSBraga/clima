from flask import current_app as app, flash
from datetime import datetime
from app.utils.db_consultas import consulta_fk_dimensao, consulta_desc_categoria_pelo_fk_categoria, consulta_texto_perguntas

def processa_respostas(dados_respostas, fk_categoria_filtro=None, fk_pergunta_filtro=None):
    if dados_respostas == None:
        return None, None, 0, None, None
    
    if fk_pergunta_filtro is not None:
        respostas_validas = [float(resposta) for _, fk_pergunta, resposta, _ in dados_respostas if fk_pergunta == fk_pergunta_filtro and resposta > 0]
        datas_validas = [data_hora.date() for _, fk_pergunta, resposta, data_hora in dados_respostas if fk_pergunta == fk_pergunta_filtro and resposta > 0]

    elif fk_categoria_filtro is not None:
        respostas_validas = [float(resposta) for fk_categoria, _, resposta, _ in dados_respostas if fk_categoria == fk_categoria_filtro and resposta > 0]
        datas_validas = [data_hora.date() for fk_categoria, _, resposta, data_hora in dados_respostas if fk_categoria == fk_categoria_filtro and resposta > 0]

    else:
        respostas_validas = [float(resposta) for _, _, resposta, _ in dados_respostas if resposta > 0]
        datas_validas = [data_hora.date() for _, _, _, data_hora in dados_respostas]

    # Calculando média, quantidade, data mínima e máxima
    if respostas_validas:
        media_respostas = round(sum(respostas_validas) / len(respostas_validas), 1)
        size = media_respostas * 10
        quantidade_respostas = len(respostas_validas)
        data_min = min(datas_validas).strftime('%d-%m')
        data_max = max(datas_validas).strftime('%d-%m')

        return media_respostas, size, quantidade_respostas, data_min, data_max
    else:
        return None, None, 0, None, None
    
def gera_cards(dados_respostas):
    # Consulta as categorias
    categorias_consulta = consulta_fk_dimensao('categorias', 'fk_categoria')
    fk_categorias = [categoria[0] for categoria in categorias_consulta]
    cards = []

    # Itera sobre cada categoria
    for categoria in fk_categorias:
        # Processa as respostas para a categoria atual
        media_respostas, size, quantidade_respostas, data_min, data_max = processa_respostas(dados_respostas, categoria)
        descricao_categoria = consulta_desc_categoria_pelo_fk_categoria(categoria)

        # Se as respostas forem válidas, cria um card
        card = {
            'id': categoria,
            'title': descricao_categoria,  # O título da categoria
            'value': media_respostas if media_respostas is not None else None,  # Defina o valor como 0 se não houver média
            'size': size if media_respostas is not None else None,  # Defina o tamanho como 0 se não houver média
            'qtd_respostas': quantidade_respostas,
            'data_min': data_min if data_min else None,
            'data_max': data_max if data_max else None
        }
        cards.append(card)

    return cards

def gera_cards_detalhe(dados_respostas, fk_categoria_detalhe):
    # Consulta as categorias
    perguntas_consulta = consulta_fk_dimensao('perguntas', 'fk_pergunta', 'fk_categoria', fk_categoria_detalhe)
    app.logger.debug(perguntas_consulta)
    fk_perguntas = [categoria[0] for categoria in perguntas_consulta]
    cards = []

    # Itera sobre cada categoria
    for pergunta in fk_perguntas:
        # Processa as respostas para a categoria atual
        media_respostas, size, quantidade_respostas, data_min, data_max = processa_respostas(dados_respostas, pergunta)
        descricao_pergunta = consulta_texto_perguntas(pergunta)

        # Se as respostas forem válidas, cria um card
        card = {
            'id': pergunta,
            'title': descricao_pergunta,  # O título da categoria
            'value': media_respostas if media_respostas is not None else 0,  # Defina o valor como 0 se não houver média
            'size': size if media_respostas is not None else None,  # Defina o tamanho como 0 se não houver média
            'qtd_respostas': quantidade_respostas,
            'data_min': data_min if data_min else None,
            'data_max': data_max if data_max else None
        }
        cards.append(card)

    return cards