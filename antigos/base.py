from flask import Flask, render_template, request, redirect, url_for, flash, session, g, current_app, jsonify
import mysql.connector
import random
import datetime
import hashlib
from config import ADMIN_USERNAME, ADMIN_PASSWORD, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, ADMIN_LOGIN, ADMIN_SENHA
import uuid
import logging
import bcrypt


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

#Funções
def id_existe(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM gestor_dim WHERE id_gestor = %s', (user_id,))
    result = cursor.fetchone()[0]
    cursor.close()
    return result > 0

def resposta_existe_esta_semana(user_id):
    db = get_db()
    cursor = db.cursor()

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
        flash("O Id não foi encontrado","error")
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

def codifica_senha(senha):
        # Gera um salt
        salt = bcrypt.gensalt()
        # Gera o hash da senha com o salt
        senha_codificada = bcrypt.hashpw(senha.encode('utf-8'), salt)
        return senha_codificada

def decodifica_senha(senha_digitada, senha_codificada):
    return bcrypt.checkpw(senha_digitada.encode('utf-8'), senha_codificada.encode('utf-8'))

def check_admin(username, password):
    if(username == ADMIN_LOGIN and password == ADMIN_SENHA):
        return True
    else:
        return False

def consulta_sugestoes(tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None, fk_area=None, respondido=None,id_sugestao=None):
        query = f'SELECT * FROM {tabela}'
        params = []
        conditions = []

        if fk_gestor is not None:
            conditions.append('fk_gestor = %s')
            params.append(fk_gestor)
        if fk_categoria is not None:
            conditions.append('fk_categoria = %s')
            params.append(fk_categoria)
        if fk_pergunta is not None:
            conditions.append('fk_pergunta = %s')
            params.append(fk_pergunta)
        if respondido is not None:
            conditions.append('respondido = %s')
            params.append(respondido)
        if id_sugestao is not None:
            conditions.append('id_sugestao = %s')
            params.append(id_sugestao)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
            
        query += ' ORDER BY respondido ASC,datetime ASC'
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        resultado = cursor.fetchall()
        cursor.close()
        sugestoes = []
        
        if not resultado:
            return None
        else:
            for row in resultado:
                sugestoes.append(row)
            return sugestoes

def consulta_respostas_sugestao(id_sugestao):
    query = f'SELECT * FROM respostas_sugestoes_fato'
    params = []
    conditions = []

    if id_sugestao is not None:
        conditions.append('id_sugestao = %s')
        params.append(id_sugestao)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
        
    query += ' ORDER BY datetime ASC'
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    resultado = cursor.fetchall()
    cursor.close()
    respostas = []
    if not resultado:
            return None
    else:
        for row in resultado:
            respostas.append(row)
        return respostas
    
def consulta_categoria(fk_categoria):
    db = get_db()
    cursor = db.cursor()
    query = 'SELECT desc_categoria FROM categoria_dim WHERE fk_categoria = %s'
    params = (fk_categoria,)
    cursor.execute(query, params)
    resultado = cursor.fetchone()

    if resultado is not None:
        return resultado[0]
    else:
        return None
    
def consulta_pergunta(fk_pergunta):
    db = get_db()
    cursor = db.cursor()
    query = 'SELECT desc_pergunta FROM pergunta_dim WHERE fk_pergunta = %s'
    params = (fk_pergunta,)
    cursor.execute(query, params)
    resultado = cursor.fetchone()

    if resultado is not None:
        return resultado[0]
    else:
        return None
    
def consulta_gestor(id_gestor):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_gestor, nome, fk_area, desc_gestor FROM gestor_dim WHERE id_gestor = %s',(id_gestor,))
        dados = cursor.fetchone()
        fk_gestor = dados[0]
        nome_gestor = dados[1]
        fk_area = dados[2]
        desc_gestor = dados[3]
        cursor.close()
        return fk_gestor, nome_gestor, fk_area, desc_gestor
    
def consulta_quantidade(tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None):
    
    query = f'SELECT COUNT(*) FROM {tabela} WHERE resposta >= 0'
    params = []

    if fk_gestor is not None:
        query += ' AND fk_gestor = %s'
        params.append(fk_gestor)
    if fk_categoria is not None:
        query += ' AND fk_categoria = %s'
        params.append(fk_categoria)
    if fk_pergunta is not None:
        query += ' AND fk_pergunta = %s'
        params.append(fk_pergunta)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, tuple(params))
    num_respostas = cursor.fetchone()[0]
    cursor.close()
    return num_respostas

def consulta_quantidade_sugestoes(tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None, respondido = None):
    
    query = f'SELECT COUNT(*) FROM {tabela}'
    params = []
    conditions = []

    if fk_gestor is not None:
        conditions.append('fk_gestor = %s')
        params.append(fk_gestor)
    if fk_categoria is not None:
        conditions.append('fk_categoria = %s')
        params.append(fk_categoria)
    if fk_pergunta is not None:
        conditions.append('fk_pergunta = %s')
        params.append(fk_pergunta)
    if respondido is not None:
        conditions.append('respondido = %s')
        params.append(respondido)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, tuple(params))
    resultado = cursor.fetchone()[0]
    cursor.close()
    if resultado is not None:
        return resultado
    else:
        return None

