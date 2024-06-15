import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import sqlite3
import random
import datetime
import hashlib
from config import ADMIN_USERNAME, ADMIN_PASSWORD

app = Flask(__name__)
app.secret_key = 'batata'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'clima_organizacional.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

#Fechar o banco quando o app for encerrado
@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def id_existe(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM usuarios_dim WHERE id = ?', (user_id,))
    result = cursor.fetchone()[0]
    return result > 0

def resposta_existe_esta_semana(user_id):
    semana_atual = datetime.datetime.now().isocalendar()[1]
    ano_atual = datetime.datetime.now().year
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT data FROM usuarios_respostas_fato WHERE id = ?', (user_id,))
    resultados = cursor.fetchall()
    
    for resultado in resultados:
        data_resposta = datetime.datetime.strptime(resultado[0], "%Y-%m-%d")
        if data_resposta.isocalendar()[1] == semana_atual and data_resposta.year == ano_atual:
            return True
    return False

def codifica_id(user_id):
    user_id_str = str(user_id)
    user_id_bytes = user_id_str.encode('utf-8')
    id_fantasia = hashlib.sha256(user_id_bytes).hexdigest()
    return id_fantasia

def valida_id(user_id, destino):
    if not user_id.isdigit():
        flash("Digite apenas números no ID","error")
        return redirect(url_for(destino))

    if not id_existe(user_id):
        flash("O ID não foi encontrado. Procure seu gestor","error")
        return redirect(url_for(destino))

    return None

def consulta_categorias():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_categoria, desc_categoria FROM categoria_dim')
        categorias = cursor.fetchall() 
        return categorias

@app.route('/', methods=['GET', 'POST'])
def entrada():
    if request.method == 'POST':
        user_id = request.form['user_id']
        
        testa_id = valida_id(user_id,'entrada')
        if testa_id:
            print(f'redicionar para {testa_id}')
            return testa_id
        
        if resposta_existe_esta_semana(user_id):
            flash("Você já respondeu essa semana.","success")
            return redirect(url_for('entrada'))

        id_fantasia = codifica_id(user_id)
        db = get_db()
        cursor = db.cursor()
    
        cursor.execute('SELECT fk_cargo FROM usuarios_dim WHERE id = ?', (user_id,))
        cargo = cursor.fetchone()[0]

        cursor.execute('SELECT fk_area FROM usuarios_dim WHERE id = ?', (user_id,))
        area = cursor.fetchone()[0]

        cursor.execute('SELECT fk_subarea FROM usuarios_dim WHERE id = ?', (user_id,))
        subarea = cursor.fetchone()[0]

        cursor.execute('SELECT fk_gestor FROM usuarios_dim WHERE id = ?', (user_id,))
        gestor = cursor.fetchone()[0]

        session['user_id'] = user_id
        session['id_fantasia'] = id_fantasia
        session['cargo'] = cargo
        session['area'] = area
        session['subarea'] = subarea
        session['gestor'] = gestor
        session['pergunta_atual'] = 0
        session['perguntas_selecionadas'] = []
        session['respostas'] = []
        
        return redirect(url_for('perguntas'))
    return render_template('entrada.html')

@app.route('/perguntas', methods=['GET', 'POST'])
def perguntas():
    if 'user_id' not in session :
        return redirect(url_for('entrada'))

    def chama_perguntas():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_pergunta, fk_categoria FROM pergunta_dim')
        perguntas = cursor.fetchall()
        return perguntas

    def cria_grupos_perguntas(perguntas):
        grupos_perguntas = {}
        for fk_pergunta, fk_categoria in perguntas:
            if fk_categoria not in grupos_perguntas:
                grupos_perguntas[fk_categoria] = []
            grupos_perguntas[fk_categoria].append(fk_pergunta)
        return grupos_perguntas

    perguntas = chama_perguntas()
    grupos_perguntas = cria_grupos_perguntas(perguntas)

    if 'perguntas_selecionadas' not in session or session['perguntas_selecionadas'] == []:
        perguntas_selecionadas = []
        for grupo in grupos_perguntas.values():
            selecionadas = random.sample(grupo, min(3, len(grupo)))
            perguntas_selecionadas += selecionadas
        if len(perguntas_selecionadas) >= 15:
            session['perguntas_selecionadas'] = random.sample(perguntas_selecionadas, 15)
        else:
            session['perguntas_selecionadas'] = perguntas_selecionadas

    pergunta_atual = session.get('pergunta_atual', 0)
    pergunta_atual = int(pergunta_atual)
    perguntas_selecionadas = session['perguntas_selecionadas']

    if pergunta_atual >= len(perguntas_selecionadas):
        return redirect(url_for('final'))

    db = get_db()
    cursor = db.cursor()
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
        print(request.form)
        if 'pular' in request.form:
            session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': -1, 'sugestao': ''})
        else:
            resposta = request.form['resposta']
            sugestao = request.form.get('sugestao', '')
            auto_identificacao = 'auto_identificacao' in request.form

            try:
                resposta = float(resposta)
            except ValueError:
                flash("A resposta deve ser um número entre 0 e 10.","warning")
                return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=15)

            session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': resposta, 'sugestao': sugestao, 'auto_identificacao': auto_identificacao})
        
        if 'proxima' in request.form or 'pular' in request.form or 'enviar-final' in request.form:
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
                    db.commit()

                    if resposta['sugestao']:
                        if resposta['auto_identificacao']:
                            cursor.execute('''
                                INSERT INTO sugestoes_fato (fk_cargo, fk_area, fk_subarea, fk_gestor, fk_pergunta, fk_categoria, data, datetime, sugestao, id_autoidentificacao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (cargo, area, subarea, gestor, resposta['pergunta'], resposta['categoria'], data_atual, date_time, resposta['sugestao'], user_id))
                            db.commit()
                        else:
                            cursor.execute('''
                                INSERT INTO sugestoes_fato (fk_cargo, fk_area, fk_subarea, fk_gestor, fk_pergunta, fk_categoria, data, datetime, sugestao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (cargo, area, subarea, gestor, resposta['pergunta'], resposta['categoria'], data_atual, date_time, resposta['sugestao']))
                            db.commit()

                session.pop('perguntas_selecionadas', None)
                session.pop('pergunta_atual', None)
                session.pop('respostas', None)

                flash("Respostas enviadas com sucesso!","success")
                cursor.execute('''
                               INSERT INTO usuarios_respostas_fato (id, data, datetime)
                               VALUES (?, ?, ?)
                               ''', (user_id, data_atual, date_time))
                db.commit()
                return redirect(url_for('final'))

        elif 'anterior' in request.form:
            if pergunta_atual > 0:
                session['pergunta_atual'] = pergunta_atual - 1

        pergunta_atual = session.get('pergunta_atual', 0)
        pergunta_atual = int(pergunta_atual)
        num_pergunta = perguntas_selecionadas[pergunta_atual]
        cursor.execute('SELECT desc_pergunta FROM pergunta_dim WHERE fk_pergunta = ?', (num_pergunta,))
        pergunta = cursor.fetchone()[0]
        cursor.execute('SELECT fk_categoria FROM pergunta_dim WHERE fk_pergunta = ?', (num_pergunta,))
        categoria = cursor.fetchone()[0]
    
    return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=15)

