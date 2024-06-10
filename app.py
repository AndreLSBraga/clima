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
            "Você está satisfeito com o seu ambiente de trabalho?",
            "Como você avalia a relação com seus colegas de trabalho?",
            "Acha que suas habilidades e competências são bem aproveitadas na sua função atual?",
            "Sente que seu trabalho é reconhecido pela empresa?",
            "Como você descreveria o equilíbrio entre sua vida profissional e pessoal?"
        ],
        "Comunicação": [
            "A comunicação entre os membros da equipe é clara e eficaz?",
            "Você se sente à vontade para compartilhar suas ideias e sugestões com a gerência?",
            "A comunicação da empresa sobre objetivos e metas é transparente?",
            "Você recebe feedback construtivo sobre o seu desempenho?",
            "Como você avalia a frequência e a qualidade das reuniões de equipe?"
        ],
        "Liderança": [
            "Você sente que a liderança da sua equipe é acessível e apoiadora?",
            "A gerência se preocupa com o desenvolvimento profissional dos colaboradores?",
            "Os líderes da empresa inspiram confiança e respeito?",
            "Como você avalia a capacidade da liderança em tomar decisões justas?",
            "Você se sente motivado pela forma como a liderança conduz a equipe?"
        ],
        "Desenvolvimento e Crescimento": [
            "A empresa oferece oportunidades claras para desenvolvimento e crescimento profissional?",
            "Você tem acesso a treinamentos e cursos para aprimorar suas habilidades?",
            "Existe um plano de carreira definido para sua posição?",
            "Sente que pode atingir suas metas de carreira dentro da empresa?",
            "A empresa incentiva a inovação e a criatividade?"
        ],
        "Condições de Trabalho": [
            "Você acha que as condições de trabalho (infraestrutura, equipamentos, etc.) são adequadas?",
            "A empresa oferece um ambiente seguro e saudável para trabalhar?",
            "As políticas de trabalho remoto ou flexível atendem às suas necessidades?",
            "Você tem os recursos necessários para realizar seu trabalho eficientemente?",
            "Como você avalia a carga de trabalho e as expectativas em relação a prazos?"
        ],
        "Cultura Organizacional": [
            "A cultura da empresa está alinhada com seus valores pessoais?",
            "Você sente que a empresa promove um ambiente inclusivo e diversificado?",
            "A empresa valoriza a colaboração e o trabalho em equipe?",
            "Você está ciente das políticas da empresa sobre ética e conduta?",
            "A empresa promove atividades que incentivam o engajamento e a integração dos colaboradores?"
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
    print(len(perguntas_selecionadas))
    print(perguntas_selecionadas)

    # Verifica se a pergunta atual está dentro do intervalo correto
    if pergunta_atual >= len(perguntas_selecionadas):
        return redirect(url_for('final'))
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
                return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=15)

            session['respostas'].append({'pergunta': pergunta, 'resposta': resposta, 'sugestao': sugestao})

        if 'proxima' in request.form or 'pular' in request.form:
            if pergunta_atual < len(perguntas_selecionadas) - 1:
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
        area_selecionada = request.form['area']  # Recebe a área selecionada pelo usuário
        user_id = request.form['user_id']
        if not user_id:
            user_id= -1
        return redirect(url_for('sugestao',area=area_selecionada, user_id=user_id))  # Redireciona para a página de sugestão após a interação
    return render_template('id_sugestao.html')  # Renderiza a tela inicial


@app.route('/sugestao', methods=['GET', 'POST'])

def sugestao():

    if request.method == 'POST':
        area = request.form.get('area')  # Ajustado para obter dados de formulário
        user_id = request.form.get('user_id')  # Ajustado para obter dados de formulário
        print(area,user_id)
        sugestao_text = request.form['sugestao']
        categoria = request.form['categoria']

        if not sugestao_text or not categoria:
            flash("Por favor, preencha a categoria e/ou sugestão.")
            return redirect(url_for('sugestao'))
        
        date_time = datetime.datetime.now()
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        conn, cursor = get_db()
        cursor.execute('''
        INSERT INTO sugestoes (id, data, datetime, categoria, sugestao)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, data_atual, date_time, categoria, sugestao_text))
        conn.commit()
        conn.close()

        flash("Sugestão enviada com sucesso!")
        return redirect(url_for('sugestao'))
    
    return render_template('sugestao.html')

if __name__ == '__main__':
    app.run(debug=True)
