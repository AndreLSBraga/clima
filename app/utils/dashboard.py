from flask import current_app as app, flash
import datetime
from app.utils.db_consultas import consulta_fk_dimensao, consulta_desc_categoria_pelo_fk_categoria, consulta_texto_perguntas,consulta_time_por_fk_gestor
from app.utils.db_consultas import consulta_usuario_respondeu, consulta_semana_mes_media_respostas


def processa_respostas_validas(dados_respostas, fk_categoria_filtro=None, fk_pergunta_filtro=None, fk_gestor=None):
    if fk_pergunta_filtro is not None:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: fk_pergunta == fk_pergunta_filtro and resposta >= 0
    elif fk_categoria_filtro is not None:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: fk_categoria == fk_categoria_filtro and resposta >= 0
    else:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: resposta >= 0

    return filtro_respostas

def gera_media_quantidade_datas_respostas(dados_respostas, fk_categoria_filtro=None, fk_pergunta_filtro=None, fk_gestor=None):

    dados_processados = processa_respostas_validas(dados_respostas, fk_categoria_filtro, fk_pergunta_filtro, fk_gestor)

    respostas_validas = [round(float(resposta),1) for fk_pergunta, fk_categoria, resposta, data_hora in dados_respostas if dados_processados(fk_pergunta, fk_categoria, resposta, data_hora)]
    datas_validas = [data_hora.date() for fk_pergunta, fk_categoria, resposta, data_hora in dados_respostas if dados_processados(fk_pergunta, fk_categoria, resposta, data_hora)]

    if respostas_validas:
        media_respostas = round(sum(respostas_validas) / len(respostas_validas), 1)
        size = media_respostas * 10
        quantidade_respostas_validas = len(respostas_validas)
        data_min = min(datas_validas).strftime('%d-%m')
        data_max = max(datas_validas).strftime('%d-%m')
        return media_respostas, size, quantidade_respostas_validas, data_min, data_max
    else:
        return None, None, 0, None, None

def gera_grafico(fk_gestor=None, fk_categoria_filtro=None, fk_pergunta_filtro=None ):
    dados_grafico = consulta_semana_mes_media_respostas(fk_gestor, fk_categoria_filtro, fk_pergunta_filtro)

    if dados_grafico:
        lista_semanas_mes = [f'S: {semana} / Mês: {mes}' for semana, mes, _, _ in dados_grafico]
        lista_media_resposta = [round(float(resposta),1) for _, _, resposta, _ in dados_grafico]
        lista_aderencia = [round(float(aderencia),0) for _,_,_, aderencia in dados_grafico]

        return lista_semanas_mes, lista_media_resposta, lista_aderencia
    else:
        lista_semanas_mes = []
        lista_media_resposta = []
        lista_aderencia = []

def processa_respostas(dados_respostas, fk_categoria_filtro=None, fk_pergunta_filtro=None, fk_gestor=None):

    if fk_pergunta_filtro is not None:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: fk_pergunta == fk_pergunta_filtro and resposta >= 0
    elif fk_categoria_filtro is not None:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: fk_categoria == fk_categoria_filtro and resposta >= 0
    else:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: resposta >= 0

    respostas_validas = [round(float(resposta),1) for fk_pergunta, fk_categoria, resposta, data_hora in dados_respostas if filtro_respostas(fk_pergunta, fk_categoria, resposta, data_hora)]
    datas_validas = [data_hora.date() for fk_pergunta, fk_categoria, resposta, data_hora in dados_respostas if filtro_respostas(fk_pergunta, fk_categoria, resposta, data_hora)]
    quantidade_respostas_validas = len(respostas_validas)

    semanas_mes = [(date.isocalendar()[1], date.month) for date in datas_validas]
    semanas_mes_tratada = list(set(semanas_mes))
    semanas_mes_tratada.sort()
    semanas_mes_grafico = []
    nota_media_semanas_grafico = []
    aderencia_semanal = []

    notas_por_semana = {}
    respostas_por_semana = {}
    usuarios_por_semana = {semana: set() for semana in semanas_mes_tratada}
    
    for resposta, data in zip(respostas_validas, datas_validas):
        semana = data.isocalendar()[1]
        mes = data.month
        chave = (semana, mes)
        
        if chave not in notas_por_semana:
            notas_por_semana[chave] = {'soma': 0, 'contagem': 0}
            respostas_por_semana[chave] = 0

        notas_por_semana[chave]['soma'] += resposta
        notas_por_semana[chave]['contagem'] += 1

    if fk_gestor is not None:
        # Obter IDs de usuários a partir de fk_gestor
        globalId_time = consulta_time_por_fk_gestor(fk_gestor)
        if len(globalId_time) < 3:
            return None, None, 0, None, None, [], [], []
        globalId_time = {id_tuple[0] for id_tuple in globalId_time}
        dados_usuarios_responderam = consulta_usuario_respondeu()
        if not dados_usuarios_responderam:
            return None, None, 0, None, None, [], [], []
        
        usuarios_responderam = [user_id for user_id, _ in dados_usuarios_responderam]
        datas_respostas = [data_resposta for _, data_resposta in dados_usuarios_responderam]

        # Contar respostas dos usuários por semana
        for user_id, data_resposta in dados_usuarios_responderam:
            semana = data_resposta.isocalendar()[1]
            mes = data_resposta.month
            chave = (semana, mes)
            
            if user_id in globalId_time:
                if chave in usuarios_por_semana:
                    usuarios_por_semana[chave].add(user_id)

        # Calculando média por semana, aderência e formatando semanas_mes_grafico
    
    media_por_semana = {}
    for semana in semanas_mes_tratada:
        num_semana, mes = semana
        chave = (num_semana, mes)
        
        if chave in notas_por_semana:
            soma = notas_por_semana[chave]['soma']
            contagem = notas_por_semana[chave]['contagem']
            media_por_semana[chave] = round(soma / contagem, 1)

            nota_media_semanas_grafico.append(media_por_semana[chave])
            semanas_mes_grafico.append(f'S{num_semana} / Mês:{mes}')
            
            if fk_gestor:
                # Calcular a aderência
                total_usuarios_semana = len(globalId_time)
                respostas_semana = len(usuarios_por_semana[chave])
                aderencia = round((respostas_semana / total_usuarios_semana)*100, 1) if total_usuarios_semana > 0 else 0
                aderencia_semanal.append(aderencia)
        else:
            nota_media_semanas_grafico.append(0)
            aderencia_semanal.append(0)

    # Calculando média geral, quantidade, data mínima e máxima
    if respostas_validas:
        media_respostas = round(sum(respostas_validas) / len(respostas_validas), 1)
        size = media_respostas * 10
        data_min = min(datas_validas).strftime('%d-%m')
        data_max = max(datas_validas).strftime('%d-%m')

        return media_respostas, size, quantidade_respostas_validas, data_min, data_max, semanas_mes_grafico, nota_media_semanas_grafico, aderencia_semanal
    else:
        return None, None, 0, None, None, [], [], []
   