@app.route('/respondido', methods=['GET', 'POST'])
def final():
    if 'user_id' not in session or 'area' not in session:
        return redirect(url_for('entrada'))

    if request.method == 'POST':
        session.clear()
        if 'enviar_sugestao' in request.form:
            return redirect(url_for('sugestao'))
    return render_template('final.html')

@app.route('/sugestao', methods=['GET', 'POST'])
def sugestao():
    session.pop('user_id', None)
    session.pop('id_fantasia', None)
    def chama_tabela(tabela):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f'SELECT desc_{tabela} FROM {tabela}_dim')
        areas = cursor.fetchall()
        return areas
    
    area = chama_tabela('area')
    subarea = chama_tabela('subarea')
    gestor = chama_tabela('gestor')
    categoria = chama_tabela('categoria')

    def cria_grupo(tabela):
        grupo_tabela = set()
        for variavel_tupla in tabela:
            variavel = variavel_tupla[0]
            grupo_tabela.add(variavel)
        return grupo_tabela
    
    areas = cria_grupo(area)
    subareas = cria_grupo(subarea)
    gestores = cria_grupo(gestor)
    categorias = cria_grupo(categoria)

    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()

        area = request.form['area']
        subarea = request.form['subarea']
        categoria = request.form['categoria']
        user_id = request.form['user_id']
        sugestao_text = request.form['sugestao']
        
        if not user_id:
            user_id = -1

        if not area or not subarea or not categoria or not sugestao_text:
            flash("Por favor, preencha a um texto na sua sugestão.","warning")
            return redirect(url_for('sugestao'))
        
        date_time = datetime.datetime.now()
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        def encontra_fk(variavel,tabela):
            variavel = f"'{variavel}'"
            cursor.execute(f'SELECT fk_{tabela} FROM {tabela}_dim WHERE desc_{tabela}={variavel}')
            fk_variavel=cursor.fetchone()[0]
            return fk_variavel
        
        fk_area = encontra_fk(area,'area')
        fk_subarea = encontra_fk(subarea,'subarea')
        fk_categoria = encontra_fk(categoria,'categoria')

        cursor.execute('''
            INSERT INTO sugestoes_fato (fk_area, fk_subarea, fk_categoria, data, datetime, sugestao, id_autoidentificacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fk_area, fk_subarea, fk_categoria, data_atual, date_time, sugestao_text, user_id))
        db.commit()

        flash("Sugestão enviada com sucesso!", "success")
        return redirect(url_for('sugestao'))

    return render_template('sugestao.html', areas=areas, subareas=subareas, gestores=gestores, categorias=categorias)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if check_admin(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Login inválido. Tente novamente.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()

    email_gestor = session['username'].split('@')
    id_gestor = email_gestor[0]

    testa_id = valida_id(id_gestor,'login')
    if testa_id:
        print(f'redicionar para {testa_id}')
        return testa_id
    
    #Traz o fk_gestor para verificar quantas respostas do time dele existem
    def consulta_gestor(id_gestor):
        cursor.execute('SELECT fk_gestor, desc_gestor FROM gestor_dim WHERE id_gestor = ?',(id_gestor))
        dados_gestor = cursor.fetchone()
        fk_gestor, nome_gestor = dados_gestor
        return fk_gestor,nome_gestor
    
    def verifica_qtd_respostas(fk_gestor, fk_categoria=None, fk_pergunta=None):
        if fk_categoria and fk_pergunta:
            cursor.execute('SELECT COUNT(*) FROM respostas_fato WHERE fk_gestor = ? and fk_categoria = ? and fk_pergunta = ?',(fk_gestor,fk_categoria, fk_pergunta))
        elif fk_categoria:
            cursor.execute('SELECT COUNT(*) FROM respostas_fato WHERE fk_gestor = ? and fk_categoria = ?',(fk_gestor,fk_categoria,))
        else:     
            cursor.execute('SELECT COUNT(*) FROM respostas_fato WHERE fk_gestor = ?',(fk_gestor,))
        num_respostas = cursor.fetchone()[0]
        return num_respostas
    
    def consulta_nota(fk_gestor, fk_categoria=None, fk_pergunta=None):
        if fk_categoria and fk_pergunta:
            cursor.execute('SELECT AVG(resposta) FROM respostas_fato WHERE fk_gestor = ? and fk_categoria = ? and fk_pergunta = ?',(fk_gestor,fk_categoria, fk_pergunta))
        elif fk_categoria:
            cursor.execute('SELECT AVG(resposta) FROM respostas_fato WHERE fk_gestor = ? and fk_categoria = ?',(fk_gestor,fk_categoria,))
        else:     
            cursor.execute('SELECT AVG(resposta) FROM respostas_fato WHERE fk_gestor = ?',(fk_gestor,))        
        nota_media = cursor.fetchone()[0]
        nota_media = round(nota_media,2)
        return nota_media
    
    
    def gera_cards():
        categorias = consulta_categorias()
        cards = []
        for fk_categoria, desc_categoria in categorias:
            valor = consulta_nota(fk_gestor,fk_categoria)
            size_bar = valor * 10
            quantidade_respostas = verifica_qtd_respostas(fk_gestor,fk_categoria)
            card = {
                'id': fk_categoria,
                'title': desc_categoria,
                'size': size_bar,
                'value': valor,
                'total': 10,
                'qtd_respostas': quantidade_respostas
            }
            cards.append(card)
        return cards
    
    fk_gestor = consulta_gestor(id_gestor)[0]
    nome_gestor = consulta_gestor(id_gestor)[1]
    quantidade_respostas = verifica_qtd_respostas(fk_gestor)
    nota_media = consulta_nota(fk_gestor)
    size_bar = nota_media * 10 
    cards = gera_cards()

    return render_template('dashboard.html', nome = nome_gestor, qtd_respostas = quantidade_respostas, nota_media = nota_media, size_bar = size_bar, cards=cards)

@app.route('/settings')
def settings():
    return render_template('settings.html')

def check_admin(username, password):
    admin_username = ADMIN_USERNAME
    admin_password_hash = ADMIN_PASSWORD
    return username == admin_username and password == admin_password_hash

if __name__ == '__main__':
    app.run(debug=True)