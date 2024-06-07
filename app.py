import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import random
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'clima_organizacional.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn, conn.cursor()

def id_existe(user_id):
    conn, cursor = get_db()
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE id = ?', (user_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def resposta_existe_esta_semana(user_id):
    semana_atual = datetime.datetime.now().isocalendar()[1]
    ano_atual = datetime.datetime.now().year
    conn, cursor = get_db()
    cursor.execute('SELECT data FROM respostas WHERE id = ?', (user_id,))
    resultados = cursor.fetchall()
    conn.close()
    for resultado in resultados:
        data_resposta = datetime.datetime.strptime(resultado[0], "%Y-%m-%d")
        print(data_resposta)
        if data_resposta.isocalendar()[1] == semana_atual and data_resposta.year == ano_atual:
            return True
    return False

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

        # Inicializar sessão para armazenar estado da navegação e respostas
        session['user_id'] = user_id
        session['pergunta_atual'] = 0
        session['respostas'] = []

        return redirect(url_for('perguntas'))
    return render_template('entrada.html')

@app.route('/perguntas', methods=['GET', 'POST'])
def perguntas():
    grupos_perguntas = {
        "Bem-estar": [
            "Como você avalia a comunicação interna na empresa?",
            "Você sente que o seu trabalho é importante para a companhia?",
            "Há um equilibrio entre minha vida pessoal e profissional?",
        ],
        "Saúde Mental": [
            "Você se sente motivado no seu trabalho diário?",
            "Você sente que tem os recursos necessários para realizar seu trabalho?",
        ],
        "Liderança": [
            "Como você avalia a liderança da sua equipe?",
            "Você sente que seu trabalho é reconhecido?",
            "Como você avalia a transparência nas decisões da empresa?",
            "Você recomendaria a empresa como um bom lugar para trabalhar?",
        ],
        "Crescimento Profissional": [
            "Como você avalia as oportunidades de crescimento na empresa?",
            "Você está satisfeito com os benefícios oferecidos pela empresa?",
            "Você sente que tem oportunidades de desenvolver novas habilidades?",
        ],
        "Equilíbrio Trabalho-Vida": [
            "Como você avalia a carga de trabalho?",
            "Você está satisfeito com o suporte da sua equipe?",
            "Como você avalia o ambiente físico de trabalho?",
        ],
        "Serviços Gerais":[
            "Como você avalia a limpeza, organização dos banheiros?"
        ]
    }

    if 'perguntas_selecionadas' not in session:
        perguntas_selecionadas = []
        for grupo in grupos_perguntas.values():
            perguntas_selecionadas += random.sample(grupo, min(2, len(grupo)))  # Seleciona 2 perguntas de cada grupo
        session['perguntas_selecionadas'] = random.sample(perguntas_selecionadas, 10)  # Seleciona 10 perguntas no total

    pergunta_atual = session.get('pergunta_atual', 0)
    pergunta_atual = int(pergunta_atual)  # Certifique-se de que é um inteiro
    perguntas_selecionadas = session['perguntas_selecionadas']
    pergunta = perguntas_selecionadas[pergunta_atual]

    if request.method == 'POST':
        if 'pular' in request.form:
            session['respostas'].append({'pergunta': pergunta, 'resposta': -1, 'sugestao': ''})
        else:
            resposta = request.form['resposta']
            sugestao = request.form.get('sugestao', '')

            # Assegure-se de que a resposta é um número flutuante
            try:
                resposta = float(resposta)
            except ValueError:
                flash("A resposta deve ser um número entre 0 e 10.")
                return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=10)

            session['respostas'].append({'pergunta': pergunta, 'resposta': resposta, 'sugestao': sugestao})

        if 'proxima' in request.form or 'pular' in request.form:
            if pergunta_atual < 9:
                session['pergunta_atual'] = pergunta_atual + 1
            else:
                user_id = session['user_id']
                date_time = datetime.datetime.now()
                data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
                conn, cursor = get_db()
                for resposta in session['respostas']:
                    cursor.execute('''
                    INSERT INTO respostas (id, data, datetime, descricao_pergunta, resposta, sugestao)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, data_atual, date_time, resposta['pergunta'], resposta['resposta'], resposta['sugestao']))
                conn.commit()
                conn.close()

                session.pop('perguntas_selecionadas', None)
                session.pop('pergunta_atual', None)
                session.pop('respostas', None)

                flash("Respostas enviadas com sucesso!")
                return redirect(url_for('final'))

        elif 'anterior' in request.form:
            if pergunta_atual > 0:
                session['pergunta_atual'] = pergunta_atual - 1
                #session['respostas'].pop()  # Remove a última resposta ao voltar para a pergunta anterior

        pergunta_atual = session.get('pergunta_atual', 0)
        pergunta_atual = int(pergunta_atual)  # Certifique-se de que é um inteiro
        pergunta = perguntas_selecionadas[pergunta_atual]

    return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=10)

@app.route('/respondido', methods=['GET', 'POST'])
def final():
    return render_template('final.html')

@app.route('/sugestao', methods=['GET', 'POST'])
def sugestao():
    if request.method == 'POST':
        sugestao_text = request.form['sugestao_text']
        user_id = session.get('user_id', 'Anonimo')  # Obtenha o user_id da sessão, ou 'Anonimo' se não estiver disponível
        date_time = datetime.datetime.now()
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        conn, cursor = get_db()
        cursor.execute('''
        INSERT INTO sugestoes (id, data, datetime, sugestao)
        VALUES (?, ?, ?, ?)
        ''', (user_id, data_atual, date_time, sugestao_text))
        conn.commit()
        conn.close()

        flash("Sugestão enviada com sucesso!")
        return redirect(url_for('sugestao'))
    
    return render_template('sugestao.html')

if __name__ == '__main__':
    app.run(debug=True)