def gera_cards(dados_respostas):
    # Consulta as categorias
    categorias_consulta = consulta_fk_dimensao('categorias', 'fk_categoria')
    fk_categorias = [categoria[0] for categoria in categorias_consulta]
    fk_categorias = fk_categorias[:10]
    cards = []

    # Itera sobre cada categoria
    for categoria in fk_categorias:

        descricao_categoria = consulta_desc_categoria_pelo_fk_categoria(categoria)
        if not dados_respostas:
            card = {
            'id': categoria,
            'title': descricao_categoria,  # O título da categoria
            'value': None ,  # Defina o valor como 0 se não houver média
            'size': 0,  # Defina o tamanho como 0 se não houver média
            'qtd_respostas': 0,
            'data_min': None,
            'data_max': None
            }
            cards.append(card)
        else:
            # Processa as respostas para a categoria atual
            media_respostas, size, quantidade_respostas, data_min, data_max = gera_media_quantidade_datas_respostas(dados_respostas, categoria)
            card = {
                'id': categoria,
                'title': descricao_categoria,  
                'value': media_respostas if media_respostas is not None else None, 
                'size': size if media_respostas is not None else None,
                'qtd_respostas': quantidade_respostas,
                'data_min': data_min if data_min else None,
                'data_max': data_max if data_max else None
            }
            cards.append(card)
    return cards

def gera_cards_detalhe(dados_respostas, fk_gestor,  fk_categoria_detalhe):
    # Consulta as categorias
    perguntas_consulta = consulta_fk_dimensao('perguntas', 'fk_pergunta', 'fk_categoria', fk_categoria_detalhe)
    fk_perguntas = [categoria[0] for categoria in perguntas_consulta]
    cards = []
    # Itera sobre cada categoria
    for pergunta in fk_perguntas:

        descricao_pergunta = consulta_texto_perguntas(pergunta)
        if not dados_respostas:
            card = {
                'id': pergunta,
                'title': descricao_pergunta,  # O título da categoria
                'value': None,  # Defina o valor como 0 se não houver média
                'size': 0,  # Defina o tamanho como 0 se não houver média
                'qtd_respostas': 0,
                'data_min': None,
                'data_max': None,
                'semanas':  [],
                'notas': []
            }
            cards.append(card)
        else:
            # Processa as respostas para a categoria atual
            media_respostas, size, quantidade_respostas, data_min, data_max = gera_media_quantidade_datas_respostas(dados_respostas, None, pergunta)
            dados_grafico = gera_grafico(fk_gestor, None, pergunta)
            app.logger.debug(pergunta, quantidade_respostas, media_respostas)
            if quantidade_respostas < 3:
                card = {
                    'id': pergunta,
                    'title': descricao_pergunta,  # O título da categoria
                    'value': None,  # Defina o valor como 0 se não houver média
                    'size': 0,  # Defina o tamanho como 0 se não houver média
                    'qtd_respostas': quantidade_respostas,
                    'data_min': None,
                    'data_max': None,
                    'semanas':  [],
                    'notas': []
                }
                cards.append(card)
            else:
                if dados_grafico:
                    semanas = dados_grafico[0]
                    notas_semana = dados_grafico[1]
                else:
                    semanas = []
                    notas_semana = []

                app.logger.debug(f'Pergunta: {pergunta}, dados: {gera_media_quantidade_datas_respostas(dados_respostas, None, pergunta)}, dados grafico: {dados_grafico}')

                # Se as respostas forem válidas, cria um card
                card = {
                    'id': pergunta,
                    'title': descricao_pergunta,  # O título da categoria
                    'value': media_respostas if media_respostas is not None else None,  # Defina o valor como 0 se não houver média
                    'size': size if media_respostas is not None else None,  # Defina o tamanho como 0 se não houver média
                    'qtd_respostas': quantidade_respostas,
                    'data_min': data_min if data_min else None,
                    'data_max': data_max if data_max else None,
                    'semanas':  semanas,
                    'notas': notas_semana
                }
                cards.append(card)

    return cards