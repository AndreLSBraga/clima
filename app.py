from flask import Flask, render_template, request, redirect, url_for, flash, session, g, current_app, jsonify
import mysql.connector
import random
import datetime
import hashlib
from config import ADMIN_USERNAME, ADMIN_PASSWORD, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, ADMIN_LOGIN, ADMIN_LOGIN_SENHA
import uuid
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        g.db.cursor(buffered=True, dictionary=True)  # Configura o cursor para retornar resultados como dicionários
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
    cursor.execute('SELECT COUNT(*) FROM gestor_dim WHERE id_gestor = %s', (user_id,))
    result = cursor.fetchone()[0]
    cursor.close()
    return result > 0

def resposta_existe_esta_semana(user_id):
    semana_atual = datetime.datetime.now().isocalendar()[1]
    ano_atual = datetime.datetime.now().year
    
    cursor.execute('SELECT data FROM usuarios_respostas_fato WHERE id = %s', (user_id,))
    resultados = cursor.fetchall()
    cursor.close()
    
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
        flash("O Id não foi encontrado. Digite um Id válido","error")
        return redirect(url_for(destino))

    return None

def consulta_categorias():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT fk_categoria, desc_categoria FROM categoria_dim')
    categorias = cursor.fetchall() 
    cursor.close()
    return categorias

def consulta_tabelas(coluna, tabela, col_filtro = None, filtro = None):
    db = get_db()
    cursor = db.cursor()
    lista = []
    if filtro:
        cursor.execute(f'SELECT {coluna} FROM {tabela} WHERE {col_filtro} = %s', (filtro,)),
    else:
        cursor.execute(f'SELECT {coluna} FROM {tabela}')
    dados = cursor.fetchall()
    cursor.close()
    for dado in dados:
        item = dado[0]
        lista.append(item)
    
    return lista

def nome_meses(mes):
        meses = {
            '01': 'Janeiro',
            '02': 'Fevereiro',
            '03': 'Março',
            '04': 'Abril',
            '05': 'Maio',
            '06': 'Junho',
            '07': 'Julho',
            '08': 'Agosto',
            '09': 'Setembro',
            '10': 'Outubro',
            '11': 'Novembro',
            '12': 'Dezembro'
        }
        return meses[mes]

@app.route('/', methods=['GET', 'POST'])
def entrada():
    subareas = consulta_tabelas('desc_subarea','subarea_dim')
    cargos = consulta_tabelas('desc_cargo','cargo_dim')
    gestores = consulta_tabelas('desc_gestor','gestor_dim')

    if request.method == 'POST':
        subarea = request.form['area']
        gestor = request.form['gestor']
        cargo = request.form['cargo']

        fk_subarea = consulta_tabelas('fk_subarea', 'subarea_dim', 'desc_subarea',subarea)
        fk_gestor = consulta_tabelas('fk_gestor', 'gestor_dim', 'desc_gestor',gestor)
        fk_cargo = consulta_tabelas('fk_cargo', 'cargo_dim', 'desc_cargo',cargo)

        session['idade'] = request.form['idade']
        session['genero'] = request.form['genero']
        session['cargo'] = fk_cargo
        session['subarea'] = fk_subarea
        session['gestor'] = fk_gestor
        session['pergunta_atual'] = 0
        session['perguntas_selecionadas'] = []
        session['respostas'] = []

        if None in (session['idade'], session['genero'], session['cargo'], session['subarea'], session['gestor']):
            flash("Preencha todos os campos acima", "warning")
        else:
            return redirect(url_for('perguntas'))
        
    return render_template('entrada.html',areas=subareas, cargos=cargos, gestores=gestores)

@app.route('/gestores/<area>', methods=['GET'])
def get_gestores(area):
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT fk_area FROM area_dim WHERE desc_area = %s',(area,))
    fk_area = cursor.fetchone()[0]
    cursor.close()
    gestores = consulta_tabelas('desc_gestor', 'gestor_dim', 'fk_area', fk_area)
    return jsonify(gestores=gestores)

@app.route('/area/<gestor>', methods=['GET'])
def get_area_gestor(gestor):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT desc_area FROM area_dim WHERE fk_area = (SELECT fk_area FROM gestor_dim WHERE desc_gestor = %s)', (gestor,))
    area_result = cursor.fetchone()
    cursor.close()
    if area_result:
        area = area_result[0]
        return jsonify(area=area)
    else:
        return jsonify(area=None)
    
