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

def consulta_tabelas(coluna, tabela, col_filtro = None, filtro = None):
    db = get_db()
    cursor = db.cursor()
    lista = []
    if filtro:
        cursor.execute(f'SELECT {coluna} FROM {tabela} WHERE {col_filtro} = ?', (filtro,)),
    else:
        cursor.execute(f'SELECT {coluna} FROM {tabela}')
    dados = cursor.fetchall()
    
    for dado in dados:
        item = dado[0]
        lista.append(item)
    return lista


@app.route('/', methods=['GET', 'POST'])
def entrada():
    subareas = consulta_tabelas('desc_subarea','subarea_dim')
    cargos = consulta_tabelas('desc_cargo','cargo_dim')
    gestores = consulta_tabelas('desc_gestor','gestor_dim')

    if request.method == 'POST':
        subarea = request.form.get('area', None)
        gestor = request.form.get('gestor', None)
        cargo = request.form.get('cargo', None)

        fk_subarea = consulta_tabelas('fk_subarea', 'subarea_dim', 'desc_subarea',subarea)
        fk_gestor = consulta_tabelas('fk_gestor', 'gestor_dim', 'desc_gestor',gestor)
        fk_cargo = consulta_tabelas('fk_cargo', 'cargo_dim', 'desc_cargo',cargo)

        session['idade'] = request.form.get('idade', None)
        session['sexo'] = request.form.get('sexo', None)
        session['cargo'] = fk_cargo
        session['subarea'] = fk_subarea
        session['gestor'] = fk_gestor
        session['pergunta_atual'] = 0
        session['perguntas_selecionadas'] = []
        session['respostas'] = []

        if None in (session['idade'], session['sexo'], session['cargo'], session['subarea'], session['gestor']):
            flash("Todos os campos são obrigatórios.", "warning")
        else:
            return redirect(url_for('perguntas'))
        
    return render_template('entrada.html',areas=subareas, cargos=cargos, gestores=gestores)

@app.route('/perguntas', methods=['GET', 'POST'])
def perguntas():
    
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
    
    date_time = datetime.datetime.now()
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
    semana_atual = datetime.datetime.now().isocalendar()[1]

    if request.method == 'POST':
        subarea = session['subarea'][0]
        gestor = session['gestor'][0]
        cargo = session['cargo'][0]
        idade = session['idade'][0]
        sexo = session['sexo'][0]

        if 'pular' in request.form:
            session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': -1, 'sugestao': ''})
        else:
            resposta = request.form['resposta']
            sugestao = request.form.get('sugestao', '')

            try:
                resposta = float(resposta)
            except ValueError:
                flash("A resposta deve ser um número entre 0 e 10.","warning")
                return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=15)

            session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': resposta, 'sugestao': sugestao})
        
        if 'proxima' in request.form or 'pular' in request.form or 'enviar-final' in request.form:
            if pergunta_atual < len(perguntas_selecionadas) - 1:
                session['pergunta_atual'] = pergunta_atual + 1
            else:

                for resposta in session['respostas']:
                    cursor.execute('''
                        INSERT INTO respostas_fato (fk_subarea, fk_gestor, fk_cargo, idade, sexo, fk_pergunta, fk_categoria, semana, data, datetime, resposta)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''',  (subarea, gestor, cargo, idade, sexo, resposta['pergunta'], resposta['categoria'], semana_atual, data_atual, date_time, resposta['resposta']))
                    db.commit()

                    if resposta['sugestao']:
                        cursor.execute('''
                            INSERT INTO sugestoes_fato (fk_subarea, fk_gestor, fk_cargo, idade, sexo, fk_pergunta, fk_categoria, semana, data, datetime, sugestao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                            ''', (subarea, gestor, cargo, idade, sexo, resposta['pergunta'], resposta['categoria'], semana_atual, data_atual, date_time, resposta['sugestao']))
                        db.commit()

                session.pop('perguntas_selecionadas', None)
                session.pop('pergunta_atual', None)
                session.pop('respostas', None)

                flash("Respostas enviadas com sucesso!","success")
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
    if 'subarea' not in session:
        return redirect(url_for('entrada'))

    if request.method == 'POST':
        if 'enviar_sugestao' in request.form:
            session.clear()
            return redirect(url_for('sugestao'))
    return render_template('final.html')

@app.route('/sugestao', methods=['GET', 'POST'])