def consulta_puladas(tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None):

    query = f'SELECT COUNT(*) FROM {tabela} WHERE resposta < 0'
    params = []

    if fk_gestor is not None:
        query += ' AND fk_gestor = %s'
        params.append(fk_gestor)
    if fk_categoria is not None:
        query += ' AND fk_categoria = %s'
        params.append(fk_categoria)
    if fk_pergunta is not None:
        query += ' AND fk_pergunta = %s'
        params.append(fk_pergunta)
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, tuple(params))
    num_respostas = cursor.fetchone()[0]
    cursor.close()
    return num_respostas

def consulta_media(coluna, tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None):
    try:
        query = f'SELECT AVG({coluna}) FROM {tabela} WHERE resposta >=0'
        params = []

        if fk_gestor is not None:
            query += ' AND fk_gestor = %s'
            params.append(fk_gestor)
        if fk_categoria is not None:
            query += ' AND fk_categoria = %s'
            params.append(fk_categoria)
        if fk_pergunta is not None:
            query += ' AND fk_pergunta = %s'
            params.append(fk_pergunta)

        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        resultado = cursor.fetchone()[0]
        cursor.close()
        
        if resultado is not None:
            nota_media = round(resultado, 1)
            size_bar = nota_media * 10
        else:
            nota_media = None
            size_bar = None
        
        return nota_media, size_bar
        
    except mysql.connector.Error as err:
        print(f"Error Consulta Média: {err}", flush=True)
        return None

def consulta_min_max(tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None):
    try:
        query = f'SELECT min(data), max(data) FROM {tabela} WHERE resposta >= 0'
        params = []

        if fk_gestor is not None:
            query += ' AND fk_gestor = %s'
            params.append(fk_gestor)
        if fk_categoria is not None:
            query += ' AND fk_categoria = %s'
            params.append(fk_categoria)
        if fk_pergunta is not None:
            query += ' AND fk_pergunta = %s'
            params.append(fk_pergunta)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado and resultado[0] and resultado[1]:
            data_min, data_max = resultado
            data_min = data_min.strftime("%d-%m-%y")
            data_max = data_max.strftime("%d-%m-%y")
        else:
            data_min, data_max = None, None

        return data_min, data_max
    
    except mysql.connector.Error as err:
        print(f"Error: {err}", flush=True)
        return None, None

def consulta_filtros(coluna_procurada, tabela, fk_gestor=None):

    query = f'SELECT DISTINCT {coluna_procurada} FROM {tabela}'
    params = []
    conditions = []

    if fk_gestor is not None:
        conditions.append('fk_gestor = %s')
        params.append(fk_gestor)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, tuple(params))
    dados = cursor.fetchall()
    cursor.close()
    filtros = []
    if not dados:
        return None
    else:
        for row in dados:
            filtros.append(row)
        return filtros
    
def gera_filtros(fk_gestor=None):

    fk_cargos = consulta_filtros('fk_cargo','respostas_fato', fk_gestor)
    
    if not fk_cargos:
        return None
    
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

def gera_cards(fk_gestor=None):

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT fk_categoria, desc_categoria FROM categoria_dim')
    categorias = cursor.fetchall()
    cards = []

    for fk_categoria, desc_categoria in categorias:
        valor = consulta_media('resposta','respostas_fato', fk_gestor, fk_categoria)[0]
        size_bar = consulta_media('resposta','respostas_fato', fk_gestor, fk_categoria)[1]
        quantidade_respostas = consulta_quantidade('respostas_fato',fk_gestor,fk_categoria)
        quantidade_puladas = consulta_puladas('respostas_fato',fk_gestor,fk_categoria)
        dados_datas = consulta_min_max('respostas_fato',fk_gestor, fk_categoria)
        data_min = dados_datas[0]
        data_max = dados_datas[1]
        
        card = {

            'id': fk_categoria,
            'title': desc_categoria,
            'size': size_bar,
            'value': valor,
            'total': 10,
            'qtd_respostas': quantidade_respostas,
            'qtd_puladas': quantidade_puladas,
            'data_min': data_min,
            'data_max': data_max
        }
        cards.append(card)
    cursor.close()
    return cards

def gera_tabela(fk_gestor=None):
    
    sugestoes = consulta_sugestoes('sugestoes_fato', fk_gestor)

    if sugestoes == None:
        return None

    tabela = []
    for sugestao in sugestoes:
        
        id_sugestao = sugestao['id_sugestao']
        data = sugestao['data']
        fk_categoria = sugestao['fk_categoria']
        fk_pergunta = sugestao['fk_pergunta']
        fk_subarea = sugestao['fk_subarea'] 
        texto_sugestao = sugestao['sugestao']
        respondido = sugestao['respondido']
        fk_gestor = sugestao['fk_gestor']

        if respondido == 1:
            status = 'Respondida'
        else:
            status = 'Pendente'

        categoria = consulta_categoria(fk_categoria)
        pergunta = consulta_pergunta(fk_pergunta)
        gestor = consulta_tabelas('desc_gestor','gestor_dim','fk_gestor',fk_gestor)[0]
        row = {
            'id_sugestao': id_sugestao,
            'status': status,
            'gestor': gestor,
            'data': data,
            'categoria': categoria,
            'pergunta': pergunta,
            'sugestao': texto_sugestao,
            'respondido': respondido
        }
        tabela.append(row)
    
    return tabela