@app.route('/perguntas', methods=['GET', 'POST'])
def perguntas():
    idade = session['idade']
    # app.logger.debug(f"a idade é: {idade}, o session recebido é: {session}")
    def chama_perguntas():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_pergunta, fk_categoria FROM pergunta_dim')
        perguntas = cursor.fetchall()
        cursor.close()
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
    cursor.execute('SELECT desc_pergunta FROM pergunta_dim WHERE fk_pergunta = %s', (num_pergunta,))
    pergunta = cursor.fetchone()[0]
    cursor.execute('SELECT fk_categoria FROM pergunta_dim WHERE fk_pergunta = %s', (num_pergunta,))
    categoria = cursor.fetchone()[0]
    if request.method == 'POST':
        subarea = session['subarea'][0]
        gestor = session['gestor'][0]
        cargo = session['cargo'][0]
        idade = session['idade']
        genero = session['genero']       
        date_time = datetime.datetime.now()
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        semana_atual = datetime.datetime.now().isocalendar()[1]
        id = uuid.uuid4().hex

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
                        INSERT INTO respostas_fato (fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_pergunta, fk_categoria, semana, data, datetime, resposta)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''',  (subarea, gestor, cargo, idade, genero, resposta['pergunta'], resposta['categoria'], semana_atual, data_atual, date_time, resposta['resposta']))
                    db.commit()
                    print(f'Respostas inseridas no banco')

                    if resposta['sugestao']:
                        cursor.execute('''
                            INSERT INTO sugestoes_fato (id, fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_pergunta, fk_categoria, semana, data, datetime, sugestao, respondido)
                                VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (id,subarea, gestor, cargo, idade, genero, resposta['pergunta'], resposta['categoria'], semana_atual, data_atual, date_time, resposta['sugestao'], 0))
                        db.commit()
                        print(f'Sugestões inseridos no banco')

                session.pop('perguntas_selecionadas', None)
                session.pop('pergunta_atual', None)
                session.pop('respostas', None)
                
                flash("Respostas enviadas com sucesso!","success")
                
                cursor.close()
                return redirect(url_for('final'))

        elif 'anterior' in request.form:
            if pergunta_atual > 0:
                session['pergunta_atual'] = pergunta_atual - 1

        pergunta_atual = session.get('pergunta_atual', 0)
        pergunta_atual = int(pergunta_atual)
        num_pergunta = perguntas_selecionadas[pergunta_atual]
        cursor.execute('SELECT desc_pergunta FROM pergunta_dim WHERE fk_pergunta = %s', (num_pergunta,))
        pergunta = cursor.fetchone()[0]
        cursor.execute('SELECT fk_categoria FROM pergunta_dim WHERE fk_pergunta = %s', (num_pergunta,))
        categoria = cursor.fetchone()[0]
    return render_template('pergunta.html', pergunta=pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=15)

