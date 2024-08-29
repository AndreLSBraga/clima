from app.utils.db import get_db  # Importando a função get_db
from app.utils.db_consultas import consulta_tabela_dimensao
from flask import current_app as app
from datetime import datetime

def gera_tabela(usuarios):
    tabela = []
    for usuario in usuarios:
        dados_usuario = {
            "globalId": usuario[0],
            "email": usuario[1],
            "nome": usuario[2],
            "data_nascimento": usuario[3].strftime('%Y-%m-%d'),
            "data_ultima_movimentacao": usuario[4].strftime('%Y-%m-%d'),
            "data_contratacao": usuario[5].strftime('%Y-%m-%d'),
            "banda": consulta_tabela_dimensao('bandas', 'fk_banda', usuario[6])[1],
            "tipo_cargo": consulta_tabela_dimensao('tipo_cargos', 'fk_tipo_cargo', usuario[7])[1],
            "fte": consulta_tabela_dimensao('ftes', 'fk_fte', usuario[8])[1],
            "cargo": consulta_tabela_dimensao('cargos', 'fk_cargo', usuario[9])[1],
            "unidade": consulta_tabela_dimensao('unidades', 'fk_unidade', usuario[10])[3],
            "area": consulta_tabela_dimensao('areas', 'fk_area', usuario[11])[1],
            "subarea": consulta_tabela_dimensao('subareas', 'fk_subarea', usuario[12])[1],
            "id_gestor": consulta_tabela_dimensao('gestores', 'fk_gestor', usuario[13])[1],
            "genero": consulta_tabela_dimensao('generos', 'fk_genero', usuario[14])[1],
        }
        
        tabela.append(dados_usuario)

    return tabela

def gera_dados_modal_selecao():

    bandas_lista = consulta_tabela_dimensao('bandas'),
    tipo_cargos_lista = consulta_tabela_dimensao('tipo_cargos'),
    ftes_lista = consulta_tabela_dimensao('ftes'),
    cargos_lista = consulta_tabela_dimensao('cargos'),
    unidades_lista = consulta_tabela_dimensao('unidades'),
    areas_lista = consulta_tabela_dimensao('areas'),
    subareas_lista = consulta_tabela_dimensao('subareas'),
    generos_lista = consulta_tabela_dimensao('generos')
    
    dados = [{
        "bandas": consulta_lista(bandas_lista,1),
        "tipo_cargos": consulta_lista(tipo_cargos_lista,1),
        "ftes": consulta_lista(ftes_lista,1),
        "cargos": consulta_lista(cargos_lista,1),
        "unidades": consulta_lista(unidades_lista,3),
        "areas": consulta_lista(areas_lista,1),
        "subareas": consulta_lista(subareas_lista,1),
        "generos": consulta_lista(generos_lista,1)
    }]
    return dados

def consulta_lista(lista, num_item):
    resultado = []
    if isinstance(lista[0], list):
        # Itera sobre a lista de tuplas
        for item in lista[0]:
            if len(item) > num_item:
                resultado.append(item[num_item])
    else:
        # Itera diretamente sobre a lista de tuplas
        for item in lista:
            if len(item) > num_item:
                resultado.append(item[num_item])
    return resultado

def verificar_alteracao(dict1, dict2):
    diferencas = {}
    
    for chave in dict1:
        if dict1[chave] != dict2.get(chave):
            diferencas[chave] = {
                'original': dict1[chave],
                'novo': dict2.get(chave)
            }
    
    return diferencas