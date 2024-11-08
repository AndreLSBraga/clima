from flask import current_app as app, flash
import datetime
from app.utils.db_consultas import consulta_fk_dimensao, consulta_desc_categoria_pelo_fk_categoria, consulta_texto_perguntas,consulta_time_por_fk_gestor
from app.utils.db_consultas import consulta_usuario_respondeu, consulta_semana_mes_media_respostas, consulta_resumo_respostas_categoria_gestor
from app.utils.db_notas_consultas import consulta_promotores_categorias, consulta_promotores_perguntas, consulta_promotores_grafico_geral, consulta_promotores_grafico_pergunta, consulta_promotores_grafico_categoria

def processa_respostas_validas(dados_respostas, fk_categoria_filtro=None, fk_pergunta_filtro=None, fk_gestor=None):
    if fk_pergunta_filtro is not None:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: fk_pergunta == fk_pergunta_filtro and resposta >= 0
    elif fk_categoria_filtro is not None:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: fk_categoria == fk_categoria_filtro and resposta >= 0
    else:
        filtro_respostas = lambda fk_pergunta, fk_categoria, resposta, data_hora: resposta >= 0

    return filtro_respostas

def gera_informacoes_respostas(dados_respostas, fk_categoria_filtro=None, fk_pergunta_filtro=None, fk_gestor=None):
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

def gera_grafico(datas_min_max, fk_gestor=None, fk_categoria_filtro=None, fk_pergunta_filtro=None ):

    dados_grafico = consulta_promotores_grafico_geral(datas_min_max, fk_gestor)
    
    if not dados_grafico:
        return None,None,None
    lista_pesquisa = [pesquisa for pesquisa, _, _, _ in dados_grafico]
    lista_promotores = [
        round(float(promotores), 1) if respondentes_unicos >= 3 else None
        for _, respondentes_unicos, promotores, _ in dados_grafico
    ]
    lista_aderencia = [
        round(float(aderencia),0) if aderencia else None
        for _, _, _, aderencia in dados_grafico]

    return lista_pesquisa, lista_promotores, lista_aderencia

def gera_grafico_detalhes(dados, fk_pergunta_filtro):

    intervalos = []
    notas = []
    # Filtra apenas os dados que correspondem ao fk_pergunta desejado
    for intervalo, fk_pergunta, qtd_respondentes_unicos, percentual_promotores in dados:
        if fk_pergunta == fk_pergunta_filtro:
            intervalos.append(intervalo)
            # Define a nota como None se qtd_respondentes for menor que 3, caso contrário usa o valor
            if qtd_respondentes_unicos < 3:
                notas.append(None)
            else:
                notas.append(float(percentual_promotores))  # Converte para float para simplificar

    return intervalos, notas

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

def gera_main_cards(nota):
    if nota[2] < 3:
        return {
                'valor': None,
                'qtd_respostas': nota[3],
                'data_min': nota[4],
                'data_max': nota[5],
        }
    else:
        return {
                'valor': nota[0],
                'qtd_respostas': nota[3],
                'data_min': nota[4],
                'data_max': nota[5],
        }

def gera_cards(datas_min_max,fk_gestor):
    # Consulta promotores por categoria
    dados_categorias = consulta_promotores_categorias(datas_min_max, fk_gestor)
    cards = []
    # Itera sobre cada categoria
    for categoria in dados_categorias:
        
        fk_categoria = categoria[0]
        descricao_categoria = categoria[1]
        perc_promotores = categoria[2]
        qtd_promotores = categoria[3]
        qtd_respostas_unicas = categoria[4]
        qtd_respostas_totais = categoria[5]
        data_min = categoria[6]
        data_max = categoria[7]
        if qtd_respostas_unicas < 3:
            card = {
            'id': fk_categoria,
            'title': descricao_categoria,  # O título da categoria
            'value': None ,  # Defina o valor como 0 se não houver média
            'size': 0,  # Defina o tamanho como 0 se não houver média
            'qtd_respostas': qtd_respostas_totais,
            'data_min': data_min,
            'data_max': data_max
            }
            cards.append(card)
        else:
            card = {
            'id': fk_categoria,
            'title': descricao_categoria,  # O título da categoria
            'value': perc_promotores ,  # Defina o valor como 0 se não houver média
            'size': perc_promotores,  # Defina o tamanho como 0 se não houver média
            'qtd_respostas': qtd_respostas_totais,
            'data_min': data_min,
            'data_max': data_max
            }
            cards.append(card)
    return cards