@app.route('/respondido', methods=['GET', 'POST'])
def final(): 
    if 'subarea' not in session:
        return redirect(url_for('entrada'))
    #Limpa os dados da sessão
    session.clear()
    if request.method == 'POST':
        if 'enviar_sugestao' in request.form:
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
        id = uuid.uuid4().hex
        subarea = request.form.get('area', None)
        session['subarea'] = subarea
        gestor = request.form.get('gestor', None)
        cargo = request.form.get('cargo', None)
        categoria = request.form.get('categoria', None)
        idade = request.form.get('idade', None)
        genero = request.form.get('genero', None)
        sugestao = request.form.get('sugestao', None)

        fk_subarea = consulta_tabelas('fk_subarea', 'subarea_dim', 'desc_subarea',subarea)[0]
        fk_gestor = consulta_tabelas('fk_gestor', 'gestor_dim', 'desc_gestor',gestor)[0]
        fk_cargo = consulta_tabelas('fk_cargo', 'cargo_dim', 'desc_cargo',cargo)[0]
        fk_categoria = consulta_tabelas('fk_categoria', 'categoria_dim', 'desc_categoria',categoria)[0]

        if None in (subarea, gestor, cargo, categoria, idade, genero, sugestao):
            flash("Selecione as opções acima, todos os campos são obrigatórios.", "warning")
        else:
            cursor.execute('''
                INSERT INTO sugestoes_fato (id, fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_categoria, semana, data, datetime, sugestao, respondido)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (id, fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_categoria, semana_atual, data_atual, date_time, sugestao, 0))
            db.commit()
            cursor.close()
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

@app.route('/settings')
def settings():
    return render_template('settings.html')

def check_admin(username, password):
    admin_username = ADMIN_LOGIN
    admin_password_hash = ADMIN_LOGIN_SENHA
    return username == admin_username and password == admin_password_hash

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    id_gestor = session['username']

    testa_id = valida_id(id_gestor,'login')
    if testa_id:
        return testa_id
    
    session['id'] = id_gestor

    def consulta_quantidade(tabela, fk_gestor, fk_categoria=None, fk_pergunta=None):
        db = get_db()
        cursor = db.cursor()
        if fk_categoria and fk_pergunta:
            cursor.execute(f'SELECT COUNT(*) FROM {tabela} WHERE fk_gestor = %s and fk_categoria = %s and fk_pergunta = %s',(fk_gestor,fk_categoria, fk_pergunta))
        elif fk_categoria:
            cursor.execute(f'SELECT COUNT(*) FROM {tabela} WHERE fk_gestor = %s and fk_categoria = %s',(fk_gestor,fk_categoria,))
        else:     
            cursor.execute(f'SELECT COUNT(*) FROM {tabela} WHERE fk_gestor = %s',(fk_gestor,))
        num_respostas = cursor.fetchone()[0]
        cursor.close()
        return num_respostas
    #Retorna caso não tenha respostas
    quantidade_respostas = consulta_quantidade('respostas_fato',id_gestor)
    
    if quantidade_respostas == 0:
        flash('Você ainda não tem respostas para avaliar', "warning")
        return render_template('login.html')
    
    #Traz o fk_gestor para verificar quantas respostas do time dele existem
    def consulta_gestor(fk_gestor):
        try:
            operation = f'SELECT fk_gestor, desc_gestor FROM gestor_dim WHERE id_gestor = %s LIMIT 1'
            params =  (fk_gestor)
            cursor.execute(operation, params)
            resultado = cursor.fetchone()[0]
            app.logger.debug(f"A consulta é: {operation, params}, o resultado é: {resultado}")
            cursor.close()
            
            if dados_gestor:
                fk_gestor, nome_gestor = dados_gestor
                return fk_gestor, nome_gestor
            else:
                fk_gestor, nome_gestor = None, None  # Ou outra ação adequada se nenhum resultado for encontrado
                return None, None
        except Exception as e:
            # Trate a exceção conforme necessário
            print(f"Erro ao consultar gestor: {e}")
            return None, None
        
    def consulta_media(coluna, tabela, fk_gestor, fk_categoria=None, fk_pergunta=None):
        try:
            if fk_categoria and fk_pergunta:
                operation = f'SELECT AVG({coluna}) FROM {tabela} WHERE fk_gestor = %s and fk_categoria = %s and fk_pergunta = %s and resposta >= %s'
                params = (fk_gestor,fk_categoria, fk_pergunta,0)
            elif fk_categoria:
                operation = f'SELECT AVG({coluna}) FROM {tabela} WHERE fk_gestor = %s and fk_categoria = %s and resposta >= %s'
                params = (fk_gestor, fk_categoria,0)
            else:     
                operation = f'SELECT AVG({coluna}) FROM {tabela} WHERE fk_gestor = %s and resposta >= %s'
                params =   (fk_gestor,0)
            db = get_db()
            cursor = db.cursor()
            cursor.execute(operation, params)
            resultado = cursor.fetchone()[0]
            cursor.close()
            
            if resultado is not None:
                nota_media = round(resultado, 1)
            else:
                nota_media = None
            
            return nota_media
            
        except mysql.connector.Error as err:
            print(f"Error Consulta Média: {err}", flush=True)
            return None
        
    
    def consulta_min_max(fk_gestor, fk_categoria=None, fk_pergunta=None):
        try:
            if fk_categoria and fk_pergunta:
                operation = 'SELECT min(data), max(data) FROM respostas_fato WHERE fk_gestor = %s and fk_categoria = %s and fk_pergunta = %s'
                params = (fk_gestor, fk_categoria, fk_pergunta)
 
            elif fk_categoria:
                operation = 'SELECT min(data), max(data) FROM respostas_fato WHERE fk_gestor = %s and fk_categoria = %s'
                params =  (fk_gestor, fk_categoria)

            else:
                operation = 'SELECT min(data), max(data) FROM respostas_fato WHERE fk_gestor = %s'
                params = (fk_gestor,)
            db = get_db()
            cursor = db.cursor()
            cursor.execute(operation, params)
            resultado = cursor.fetchone()
            cursor.close()
            if resultado:
                data_min, data_max = resultado
            else:
                data_min, data_max = None, None

            return data_min, data_max
        
        except mysql.connector.Error as err:
            print(f"Error: {err}", flush=True)
            return None, None

    def consulta_sugestoes( tabela, fk_gestor, coluna=None , fk_categoria=None, fk_pergunta=None):
        if fk_categoria and fk_pergunta:
            operation = f'SELECT {coluna} FROM {tabela} WHERE fk_gestor = %s and fk_categoria = %s and fk_pergunta = %s ORDER BY respondido ASC, datetime ASC'
            params = (fk_gestor,fk_categoria, fk_pergunta)
        elif fk_categoria:
            operation = f'SELECT {coluna} FROM {tabela} WHERE fk_gestor = %s and fk_categoria = %s ORDER BY respondido ASC, datetime DESC'
            params = (fk_gestor,fk_categoria)
        else:
            operation = f'SELECT * FROM sugestoes_fato WHERE fk_gestor = %s ORDER BY respondido ASC, datetime DESC'
            params = (fk_gestor,) 
        db = get_db()
        cursor = db.cursor()
        cursor.execute(operation, params)
        resultado = cursor.fetchall()
        
        cursor.close()
        sugestoes = []
        
        if not resultado:
            return None  # Retorna None se não houver sugestões
        else:
            for row in resultado:
                sugestoes.append(row)
            return sugestoes
    
    def consulta_filtros(coluna_procurada, tabela, fk_gestor):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f'SELECT DISTINCT {coluna_procurada} FROM {tabela} WHERE fk_gestor = %s', (fk_gestor,))
        dados = cursor.fetchall()
        cursor.close()
        filtros = []
        if not dados:
            return None  # Retorna None se não houver sugestões
        else:
            for row in dados:
                filtros.append(row)
            return filtros

    def gera_filtros(fk_gestor):
        fk_cargos = consulta_filtros('fk_cargo','respostas_fato', fk_gestor)
        
        cargos = []
        for fk_cargo in fk_cargos:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT desc_cargo FROM cargo_dim WHERE fk_cargo = %s', (fk_cargo))
            cargo = cursor.fetchone()[0]
            cargos.append(cargo)

        idades = consulta_filtros('idade','respostas_fato', fk_gestor)
        generos = consulta_filtros('genero','respostas_fato', fk_gestor)
        grupo_filtros = {
            'cargos': cargos,
            'idades': idades,
            'generos':generos
        }
        cursor.close()
        return grupo_filtros
    
    def gera_cards():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_categoria, desc_categoria FROM categoria_dim')
        categorias = cursor.fetchall()
        cards = []
        for fk_categoria, desc_categoria in categorias:
            valor = consulta_media('resposta','respostas_fato', id_gestor, fk_categoria)
            if valor is not None:
                valor = consulta_media('resposta','respostas_fato', id_gestor, fk_categoria)
                size_bar = valor * 10
            else:
                valor = None,
                size_bar = None
            quantidade_respostas = consulta_quantidade('respostas_fato',id_gestor,fk_categoria)
            dados_datas = consulta_min_max(id_gestor, fk_categoria)  
            data_min = dados_datas[0]
            data_max = dados_datas[1]
            
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
        cursor.close()
        return cards
    
    def gera_tabela():
        db = get_db()
        cursor = db.cursor()
        sugestoes = consulta_sugestoes('sugestoes_fato', fk_gestor)
        if sugestoes == None:
            return None
        
        tabela = []
        for sugestao in sugestoes:
            data = sugestao['data']
            fk_categoria = sugestao['fk_categoria']
            cursor.execute(f'SELECT desc_categoria FROM categoria_dim WHERE fk_categoria = {fk_categoria}')
            categoria = cursor.fetchone()[0]
            sugestao = sugestao['sugestao']
            respondido = sugestao['respondido']
            row = {
                'data': data,
                'categoria': categoria,
                'sugestao': sugestao,
                'respondido': respondido
            }
            tabela.append(row)
        cursor.close()
        return tabela
    
    def gera_grafico(fk_gestor):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f'''SELECT DISTINCT semana, DATE_FORMAT(data, '%m') AS mes FROM respostas_fato WHERE fk_gestor = {fk_gestor} ORDER BY semana asc''')
        datas = cursor.fetchall()
        grafico = []
       
        for semana, mes in datas:
            num_semana = semana
            num_mes = mes
            mes = nome_meses(num_mes)
            cursor.execute(f'SELECT AVG(resposta) FROM respostas_fato WHERE fk_gestor = {fk_gestor} and semana = {num_semana} and resposta >=0')
            nota = round(cursor.fetchone()[0],1)
            cursor.execute(f'SELECT COUNT(*) FROM respostas_fato WHERE fk_gestor = {fk_gestor} and semana = {num_semana}')
            num_respostas = cursor.fetchone()[0]

            dados = {
                'eixo_x': f'Semana: {num_semana} / {mes}',
                'nota': nota,
                'num_respostas': num_respostas
            }
            grafico.append(dados)
        cursor.close()
        return grafico

    dados_filtros = gera_filtros(id_gestor)
    dados_grafico = gera_grafico(id_gestor)
    dados_gestor = consulta_gestor(id_gestor)
    fk_gestor = dados_gestor[0]
    nome_gestor = dados_gestor[1]
    dados_datas = consulta_min_max(fk_gestor)  
    data_min = dados_datas[0]
    data_max = dados_datas[1]
    app.logger.debug(f'Datas: {data_max, data_min}, Gestor: {dados_gestor, fk_gestor}')
    nota_media = consulta_media('resposta','respostas_fato',id_gestor)
    if nota_media is not None:
        nota_media = consulta_media('resposta','respostas_fato',id_gestor)
        size_bar = nota_media * 10
    else:
        nota_media = None
        size_bar = None
    cards = gera_cards()
    tabela = gera_tabela()
    dados = [{
        'nome': consulta_gestor(id_gestor)[1],
        'qtd_respostas': consulta_quantidade('respostas_fato',id_gestor),
        'nota_media': nota_media,
        'size_bar': size_bar,
        'nota_nps': 10, #Criar lógica de consultar a nota do nps
        'size_nps': 10 * 10,
        'data_min':consulta_min_max('data', 'respostas_fato', id_gestor)[0],
        'data_max': consulta_min_max('data', 'respostas_fato', id_gestor)[1]
    }]
    return render_template('dashboard.html', dados=dados, nome = nome_gestor, qtd_respostas = quantidade_respostas, nota_media = nota_media, size_bar = size_bar, cards=cards, data_min = data_min, data_max = data_max, tabela = tabela, dados_grafico=dados_grafico, filtros=dados_filtros)

@app.route('/detalhes/<int:fk_categoria>')            
def get_detalhes(fk_categoria):
    id_gestor = session['id'][0]
    db = get_db()
    cursor = db.cursor()

    # Descrição da categoria
    cursor.execute('SELECT desc_categoria FROM categoria_dim WHERE fk_categoria = %s', (fk_categoria,))
    result = cursor.fetchone()
    categoria = result[0] if result else None

    if not categoria:
        return jsonify({
            "title": "Detalhes não encontrados",
            "content": "Nenhum detalhe disponível para este card.",
            "perguntas": []
        })

    # Perguntas
    cursor.execute('SELECT fk_pergunta, desc_pergunta FROM pergunta_dim WHERE fk_categoria = %s', (fk_categoria,))
    dados_perguntas = cursor.fetchall()
    perguntas = []
    cursor.execute('SELECT COUNT(*) FROM respostas_fato WHERE fk_gestor = %s and fk_categoria = %s', (id_gestor, fk_categoria))
    num_respostas = cursor.fetchone()[0]

    for fk_pergunta, desc_pergunta in dados_perguntas:
        operation = f'SELECT AVG(resposta) FROM respostas_fato WHERE fk_pergunta = %s and fk_gestor = %s and resposta >= 0'
        params =   (fk_pergunta, id_gestor)
        cursor.execute(operation, params)
        resultado = cursor.fetchone()[0]
        
        if resultado is not None:
            nota = round(resultado, 1)
            size = nota * 10
        else:
            nota = None
            size = None
        
        cursor.execute('SELECT COUNT(*) FROM respostas_fato WHERE fk_pergunta = %s AND fk_gestor = %s', (fk_pergunta, id_gestor))
        respostas = cursor.fetchone()[0]
        # Dados para o gráfico da pergunta
        cursor.execute('''
            SELECT semana,  DATE_FORMAT(data, '%m') AS mes, AVG(resposta) as nota
            FROM respostas_fato
            WHERE fk_pergunta = %s and fk_gestor = %s and resposta >= 0
            GROUP BY semana, mes
            ORDER BY semana ASC
        ''', (fk_pergunta, id_gestor))
        
        grafico = [{'eixo_x':  f'Semana: {semana} / {nome_meses(mes)}', 'nota': round(nota, 1)} for semana, mes, nota in cursor.fetchall()]
        perguntas.append({
            'fk_pergunta': fk_pergunta,
            'pergunta': desc_pergunta,
            'nota': nota,
            'respostas': respostas,
            'size': size,
            'grafico': grafico
        })

    details_data = {
        "title": categoria,
        "content": f'Abertura por pergunta da dimensão {categoria}, notas baseada em um total de {num_respostas} respostas.',
        "perguntas": perguntas
    }
    cursor.close()
    return jsonify(details_data)

if __name__ == '__main__':
    app.run(debug=True)
    db = get_db()
    cursor = db.cursor()