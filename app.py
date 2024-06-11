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
        session['perguntas_selecionadas'] = []
        session['respostas'] = []

        return redirect(url_for('perguntas'))
    return render_template('entrada.html')

@app.route('/perguntas', methods=['GET', 'POST'])
def perguntas():
    if 'user_id' not in session:
        return redirect(url_for('entrada'))

    grupos_perguntas = {
        "Satisfação no Trabalho": [
            "Quão satisfeito estou com meu ambiente de trabalho?",
            "Como avalio minha relação com meus colegas de trabalho?",
            "Como avalio o aproveitamento das minhas habilidades e competências na minha função atual?",
            "Como avalio o reconhecimento do meu trabalho pela empresa?",
            "Como descrevo o equilíbrio entre minha vida profissional e pessoal?"
        ],
        "Comunicação": [
            "Como avalio a clareza e eficácia da comunicação entre os membros da minha equipe?",
            "Como avalio meu conforto para compartilhar ideias e sugestões com a gerência?",
            "Como avalio a transparência da comunicação da empresa sobre objetivos e metas?",
            "Como avalio o feedback construtivo que recebo sobre o meu desempenho?",
            "Como avalio a frequência e qualidade das reuniões de equipe?"
        ],
        "Liderança": [
            "Como avalio a acessibilidade e apoio da liderança da minha equipe?",
            "Como avalio a preocupação da gerência com o meu desenvolvimento profissional?",
            "Como avalio a confiança e respeito inspirados pelos líderes da empresa?",
            "Como avalio a capacidade da liderança em tomar decisões justas?",
            "Como avalio a motivação proporcionada pela liderança na condução da equipe?"
        ],
        "Desenvolvimento e Crescimento": [
            "Como avalio as oportunidades para meu desenvolvimento e crescimento profissional oferecidas pela empresa?",
            "Como avalio o acesso a treinamentos e cursos para aprimorar minhas habilidades?",
            "Como avalio o plano de carreira definido para minha posição?",
            "Como avalio minhas chances de atingir minhas metas de carreira dentro da empresa?",
            "Como avalio o incentivo à inovação e criatividade pela empresa?"
        ],
        "Condições de Trabalho": [
            "Como avalio as condições de trabalho (infraestrutura, equipamentos, etc.)?",
            "Como avalio o ambiente seguro e saudável oferecido pela empresa?",
            "Como avalio as políticas de trabalho remoto ou flexível em atender às minhas necessidades?",
            "Como avalio os recursos necessários para realizar meu trabalho eficientemente?",
            "Como avalio a carga de trabalho e as expectativas em relação a prazos?"
        ],
        "Cultura Organizacional": [
            "Como avalio o alinhamento da cultura da empresa com meus valores pessoais?",
            "Como avalio a promoção de um ambiente inclusivo e diversificado pela empresa?",
            "Como avalio a valorização da colaboração e trabalho em equipe pela empresa?",
            "Como avalio meu conhecimento das políticas da empresa sobre ética e conduta?",
            "Como avalio as atividades promovidas pela empresa que incentivam meu engajamento e integração?"
        ]
    }

    if 'perguntas_selecionadas' not in session or session['perguntas_selecionadas'] == [] :
        perguntas_selecionadas = []
        for grupo in grupos_perguntas.values():
            selecionadas = random.sample(grupo, min(5, len(grupo)))  # Seleciona 2 perguntas de cada grupo
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
    pergunta = perguntas_selecionadas[pergunta_atual]

    if request.method == 'POST':
        if 'pular' in request.form:
            session['respostas'].append({'pergunta': pergunta, 'resposta': -1, 'sugestao': '', 'auto_identificacao': False})
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

            session['respostas'].append({'pergunta': pergunta, 'resposta': resposta, 'sugestao': sugestao, 'auto_identificacao': auto_identificacao})
        if 'proxima' in request.form or 'pular' in request.form:
            if pergunta_atual < len(perguntas_selecionadas) - 1:
                session['pergunta_atual'] = pergunta_atual + 1
            else:
                user_id = session['user_id']
                date_time = datetime.datetime.now()
                data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
                conn, cursor = get_db()
                cursor.execute('SELECT area FROM usuarios where id = (?)',(user_id))
                area_lista = cursor.fetchone()
                area = area_lista[0]
                for resposta in session['respostas']:
                    cursor.execute('''
                        INSERT INTO respostas (id, data, datetime, descricao_pergunta, resposta)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, data_atual, date_time, resposta['pergunta'], resposta['resposta']))

                    if resposta['sugestao']:
                        if resposta	['auto_identificacao']:
                            cursor.execute('''
                                INSERT INTO sugestoes (id, area, data, datetime,  pergunta, sugestao, auto_identificacao, id_auto_identificacao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (user_id, area, data_atual, date_time, resposta['pergunta'], resposta['sugestao'], resposta['auto_identificacao'], user_id))
                        else:
                            cursor.execute('''
                                INSERT INTO sugestoes (id, area, data, datetime,  pergunta, sugestao)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (user_id, area, data_atual, date_time, resposta['pergunta'], resposta['sugestao']))
                
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

        pergunta_atual = session.get('pergunta_atual', 0)
        pergunta_atual = int(pergunta_atual)  # Certifique-se de que é um inteiro
        pergunta = perguntas_selecionadas[pergunta_atual]

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
        area = session['area']
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
            ''', (user_id, area, data_atual, date_time, categoria, sugestao_text))
        conn.commit()
        conn.close()

        flash("Sugestão enviada com sucesso!")
        return redirect(url_for('inicio_sugestao'))
    
    return render_template('sugestao.html')

if __name__ == '__main__':
    
    app.run(debug=True)