def gera_grafico(fk_gestor=None):

    query = f'''SELECT DISTINCT semana, DATE_FORMAT(data, '%m')AS mes FROM respostas_fato '''
    params = []
    conditions = []

    if fk_gestor is not None:
        conditions.append('fk_gestor = %s')
        params.append(fk_gestor)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, tuple(params))
    datas = cursor.fetchall()
    grafico = []
    
    for semana, mes in datas:
        num_semana = semana
        num_mes = mes
        mes = nome_meses(num_mes)

        query_nota = f'SELECT AVG(resposta) FROM respostas_fato WHERE resposta >= 0 AND semana = {num_semana}'
        query_qtd = f'SELECT COUNT(*) FROM respostas_fato WHERE resposta >= 0 AND semana = {num_semana}'
        params = []

        if fk_gestor is not None:
            query_nota += ' AND fk_gestor = %s'
            query_qtd += ' AND fk_gestor = %s'
            params.append(fk_gestor)

        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query_nota, params)
        nota = round(cursor.fetchone()[0],1)
        cursor.execute(query_qtd, tuple(params))
        num_respostas = cursor.fetchone()[0]           

        dados = {
            'eixo_x': f'Semana: {num_semana} / {mes}',
            'nota': nota,
            'num_respostas': round(num_respostas/10,0)
        }
        grafico.append(dados)
    cursor.close()
    return grafico

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
        session['pergunta_atual'] = 0
        for grupo in grupos_perguntas.values():
            selecionadas = random.sample(grupo, min(1, len(grupo)))
            perguntas_selecionadas += selecionadas
        if len(perguntas_selecionadas) >= 10:
            session['perguntas_selecionadas'] = random.sample(perguntas_selecionadas, 10)
        else:
            session['perguntas_selecionadas'] = perguntas_selecionadas

    pergunta_atual = session['pergunta_atual']
    perguntas_selecionadas = session['perguntas_selecionadas']
    num_pergunta = perguntas_selecionadas[pergunta_atual]
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT fk_categoria FROM pergunta_dim WHERE fk_pergunta = %s', (num_pergunta,))
    categoria = cursor.fetchone()[0]
    cursor.execute('SELECT desc_pergunta FROM pergunta_dim WHERE fk_pergunta = %s', (num_pergunta,))
    texto_pergunta = cursor.fetchone()[0]
    
    if pergunta_atual >= len(perguntas_selecionadas):
        return redirect(url_for('final'))

    if request.method == 'POST':
        subarea = session['subarea'][0]
        gestor = session['gestor'][0]
        cargo = session['cargo'][0]
        idade = session['idade']
        genero = session['genero']       
        date_time = datetime.datetime.now()
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        semana_atual = datetime.datetime.now().isocalendar()[1]
        

        if 'anterior' in request.form:
            if pergunta_atual > 0:
                pergunta_atual = pergunta_atual - 1
                session['pergunta_atual'] = pergunta_atual

        if 'pular' in request.form or 'pular-inicial' in request.form:
            existing_response = next((res for res in session['respostas'] if res['pergunta'] == num_pergunta), None)
            if existing_response:
                existing_response['resposta'] = -1
                existing_response['sugestao'] = ''
            else:
                session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': -1, 'sugestao': ''})

            if pergunta_atual < len(perguntas_selecionadas) - 1:
                pergunta_atual = pergunta_atual +  1
                session['pergunta_atual'] = pergunta_atual

        if 'proxima' in request.form or 'enviar-inicial' in request.form:
            resposta = request.form['resposta']
            sugestao = request.form.get('sugestao', '')
            try:
                resposta = float(resposta)
            except ValueError:
                flash("A resposta deve ser um número entre 0 e 10.", "warning")
                return render_template('pergunta.html', pergunta=texto_pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=10)

            existing_response = next((res for res in session['respostas'] if res['pergunta'] == num_pergunta), None)
            if existing_response:
                existing_response['resposta'] = resposta
                existing_response['sugestao'] = sugestao
            else:
                session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': resposta, 'sugestao': sugestao})

            if pergunta_atual < len(perguntas_selecionadas) - 1:
                pergunta_atual = pergunta_atual +  1
                session['pergunta_atual'] = pergunta_atual

        if 'enviar-final' in request.form or 'pular-final' in request.form:
            if 'enviar-final' in request.form:
                resposta = float(request.form['resposta'])
                sugestao = request.form.get('sugestao', '')
                existing_response = next((res for res in session['respostas'] if res['pergunta'] == num_pergunta), None)
                if existing_response:
                    existing_response['resposta'] = resposta
                    existing_response['sugestao'] = sugestao
                else:
                    session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': resposta, 'sugestao': sugestao})

            elif 'pular-final' in request.form:
                session['respostas'].append({'categoria': categoria, 'pergunta': num_pergunta, 'resposta': -1, 'sugestao': ''})
        
            for resposta in session['respostas']:
                    cursor.execute('''
                        INSERT INTO respostas_fato (fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_pergunta, fk_categoria, semana, data, datetime, resposta)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''',  (subarea, gestor, cargo, idade, genero, resposta['pergunta'], resposta['categoria'], semana_atual, data_atual, date_time, resposta['resposta']))
                    db.commit()

                    if resposta['sugestao']:
                        id_sugestao = uuid.uuid4().hex
                        cursor.execute('''
                            INSERT INTO sugestoes_fato (id_sugestao, fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_pergunta, fk_categoria, semana, data, datetime, sugestao, respondido)
                                VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (id_sugestao,subarea, gestor, cargo, idade, genero, resposta['pergunta'], resposta['categoria'], semana_atual, data_atual, date_time, resposta['sugestao'], 0))
                        db.commit()
                        print(f'Sugestões inseridos no banco')

            session.pop('perguntas_selecionadas', None)
            session.pop('pergunta_atual', None)
            session.pop('respostas', None)    
            flash("Respostas enviadas com sucesso!","success")
            cursor.close()
            return redirect(url_for('final'))
    
    pergunta_atual = session['pergunta_atual']
    perguntas_selecionadas = session['perguntas_selecionadas']
    num_pergunta = perguntas_selecionadas[pergunta_atual]
    cursor.execute('SELECT fk_categoria FROM pergunta_dim WHERE fk_pergunta = %s', (num_pergunta,))
    categoria = cursor.fetchone()[0]
    cursor.execute('SELECT desc_pergunta FROM pergunta_dim WHERE fk_pergunta = %s', (num_pergunta,))
    texto_pergunta = cursor.fetchone()[0]

    return render_template('pergunta.html', pergunta=texto_pergunta, pergunta_num=pergunta_atual + 1, total_perguntas=10)

@app.route('/respondido', methods=['GET', 'POST'])
def final(): 
    
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
        id_sugestao = uuid.uuid4().hex
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
                INSERT INTO sugestoes_fato (id_sugestao, fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_categoria, semana, data, datetime, sugestao, respondido)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (id_sugestao, fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_categoria, semana_atual, data_atual, date_time, sugestao, 0))
            db.commit()
            cursor.close()
            flash("Sugestão enviada com sucesso!", "success")
            return redirect(url_for('final'))
        

    return render_template('sugestao.html', areas=subareas, gestores=gestores, cargos=cargos, categorias=categorias)
   
@app.route('/login', methods=['GET', 'POST'])
def login():   

    if request.method == 'POST':
        usuario = request.form['username']
        senha = request.form['password']

        if check_admin(usuario, senha) == True:
            session['perfil'] = 'admin'
            session['logged_in'] = True
            session['id'] = usuario
            return redirect(url_for('dashboard'))
        
        if not usuario.isdigit():
            flash("Digite apenas números no ID","error")
            return redirect(url_for('login'))
        
        db = get_db()
        cursor = db.cursor()
        #Consulta fk_gestor
        cursor.execute('SELECT fk_gestor FROM gestor_dim WHERE id_gestor = %s',(usuario,))
        dados_gestor = cursor.fetchone()

        if not dados_gestor:
            flash("Id não encontrado na base de gestores","error")
            return redirect(url_for('login'))
        else:            
            fk_gestor = dados_gestor[0]
            session['fk_gestor'] = fk_gestor

        cursor.execute('SELECT senha, tipo_usuario , logou FROM usuarios WHERE fk_gestor = %s',(fk_gestor,))
        dados_usuarios = cursor.fetchone()
        cursor.close()
        senha_db = dados_usuarios[0]
        perfil = dados_usuarios[1]
        logou = dados_usuarios[2]
                
        if not logou:
            if senha != 'pulsa7l':
                flash("Senha incorreta. Digite a senha correta","error")
                return redirect(url_for('login'))
            return redirect(url_for('configura_senha'))
        
        check_senha = decodifica_senha(senha, senha_db)
        if not check_senha:
            flash("Senha incorreta. Digite a senha correta","error")
            return redirect(url_for('login'))
        
        session['logged_in'] = True
        session['id'] = usuario
        session['perfil'] = perfil
            
        return redirect(url_for('dashboard'))
            
    return render_template('login.html')

@app.route('/configura_senha', methods=['GET', 'POST'])
def configura_senha():
    fk_gestor = session['fk_gestor']
    if request.method == 'POST':
        senha_anterior = request.form['past_password']
        senha_nova = request.form['new_password']
        senha_confirmacao = request.form['confirmed_password']

        if(senha_anterior != 'pulsa7l'):
            flash("A senha anterior está incorreta", "error")
            return render_template('configura_senha.html')
        
        if(senha_nova != senha_confirmacao):
            flash("A senha nova e a confirmação estão diferentes", "error")
            return render_template('configura_senha.html')
        
        senha_codificada = codifica_senha(senha_nova)
        db = get_db()
        cursor = db.cursor()
        #Atualiza senha nova no banco
        cursor.execute('UPDATE usuarios SET senha = %s, logou = 1 WHERE fk_gestor = %s',(senha_codificada, fk_gestor))
        db.commit()
        flash('Senha nova cadastrada',"success")
        return redirect(url_for('login'))
    return render_template('configura_senha.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/settings')
def settings():
    return render_template('settings.html')
        
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        flash('É necessário fazer login primeiro',"warning")
        return redirect(url_for('login'))

    usuario = session['id']
    perfil = session['perfil']
    
    if perfil == 'admin':
        nome_gestor = 'Administrador'
        dados_filtros = gera_filtros()
        dados_grafico = gera_grafico()
        cards = gera_cards()
        tabela = gera_tabela()

        dados = [{
            'nome': nome_gestor,
            'qtd_respostas': consulta_quantidade('respostas_fato'),
            'qtd_puladas': consulta_puladas('respostas_fato'),
            'nota_media': consulta_media('resposta','respostas_fato')[0],
            'size_bar': consulta_media('resposta','respostas_fato')[1],
            'data_min':consulta_min_max('respostas_fato')[0],
            'data_max': consulta_min_max('respostas_fato')[1],
            'qtd_nps':consulta_quantidade('respostas_fato',None,7,29),
            'qtd_puladas_nps': consulta_puladas('respostas_fato',None,7,29),
            'nota_nps': consulta_media('resposta','respostas_fato',None,7,29)[0],
            'size_nps': consulta_media('resposta','respostas_fato',None,7,29)[1],
            'data_min_nps':consulta_min_max('respostas_fato',None,7,29)[0],
            'data_max_nps': consulta_min_max('respostas_fato',None,7,29)[1],
            'qtd_psico':consulta_quantidade('respostas_fato',None,10),
            'qtd_puladas_psico': consulta_puladas('respostas_fato',None,10),
            'nota_psico':consulta_media('resposta','respostas_fato',None,10)[0],
            'size_psico':consulta_media('resposta','respostas_fato',None,10)[1],
            'data_min_psico':consulta_min_max('respostas_fato',None,10)[0],
            'data_max_psico': consulta_min_max('respostas_fato',None,10)[1],
            'qtd_sugestoes': consulta_quantidade_sugestoes('sugestoes_fato'),
            'qtd_sugestoes_respondidas': consulta_quantidade_sugestoes('sugestoes_fato',None, None, None, 1),
            'qtd_sugestoes_pendentes': consulta_quantidade_sugestoes('sugestoes_fato',None, None, None, 0)
        }]
        return render_template('dashboard.html', perfil=perfil, dados=dados, cards=cards, tabela = tabela, dados_grafico=dados_grafico, filtros=dados_filtros)
    else:
        id_gestor = consulta_gestor(usuario)[0]
        nome_gestor = consulta_gestor(usuario)[1]
        session['id_gestor'] = id_gestor

        dados_filtros = gera_filtros(id_gestor)
        dados_grafico = gera_grafico(id_gestor)
        cards = gera_cards(id_gestor)
        tabela = gera_tabela(id_gestor)

        dados = [{
            'nome': nome_gestor,
            'qtd_respostas': consulta_quantidade('respostas_fato',id_gestor),
            'qtd_puladas': consulta_puladas('respostas_fato',id_gestor),
            'nota_media': consulta_media('resposta','respostas_fato',id_gestor)[0],
            'size_bar': consulta_media('resposta','respostas_fato',id_gestor)[1],
            'data_min':consulta_min_max('respostas_fato',id_gestor)[0],
            'data_max': consulta_min_max('respostas_fato',id_gestor)[1],
            'qtd_nps':consulta_quantidade('respostas_fato',id_gestor,7,29),
            'qtd_puladas_nps': consulta_puladas('respostas_fato',id_gestor,7,29),
            'nota_nps': consulta_media('resposta','respostas_fato',id_gestor,7,29)[0],
            'size_nps': consulta_media('resposta','respostas_fato',id_gestor,7,29)[1],
            'data_min_nps':consulta_min_max('respostas_fato',id_gestor,7,29)[0],
            'data_max_nps': consulta_min_max('respostas_fato',id_gestor,7,29)[1],
            'qtd_psico':consulta_quantidade('respostas_fato',id_gestor,10),
            'qtd_puladas_psico': consulta_puladas('respostas_fato',id_gestor,10),
            'nota_psico':consulta_media('resposta','respostas_fato',id_gestor,10)[0],
            'size_psico':consulta_media('resposta','respostas_fato',id_gestor,10)[1],
            'data_min_psico':consulta_min_max('respostas_fato',id_gestor,10)[0],
            'data_max_psico': consulta_min_max('respostas_fato',id_gestor,10)[1],
            'qtd_sugestoes': consulta_quantidade_sugestoes('sugestoes_fato',id_gestor),
            'qtd_sugestoes_respondidas': consulta_quantidade_sugestoes('sugestoes_fato',id_gestor, None, None, 1),
            'qtd_sugestoes_pendentes': consulta_quantidade_sugestoes('sugestoes_fato',id_gestor, None, None, 0)
        }]
        
        return render_template('dashboard.html', perfil=perfil, dados=dados, cards=cards, tabela = tabela, dados_grafico=dados_grafico, filtros=dados_filtros)

@app.route('/dashboard_geral')
def dashboard_geral():
    if 'logged_in' not in session:
        flash('É necessário fazer login primeiro',"warning")
        return redirect(url_for('login'))

    usuario = session['id']
    perfil = session['perfil']
    
    if perfil == 'admin':
        nome_gestor = 'Administrador'
    else:
        id_gestor = consulta_gestor(usuario)[0]
        nome_gestor = consulta_gestor(usuario)[1]
        fk_area = consulta_gestor(usuario)[2]

    dados_filtros = gera_filtros()
    dados_grafico = gera_grafico()
    cards = gera_cards()
    tabela = gera_tabela()

    dados = [{
        'nome': nome_gestor,
        'qtd_respostas': consulta_quantidade('respostas_fato'),
        'qtd_puladas': consulta_puladas('respostas_fato'),
        'nota_media': consulta_media('resposta','respostas_fato')[0],
        'size_bar': consulta_media('resposta','respostas_fato')[1],
        'data_min':consulta_min_max('respostas_fato')[0],
        'data_max': consulta_min_max('respostas_fato')[1],
        'qtd_nps':consulta_quantidade('respostas_fato',None,7,29),
        'qtd_puladas_nps': consulta_puladas('respostas_fato',None,7,29),
        'nota_nps': consulta_media('resposta','respostas_fato',None,7,29)[0],
        'size_nps': consulta_media('resposta','respostas_fato',None,7,29)[1],
        'data_min_nps':consulta_min_max('respostas_fato',None,7,29)[0],
        'data_max_nps': consulta_min_max('respostas_fato',None,7,29)[1],
        'qtd_psico':consulta_quantidade('respostas_fato',None,10),
        'qtd_puladas_psico': consulta_puladas('respostas_fato',None,10),
        'nota_psico':consulta_media('resposta','respostas_fato',None,10)[0],
        'size_psico':consulta_media('resposta','respostas_fato',None,10)[1],
        'data_min_psico':consulta_min_max('respostas_fato',None,10)[0],
        'data_max_psico': consulta_min_max('respostas_fato',None,10)[1],
        'qtd_sugestoes': consulta_quantidade_sugestoes('sugestoes_fato'),
        'qtd_sugestoes_respondidas': consulta_quantidade_sugestoes('sugestoes_fato',None, None, None, 1),
        'qtd_sugestoes_pendentes': consulta_quantidade_sugestoes('sugestoes_fato',None, None, None, 0)
    }]

    return render_template('dashboard_geral.html', perfil=perfil, dados=dados, cards=cards, tabela = tabela, dados_grafico=dados_grafico, filtros=dados_filtros)

@app.route('/filtro_tabela')
def filtro_tabela():
    origem = request.args.get('origem')
    status = request.args.get('status')
    perfil = session['perfil']
    fk_gestor = session['fk_gestor']
    
    if status == 'todos':
        dados = consulta_sugestoes('sugestoes_fato',fk_gestor)
    elif status == 'respondidas':
        dados = consulta_sugestoes('sugestoes_fato',fk_gestor,None,None,None,1)
    elif status == 'pendentes':
        dados = consulta_sugestoes('sugestoes_fato',fk_gestor,None,None,None,0)
    else:
        dados = []

    if dados == None:
        dados_formatados = None
    else:
        dados_formatados = []
        for sugestao in dados:
            data = sugestao['data'].strftime('%Y-%m-%d')
            fk_categoria = sugestao['fk_categoria']
            fk_pergunta = sugestao['fk_pergunta']
            fk_subarea = sugestao['fk_subarea'] 
            texto_sugestao = sugestao['sugestao']
            respondido = sugestao['respondido']
            fk_gestor = sugestao['fk_gestor']

            if respondido == 1:
                status = 'Respondida'
            else:
                status = 'Pendente'

            categoria = consulta_categoria(fk_categoria)
            pergunta = consulta_pergunta(fk_pergunta)
            gestor = consulta_tabelas('desc_gestor','gestor_dim','fk_gestor',fk_gestor)[0]

            dado_formatado = {
                'id_sugestao': sugestao['id_sugestao'],
                'gestor': gestor,
                'status': status,
                'data': data,
                'categoria': categoria, 
                'pergunta': pergunta,
                'sugestao': texto_sugestao,
                'respondido': respondido
            }
            dados_formatados.append(dado_formatado)
    app.logger.debug(dados_formatados)
    return jsonify(tabela=dados_formatados)

@app.route('/filtro_tabela_geral')
def filtro_tabela_geral():
    origem = request.args.get('origem')
    status = request.args.get('status')
    perfil = session['perfil']
    fk_gestor = session['fk_gestor']      

    if status == 'todos':
        dados = consulta_sugestoes('sugestoes_fato',None)
    elif status == 'respondidas':
        dados = consulta_sugestoes('sugestoes_fato',None,None,None,None,1)
    elif status == 'pendentes':
        dados = consulta_sugestoes('sugestoes_fato',None,None,None,None,0)
    else:
        dados = []

    if dados == None:
        dados_formatados = None
    else:
        dados_formatados = []
        for sugestao in dados:
            data = sugestao['data'].strftime('%Y-%m-%d')
            fk_categoria = sugestao['fk_categoria']
            fk_pergunta = sugestao['fk_pergunta']
            fk_subarea = sugestao['fk_subarea'] 
            texto_sugestao = sugestao['sugestao']
            respondido = sugestao['respondido']
            fk_gestor = sugestao['fk_gestor']

            if respondido == 1:
                status = 'Respondida'
            else:
                status = 'Pendente'

            categoria = consulta_categoria(fk_categoria)
            pergunta = consulta_pergunta(fk_pergunta)
            gestor = consulta_tabelas('desc_gestor','gestor_dim','fk_gestor',fk_gestor)[0]

            dado_formatado = {
                'id_sugestao': sugestao['id_sugestao'],
                'gestor': gestor,
                'status': status,
                'data': data,
                'categoria': categoria, 
                'pergunta': pergunta,
                'sugestao': texto_sugestao,
                'respondido': respondido
            }
            dados_formatados.append(dado_formatado)
    app.logger.debug(dados_formatados)
    return jsonify(tabela=dados_formatados)

@app.route('/detalhes/<int:fk_categoria>')            
def get_detalhes(fk_categoria):
       
    def consulta_categorias():
        query = 'SELECT desc_categoria FROM categoria_dim WHERE fk_categoria = %s'
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, (fk_categoria,))
        dados = cursor.fetchone()
        cursor.close()
        if dados is not None:
            resultado = dados[0]
            return resultado
        else:
            return jsonify({
            "title": "Detalhes não encontrados",
            "content": "Nenhum detalhe disponível para este card.",
            "perguntas": []
        })
    
    def consulta_perguntas(fk_categoria):
        query = 'SELECT fk_pergunta, desc_pergunta FROM pergunta_dim WHERE fk_categoria = %s'
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, (fk_categoria,))
        dados = cursor.fetchall()
        cursor.close()
        if dados is not None:
            return dados
        else:
            return None
        
    def consulta_quantidade(tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None, operador = None):
        
        query = f'SELECT COUNT(*) FROM {tabela} WHERE resposta {operador} 0'
        params = []

        if fk_gestor is not None:
            query += ' AND fk_gestor = %s'
            params.append(fk_gestor)
        if fk_categoria is not None:
            query += ' AND fk_categoria = %s'
            params.append(fk_categoria)
        if fk_pergunta is not None:
            query += ' AND fk_pergunta = %s'
            params.append(fk_pergunta)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        num_respostas = cursor.fetchone()[0]
        cursor.close()
        return num_respostas
    
    def consulta_nota(tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None):
        query = f'SELECT AVG(resposta) FROM {tabela} WHERE resposta >= 0'
        params = []

        if fk_gestor is not None:
            query += ' AND fk_gestor = %s'
            params.append(fk_gestor)
        if fk_categoria is not None:
            query += ' AND fk_categoria = %s'
            params.append(fk_categoria)
        if fk_pergunta is not None:
            query += ' AND fk_pergunta = %s'
            params.append(fk_pergunta)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        resultado = cursor.fetchone()[0]
        cursor.close()
        if resultado is not None:
            nota = round(resultado,1)
            size = nota * 10
            return nota, size
        else:
            return None, None
        
    def consulta_datas(tabela, fk_gestor=None, fk_categoria=None, fk_pergunta=None):
        query = f'SELECT Min(data), Max(data) FROM {tabela} WHERE resposta >= 0'
        params = []

        if fk_gestor is not None:
            query += ' AND fk_gestor = %s'
            params.append(fk_gestor)
        if fk_categoria is not None:
            query += ' AND fk_categoria = %s'
            params.append(fk_categoria)
        if fk_pergunta is not None:
            query += ' AND fk_pergunta = %s'
            params.append(fk_pergunta)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        resultado = cursor.fetchone()
        cursor.close()
        if resultado:
            data_min = resultado[0]
            data_max = resultado[1]
            return data_min, data_max
        else:
            return None, None
    
    def gera_dados_grafico(fk_gestor=None, fk_pergunta=None):
        query = '''
        SELECT
            semana,
            DATE_FORMAT(data, '%m') as mes,
            AVG(resposta) as nota
        FROM
            respostas_fato
        WHERE 
            resposta >=0
        '''
        params = []

        if fk_gestor is not None:
            query += ' AND fk_gestor = %s'
            params.append(fk_gestor)
        if fk_pergunta is not None:
            query += ' AND fk_pergunta = %s'
            params.append(fk_pergunta)

        query += ' GROUP BY semana, mes ORDER BY semana ASC'
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        dados = cursor.fetchall()
        cursor.close()
        
        return dados

    def gera_cards_perguntas(dados_perguntas,fk_gestor=None):
        perguntas = []
        for fk_pergunta, desc_pergunta in dados_perguntas:
            
            resultado_nota = consulta_nota('respostas_fato',fk_gestor,None,fk_pergunta)
            nota = resultado_nota[0]
            size = resultado_nota[1]
            
            respostas = consulta_quantidade('respostas_fato',fk_gestor,None,fk_pergunta,'>=')
            puladas = consulta_quantidade('respostas_fato',fk_gestor,None,fk_pergunta,'<')

            resultado_datas = consulta_datas('respostas_fato',fk_gestor, None, fk_pergunta)
            data_min = resultado_datas[0]
            data_max = resultado_datas[1]
            
            dados_graficos = gera_dados_grafico(fk_gestor, fk_pergunta)
            grafico = [{'eixo_x':  f'Semana: {semana} / {nome_meses(mes)}', 'nota': round(nota, 1)} for semana, mes, nota in gera_dados_grafico(fk_gestor, fk_pergunta)]
            
            perguntas.append({
                'fk_pergunta': fk_pergunta,
                'pergunta': desc_pergunta,
                'nota': nota,
                'respostas': respostas,
                'puladas': puladas,
                'size': size,
                'grafico': grafico,
                'data_min': data_min,
                'data_max': data_max
            })
        
        dados_detalhes = {
            "title": categoria,
            "content": f'Abertura por pergunta da dimensão {categoria}, notas baseada em um total de {respostas} respostas.',
            "perguntas": perguntas
        }

        return dados_detalhes

    perfil = session['perfil']
    id_gestor = session['id']

    # Categorias
    categoria = consulta_categorias()       
    # Perguntas
    dados_perguntas = consulta_perguntas(fk_categoria)

    if perfil == 'gestor':
        dados_detalhes = gera_cards_perguntas(dados_perguntas, id_gestor)
    elif perfil == 'admin' or perfil == 'gerente_fabril':
        dados_detalhes = gera_cards_perguntas(dados_perguntas)
    return jsonify(dados_detalhes)

@app.route('/detalhes_sugestao/<id_sugestao>', methods=['GET'])
def detalhes_sugestao(id_sugestao):
    session['id_sugestao'] = id_sugestao
    def nome_gestor(fk_gestor):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT desc_gestor FROM gestor_dim WHERE fk_gestor = %s',(fk_gestor,))
        gestor = cursor.fetchone()
        cursor.close()
        return gestor
    
    dados_sugestao = consulta_sugestoes('sugestoes_fato',None,None,None,None,None, id_sugestao)[0]
    fk_gestor = dados_sugestao['fk_gestor']
    gestor = nome_gestor(fk_gestor)
    
    fk_categoria = dados_sugestao['fk_categoria']
    fk_pergunta = dados_sugestao['fk_pergunta']
    categoria = consulta_categoria(fk_categoria)
    if fk_pergunta is not None:
        pergunta = consulta_pergunta(fk_pergunta)
    else:
        pergunta = 'Sugestão enviada pela aba de sugestões.'
    sugestao = dados_sugestao['sugestao']

    dados = {
        "sugestao": sugestao,
        "gestor": gestor,
        "categoria": categoria,
        "pergunta": pergunta,
        "respostas": []
    }

    respostas_sugestao = consulta_respostas_sugestao(id_sugestao)
    if respostas_sugestao is not None:
        for resposta in respostas_sugestao:
            fk_gestor_resposta = resposta['fk_gestor']
            gestor_resposta = nome_gestor(fk_gestor_resposta)
            data_resposta = resposta['data']
            texto_resposta = resposta['texto_resposta']

            resposta_objeto = {
            "gestor": gestor_resposta,
            "data": data_resposta,
            "texto_resposta": texto_resposta
            }
            
            dados["respostas"].append(resposta_objeto)
    
    app.logger.debug(dados)
    return jsonify(dados)

@app.route('/enviar_resposta', methods=['POST'])
def enviar_resposta():
    
    def atualiza_sugestoes_fato(id_sugestao):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE sugestoes_fato SET respondido = 1 WHERE id_sugestao = %s',(id_sugestao,))
        db.commit()
        cursor.close()

    def salva_resposta(id_sugestao, data_atual, date_time, fk_gestor, resposta):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT into  respostas_sugestoes_fato (id_sugestao, data, datetime, fk_gestor, texto_resposta) VALUES (%s, %s, %s, %s, %s)',(id_sugestao, data_atual, date_time, fk_gestor, resposta))
        db.commit()
        cursor.close()

    try:
        resposta = request.form['responderTextarea']
        fk_gestor = session['fk_gestor']
        id_sugestao = session['id_sugestao']
        date_time = datetime.datetime.now()
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        atualiza_sugestoes_fato(id_sugestao)
        salva_resposta(id_sugestao, data_atual, date_time, fk_gestor, resposta)
        
        return jsonify({'status': 'success', 'message': 'Resposta enviada com sucesso!'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Erro ao enviar a resposta: {}'.format(str(e))})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)