from flask import current_app as app, session
import random

def cria_grupos_perguntas(perguntas):
        grupos_perguntas = {}
        for fk_pergunta, fk_categoria in perguntas:
            if fk_categoria not in grupos_perguntas:
                grupos_perguntas[fk_categoria] = []
            grupos_perguntas[fk_categoria].append(fk_pergunta)

        return grupos_perguntas

def navegar_perguntas(num_pergunta_atual, botao, total_perguntas):
        if botao == 'anterior' and num_pergunta_atual > 0:
                return num_pergunta_atual - 1
        elif botao in ['proxima', 'pular'] and num_pergunta_atual < (total_perguntas - 1):
                return num_pergunta_atual + 1

def sorteia_perguntas(grupo_perguntas, num_perguntas):
    perguntas_selecionadas = []
    
    # Seleciona uma pergunta de cada grupo
    for grupo in grupo_perguntas.values():
        selecionadas = random.sample(grupo, min(1, len(grupo)))
        perguntas_selecionadas += selecionadas
    
    # Verifica se o total de perguntas selecionadas é menor que o número desejado
    if len(perguntas_selecionadas) < num_perguntas:
        # Combina todas as perguntas restantes que não foram selecionadas
        todas_perguntas = [pergunta for grupo in grupo_perguntas.values() for pergunta in grupo]
        perguntas_disponiveis = list(set(todas_perguntas) - set(perguntas_selecionadas))
        
        # Sorteia perguntas extras até atingir o número desejado
        adicionais = random.sample(perguntas_disponiveis, min(len(perguntas_disponiveis), num_perguntas - len(perguntas_selecionadas)))
        perguntas_selecionadas += adicionais
    
    # Se já há mais do que o necessário, seleciona um subconjunto
    if len(perguntas_selecionadas) > num_perguntas:
        perguntas_selecionadas = random.sample(perguntas_selecionadas, num_perguntas)
    
    return perguntas_selecionadas