def sugestao():
    db = get_db()
    cursor = db.cursor()

    date_time = datetime.datetime.now()
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
    semana_atual = datetime.datetime.now().isocalendar()[1]
    subareas = consulta_tabelas('desc_subarea','subarea_dim')
    cargos = consulta_tabelas('desc_cargo','cargo_dim')
    gestores = consulta_tabelas('desc_gestor','gestor_dim')
    categorias = consulta_tabelas('desc_categoria','categoria_dim')

    if request.method == 'POST':
        subarea = request.form.get('area', None)
        gestor = request.form.get('gestor', None)
        cargo = request.form.get('cargo', None)
        categoria = request.form.get('categoria', None)
        idade = request.form.get('idade', None)
        sexo = request.form.get('sexo', None)
        sugestao = request.form.get('sugestao', None)

        fk_subarea = consulta_tabelas('fk_subarea', 'subarea_dim', 'desc_subarea',subarea)[0]
        fk_gestor = consulta_tabelas('fk_gestor', 'gestor_dim', 'desc_gestor',gestor)[0]
        fk_cargo = consulta_tabelas('fk_cargo', 'cargo_dim', 'desc_cargo',cargo)[0]
        fk_categoria = consulta_tabelas('fk_categoria', 'categoria_dim', 'desc_categoria',categoria)[0]

        if None in (subarea, gestor, cargo, categoria, idade, sexo, sugestao):
            flash("Selecione as opções acima, todos os campos são obrigatórios.", "warning")
        else:
            cursor.execute('''
                INSERT INTO sugestoes_fato (fk_subarea, fk_gestor, fk_cargo, idade, sexo, fk_categoria, semana, data, datetime, sugestao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (fk_subarea, fk_gestor, fk_cargo, idade, sexo, fk_categoria, semana_atual, data_atual, date_time, sugestao))
            db.commit()

            flash("Sugestão enviada com sucesso!", "success")
            return redirect(url_for('final'))

    return render_template('sugestao.html', areas=subareas, gestores=gestores, cargos=cargos, categorias=categorias)

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
        return testa_id
    
    #Traz o fk_gestor para verificar quantas respostas do time dele existem
    def consulta_gestor(id_gestor):
        cursor.execute('SELECT fk_gestor, desc_gestor FROM gestor_dim WHERE id = ?',(id_gestor))
        dados_gestor = cursor.fetchone()
        fk_gestor, nome_gestor = dados_gestor
        return fk_gestor,nome_gestor
    
    def consulta_quantidade(tabela, fk_gestor, fk_categoria=None, fk_pergunta=None):
        if fk_categoria and fk_pergunta:
            cursor.execute(f'SELECT COUNT(*) FROM {tabela} WHERE fk_gestor = ? and fk_categoria = ? and fk_pergunta = ?',(fk_gestor,fk_categoria, fk_pergunta))
        elif fk_categoria:
            cursor.execute(f'SELECT COUNT(*) FROM {tabela} WHERE fk_gestor = ? and fk_categoria = ?',(fk_gestor,fk_categoria,))
        else:     
            cursor.execute(f'SELECT COUNT(*) FROM {tabela} WHERE fk_gestor = ?',(fk_gestor,))
        num_respostas = cursor.fetchone()[0]
        return num_respostas
    
    def consulta_media(coluna, tabela, fk_gestor, fk_categoria=None, fk_pergunta=None):
        if fk_categoria and fk_pergunta:
            cursor.execute(f'SELECT AVG({coluna}) FROM {tabela} WHERE fk_gestor = ? and fk_categoria = ? and fk_pergunta = ? and resposta >= 0',(fk_gestor,fk_categoria, fk_pergunta))
        elif fk_categoria:
            cursor.execute(f'SELECT AVG({coluna}) FROM {tabela} WHERE fk_gestor = ? and fk_categoria = ? and resposta >= 0',(fk_gestor,fk_categoria,))
        else:     
            cursor.execute(f'SELECT AVG({coluna}) FROM {tabela} WHERE fk_gestor = ? and resposta >= 0',(fk_gestor,))        
        nota_media = cursor.fetchone()[0]
        nota_media = round(nota_media,2)
        return nota_media
    
    def consulta_min_max(coluna, tabela, fk_gestor, fk_categoria=None, fk_pergunta=None):
        if fk_categoria and fk_pergunta:
            cursor.execute(f'SELECT min({coluna}), max({coluna}) FROM {tabela} WHERE fk_gestor = ? and fk_categoria = ? and fk_pergunta = ?',(fk_gestor,fk_categoria, fk_pergunta))
        elif fk_categoria:
            cursor.execute(f'SELECT min({coluna}), max({coluna}) FROM {tabela} WHERE fk_gestor = ? and fk_categoria = ?',(fk_gestor,fk_categoria,))
        else:     
            cursor.execute(f'SELECT min({coluna}), max({coluna}) FROM {tabela} WHERE fk_gestor = ?',(fk_gestor,)) 
        datas = cursor.fetchone()
        data_min, data_max = datas
        return data_min, data_max
    
    def consulta_sugestoes( tabela, fk_gestor, coluna=None , fk_categoria=None, fk_pergunta=None):
        if fk_categoria and fk_pergunta:
            cursor.execute(f'SELECT {coluna} FROM {tabela} WHERE fk_gestor = ? and fk_categoria = ? and fk_pergunta = ?',(fk_gestor,fk_categoria, fk_pergunta))
        elif fk_categoria:
            cursor.execute(f'SELECT {coluna} FROM {tabela} WHERE fk_gestor = ? and fk_categoria = ?',(fk_gestor,fk_categoria,))
        else:
            cursor.execute(f'SELECT * FROM sugestoes_fato WHERE fk_gestor = ?',(fk_gestor,)) 
        dados = cursor.fetchall()
        sugestoes = [dict(row) for row in dados]
        print(sugestoes)
        return sugestoes

    def gera_cards():
        categorias = consulta_categorias()
        cards = []
        for fk_categoria, desc_categoria in categorias:
            valor = consulta_media('resposta','respostas_fato', fk_gestor, fk_categoria)
            size_bar = valor * 10
            quantidade_respostas = consulta_quantidade('respostas_fato',fk_gestor,fk_categoria)
            data_min = consulta_min_max('data', 'respostas_fato', fk_gestor, fk_categoria)[0]
            data_max = consulta_min_max('data', 'respostas_fato', fk_gestor, fk_categoria)[1]
            card = {
                'id': fk_categoria,
                'title': desc_categoria,
                'size': size_bar,
                'value': valor,
                'total': 10,
                'qtd_respostas': quantidade_respostas,
                'data_min': data_min,
                'data_max': data_max
            }
            cards.append(card)
        return cards
    
    def gera_tabela():
        sugestoes = consulta_sugestoes('sugestoes_fato', fk_gestor)
        tabela = []
        for sugestao in sugestoes:
            data = sugestao['data']
            fk_categoria = sugestao['fk_categoria']
            cursor.execute(f'SELECT desc_categoria FROM categoria_dim WHERE fk_categoria = {fk_categoria}')
            categoria = cursor.fetchone()[0]
            sugestao = sugestao['sugestao']
            # respondido = bool(sugestao['respondido'],False)
            respondido = bool(False)
            print(data)
            row = {
                'data': data,
                'categoria': categoria,
                'sugestao': sugestao,
                'respondido': respondido
            }
            tabela.append(row)
        return tabela
    
    fk_gestor = consulta_gestor(id_gestor)[0]
    nome_gestor = consulta_gestor(id_gestor)[1]
    data_min = consulta_min_max('data', 'respostas_fato', fk_gestor)[0]
    data_max = consulta_min_max('data', 'respostas_fato', fk_gestor)[1]
    quantidade_respostas = consulta_quantidade('respostas_fato',fk_gestor)
    nota_media = consulta_media('resposta','respostas_fato',fk_gestor)
    size_bar = nota_media * 10 
    cards = gera_cards()
    tabela = gera_tabela()
    print(f'os cards são {cards}')
    print(f'a tabela é {tabela}')
    return render_template('dashboard.html', nome = nome_gestor, qtd_respostas = quantidade_respostas, nota_media = nota_media, size_bar = size_bar, cards=cards, data_min = data_min, data_max = data_max, tabela = tabela)

@app.route('/settings')
def settings():
    return render_template('settings.html')

def check_admin(username, password):
    admin_username = ADMIN_USERNAME
    admin_password_hash = ADMIN_PASSWORD
    return username == admin_username and password == admin_password_hash

if __name__ == '__main__':
    app.run(debug=True)