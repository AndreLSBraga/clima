import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import random
import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'clima_organizacional.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn, conn.cursor()

def id_existe(user_id):
    conn, cursor = get_db()
    cursor.execute('SELECT COUNT(*) FROM usuarios_dim WHERE id = ?', (user_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def resposta_existe_esta_semana(user_id):
    semana_atual = datetime.datetime.now().isocalendar()[1]
    ano_atual = datetime.datetime.now().year
    conn, cursor = get_db()
    cursor.execute('SELECT data FROM usuarios_respostas_fato WHERE id = ?', (user_id,))
    resultados = cursor.fetchall()
    
    conn.close()
    for resultado in resultados:
        data_resposta = datetime.datetime.strptime(resultado[0], "%Y-%m-%d")
        if data_resposta.isocalendar()[1] == semana_atual and data_resposta.year == ano_atual:
            return True
    return False

def codifica_id(user_id):
    # Convertendo o ID do usuário para string e depois para bytes
    user_id_str = str(user_id)
    user_id_bytes = user_id_str.encode('utf-8')
    
    # Calculando o hash SHA-256
    id_fantasia = hashlib.sha256(user_id_bytes).hexdigest()
    
    return id_fantasia

@app.route('/', methods=['GET', 'POST'])
def entrada():
    if request.method == 'POST':
        user_id = request.form['user_id']

        if not user_id.isdigit():
            flash("Digite apenas números no ID")
            return redirect(url_for('entrada'))

        if not id_existe(user_id):
            flash("O ID não foi encontrado. Procure o suporte")
            return redirect(url_for('entrada'))

        if resposta_existe_esta_semana(user_id):
            flash("Você já respondeu o clima desta semana.")
            return redirect(url_for('entrada'))
        
        id_fantasia = codifica_id(user_id)
        conn, cursor = get_db()
    
        cursor.execute('SELECT fk_cargo FROM usuarios_dim WHERE id = ?', (user_id))
        cargo = cursor.fetchone()[0]

        cursor.execute('SELECT fk_area FROM usuarios_dim WHERE id = ?', (user_id))
        area = cursor.fetchone()[0]

        cursor.execute('SELECT fk_subarea FROM usuarios_dim WHERE id = ?', (user_id))
        subarea = cursor.fetchone()[0]

        cursor.execute('SELECT fk_gestor FROM usuarios_dim WHERE id = ?', (user_id))
        gestor = cursor.fetchone()[0]
        # Inicializar sessão para armazenar estado da navegação e respostas
        session['user_id'] = user_id
        session['id_fantasia'] = id_fantasia
        session['cargo'] = cargo
        session['area'] = area
        session['subarea'] = subarea
        session['gestor'] = gestor
        session['pergunta_atual'] = 0
        session['perguntas_selecionadas'] = []
        session['respostas'] = []
        conn.close()
        return redirect(url_for('perguntas'))
    return render_template('entrada.html')

@app.route('/perguntas', methods=['GET', 'POST'])
def perguntas():
    if 'user_id' not in session:
        return redirect(url_for('entrada'))

    def chama_perguntas():
        conn, cursor = get_db()
        cursor.execute('SELECT fk_pergunta, fk_categoria FROM pergunta_dim')
        perguntas = cursor.fetchall()
        conn.close()
        return perguntas

    def cria_grupos_perguntas(perguntas):
        grupos_perguntas = {}

        # Percorrer as perguntas e organizar por categoria
        for fk_pergunta, fk_categoria in perguntas:
            if fk_categoria not in grupos_perguntas:
                grupos_perguntas[fk_categoria] = []
            grupos_perguntas[fk_categoria].append(fk_pergunta)

        return grupos_perguntas

    perguntas = chama_perguntas()

    # Construir o dicionário de grupos de perguntas
    grupos_perguntas = cria_grupos_perguntas(perguntas)

    if 'perguntas_selecionadas' not in session or session['perguntas_selecionadas'] == [] :
        perguntas_selecionadas = []
        for grupo in grupos_perguntas.values():
            selecionadas = random.sample(grupo, min(3, len(grupo)))  # Seleciona 2 perguntas de cada grupo
            perguntas_selecionadas += selecionadas
        if len(perguntas_selecionadas) >= 15:
            session['perguntas_selecionadas'] = random.sample(perguntas_selecionadas, 15)  # Seleciona 15 perguntas no total
        else:
            session['perguntas_selecionadas'] = perguntas_selecionadas

    pergunta_atual = session.get('pergunta_atual', 0)
    pergunta_atual = int(pergunta_atual)  # Certifique-se de que é um inteiro
    perguntas_selecionadas = session['perguntas_selecionadas']
    # Verifica se a pergunta atual está dentro do intervalo correto
    if pergunta_atual >= len(perguntas_selecionadas):
        return redirect(url_for('final'))
    conn, cursor = get_db()
    num_pergunta = perguntas_selecionadas[pergunta_atual]
    cursor.execute('SELECT desc_pergunta FROM pergunta_dim WHERE fk_pergunta = ?', (num_pergunta,))
    pergunta = cursor.fetchone()[0]
    cursor.execute('SELECT fk_categoria FROM pergunta_dim WHERE fk_pergunta = ?', (num_pergunta,))
    categoria = cursor.fetchone()[0]

    if request.method == 'POST':

        id_fantasia = session['id_fantasia']
        cargo = session['cargo']
        area = session['area']
        subarea = session['subarea']
        gestor = session['gestor']

        if 'pular' in request.form:
            session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': -1, 'sugestao': ''})
        else:
            resposta = request.form['resposta']
            sugestao = request.form.get('sugestao', '')
            auto_identificacao = 'auto_identificacao' in request.form

            # Assegure-se de que a resposta é um número flutuante
            try:
                resposta = float(resposta)
            except ValueError:
                flash("A resposta deve ser um número entre 0 e 10.")
                return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=15)

            session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': resposta, 'sugestao': sugestao, 'auto_identificacao': auto_identificacao})
        
        if 'proxima' in request.form or 'pular' in request.form:
            if pergunta_atual < len(perguntas_selecionadas) - 1:
                session['pergunta_atual'] = pergunta_atual + 1
            else:
                user_id = session['user_id']
                date_time = datetime.datetime.now()
                data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
                
                for resposta in session['respostas']:
                    cursor.execute('''
                        INSERT INTO respostas_fato (id_fantasia, fk_cargo, fk_area, fk_subarea, fk_gestor, fk_pergunta, fk_categoria, data, datetime, resposta)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (id_fantasia, cargo, area, subarea, gestor, resposta['pergunta'], resposta['categoria'], data_atual, date_time, resposta['resposta']))
                    conn.commit()
                        
                    if resposta['sugestao']:
                        if resposta	['auto_identificacao']:
                            cursor.execute('''
                                INSERT INTO sugestoes_fato (fk_cargo, fk_area, fk_subarea, fk_gestor, fk_pergunta, fk_categoria, data, datetime, sugestao, id_autoidentificacao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (cargo, area, subarea, gestor, resposta['pergunta'], resposta['categoria'], data_atual, date_time, resposta['sugestao'], user_id))
                            conn.commit()
                        else:
                            cursor.execute('''
                                INSERT INTO sugestoes_fato (fk_cargo, fk_area, fk_subarea, fk_gestor, fk_pergunta, fk_categoria, data, datetime, sugestao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (cargo, area, subarea, gestor, resposta['pergunta'], resposta['categoria'], data_atual, date_time, resposta['sugestao']))
                            conn.commit()
                session.pop('perguntas_selecionadas', None)
                session.pop('pergunta_atual', None)
                session.pop('respostas', None)

                flash("Respostas enviadas com sucesso!")
                cursor.execute(''' 
                               INSERT INTO usuarios_respostas_fato (id, data, datetime)
                               VALUES (?,?,?)
                               ''', (user_id, data_atual, date_time))
                conn.commit()
                return redirect(url_for('final'))

        elif 'anterior' in request.form:
            if pergunta_atual > 0:
                session['pergunta_atual'] = pergunta_atual - 1
        print(session['respostas'])
        pergunta_atual = session.get('pergunta_atual', 0)
        pergunta_atual = int(pergunta_atual)  # Certifique-se de que é um inteiro
        num_pergunta = perguntas_selecionadas[pergunta_atual]
        cursor.execute('SELECT desc_pergunta FROM pergunta_dim WHERE fk_pergunta = ?', (num_pergunta,))
        pergunta = cursor.fetchone()[0]
        cursor.execute('SELECT fk_categoria FROM pergunta_dim WHERE fk_pergunta = ?', (num_pergunta,))
        categoria = cursor.fetchone()[0]
        conn.close()
    return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=15)

@app.route('/respondido', methods=['GET', 'POST'])
def final():
    if 'user_id' not in session:
        return redirect(url_for('entrada'))

    if request.method == 'POST':
        if 'abrir_sugestao' in request.form:
            return redirect(url_for('sugestao'))
    return render_template('final.html')

@app.route('/inicio_sugestao', methods=['GET', 'POST'])
    
def inicio_sugestao():
    if request.method == 'POST':
        session['area'] = request.form['area']
        session['user_id'] = request.form['user_id']
        user_id = session['user_id']
        if not user_id:
            session['user_id'] = -1
        return redirect(url_for('sugestao'))  # Redireciona para a página de sugestão após a interação
    return render_template('inicio_sugestao.html')  # Renderiza a tela inicial
    

@app.route('/sugestao', methods=['GET', 'POST'])

def sugestao():
    
    if request.method == 'POST':
        subarea = session['subarea']
        user_id = session['user_id']
        sugestao_text = request.form['sugestao']
        categoria = request.form['categoria']

        if not sugestao_text or not categoria:
            flash("Por favor, preencha a categoria e/ou sugestão.")
            return redirect(url_for('sugestao'))
        
        date_time = datetime.datetime.now()
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        conn, cursor = get_db()
        cursor.execute('''
            INSERT INTO sugestoes (id, area, data, datetime, categoria, sugestao)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, subarea, data_atual, date_time, categoria, sugestao_text))
        conn.commit()
        conn.close()

        flash("Sugestão enviada com sucesso!")
        return redirect(url_for('inicio_sugestao'))
    
    return render_template('inicio_sugestao.html')

if __name__ == '__main__':
    app.run(debug=True)