def gera_cards_detalhe(datas_min_max, fk_gestor,  fk_categoria_detalhe):
    cards = []
    lista_semanas = []
    #Traz os dados do gestor
    dados_respostas = consulta_promotores_perguntas(datas_min_max, fk_gestor, fk_categoria_detalhe)
    
    dados_grafico = consulta_promotores_grafico_pergunta(datas_min_max, fk_gestor, fk_categoria_detalhe)
    
    # Itera sobre cada categoria
    for pergunta in dados_respostas:
        fk_pergunta = pergunta[0]
        descricao_pergunta = pergunta[1]
        perc_promotores = pergunta[2]
        qtd_promotores = pergunta[3]
        qtd_respostas_unicas = pergunta[4]
        qtd_respostas_totais = pergunta[5]
        data_min = pergunta[6]
        data_max = pergunta[7]
        dados_grafico_pergunta = gera_grafico_detalhes(dados_grafico, fk_pergunta)
        semanas = dados_grafico_pergunta[0]
        notas = dados_grafico_pergunta[1]
        if qtd_respostas_unicas < 3:
            card = {
            'id': fk_pergunta,
            'title': descricao_pergunta,  
            'value': None , 
            'size': 0,
            'qtd_respostas': qtd_respostas_totais,
            'data_min': data_min,
            'data_max': data_max,
            'semanas':[],
            'notas':[]
            }
            cards.append(card)
        else:
            card = {
            'id': fk_pergunta,
            'title': descricao_pergunta,  # O título da categoria
            'value': perc_promotores ,  # Defina o valor como 0 se não houver média
            'size': perc_promotores, 
            'qtd_respostas': qtd_respostas_totais,
            'data_min': data_min,
            'data_max': data_max,
            'semanas': semanas,
            'notas': notas
            }
            cards.append(card)
    return cards

def gera_cards_categoria(datas_min_max, fk_gestor, fk_categoria):

    dados_categoria = consulta_promotores_grafico_categoria(datas_min_max, fk_gestor, fk_categoria)
    intervalos = []
    notas = []
    # Filtra apenas os dados que correspondem ao fk_pergunta desejado
    for intervalo, qtd_respondentes_unicos, percentual_promotores in dados_categoria:
        intervalos.append(intervalo)
        # Define a nota como None se qtd_respondentes for menor que 3, caso contrário usa o valor
        if qtd_respondentes_unicos < 3:
            notas.append(None)
        else:
            notas.append(float(percentual_promotores))  # Converte para float para simplificar    
    
    return {
        'id_categoria': fk_categoria,
        'descricao': consulta_desc_categoria_pelo_fk_categoria(fk_categoria),
        'semanas': intervalos,
        'notas':  notas
    }

def processa_sugestoes(base_sugestoes):
    sugestoes = []
    for sugestao in base_sugestoes:
        id_sugestao = sugestao[0]
        data_sugestao = sugestao[1].strftime('%d/%m/%y')
        fk_categoria = sugestao[2]
        fk_pergunta = sugestao[3]
        texto_sugestao = sugestao[4]
        texto_categoria = None
        texto_pergunta = None
        if fk_categoria:
            texto_categoria = consulta_desc_categoria_pelo_fk_categoria(fk_categoria)
        
        if fk_pergunta:
            texto_pergunta = consulta_texto_perguntas(fk_pergunta)
        
        sugestao_tuple = {
            'id_sugestao': id_sugestao,
            'data_sugestao': data_sugestao,
            'texto_categoria': texto_categoria,
            'texto_pergunta': texto_pergunta,
            'texto_sugestao': texto_sugestao
        }
        sugestoes.append(sugestao_tuple)

    return sugestoes

def gera_card_gestor_liderado(dados_gestor, indice):
    fk_gestor = dados_gestor['fk_gestor']
    nome_gestor = dados_gestor['nome_liderado']
    respostas_categoria = consulta_resumo_respostas_categoria_gestor(fk_gestor)
    card = {
        'id': indice,
        'nome_gestor': nome_gestor,
        'qtd_respostas': 100,  # O título da categoria
        'qtd_sugestoes': 100,
        'perc_promotores': 50,
        'categorias': respostas_categoria
    }

    return card