from app.utils.db import get_db  # Importando a função get_db
from flask import current_app as app, flash

def consulta_usuario_id(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE globalId = %s', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result
    else:
        return None

def consulta_usuario_resposta_data(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT data FROM usuario_respondeu WHERE globalId = %s ORDER BY data desc LIMIT 1',(user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
                return result[0]
        else:
                return None

def consulta_usuario_resposta_semana(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT WEEK(data,1) FROM usuario_respondeu WHERE globalId = %s ORDER BY data desc LIMIT 1',(user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
                return result[0]
        else:
                return None
def consulta_perguntas_selecionadas(perguntas_selecionadas):
    # Criar placeholders
    placeholders = ', '.join(['%s'] * len(perguntas_selecionadas))
    
    # Construir a query
    query = f'SELECT fk_pergunta, fk_categoria, texto_pergunta, texto_pergunta_es FROM perguntas WHERE fk_pergunta IN ({placeholders})'
        
    # Conectar ao banco de dados e executar a query
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, perguntas_selecionadas)
    result = cursor.fetchall()
    
    # Fechar o cursor e a conexão com o banco de dados
    cursor.close()
    
    # Retornar o resultado da query
    return result if result else None
        
def consulta_fk_pergunta_categoria(fk_categoria=None):
        query = 'SELECT fk_pergunta, fk_categoria FROM perguntas'
        conditions = []
        params = []
        if fk_categoria is not None:
                conditions.append('fk_categoria = %s')
                params.append(fk_categoria)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

def consulta_fk_categoria_geral():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_categoria FROM categorias')
        result = cursor.fetchall()
        cursor.close()
        return result

def consulta_fk_categoria(fk_pergunta):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fk_categoria FROM perguntas WHERE fk_pergunta = %s',(fk_pergunta,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result

def consulta_texto_perguntas(fk_pergunta, fk_pais=3):
        db = get_db()
        cursor = db.cursor()
        if fk_pais != 3:
                cursor.execute('SELECT texto_pergunta_es FROM perguntas WHERE fk_pergunta = %s',(fk_pergunta,))
        else:
                cursor.execute('SELECT texto_pergunta FROM perguntas WHERE fk_pergunta = %s',(fk_pergunta,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result
def get_todas_perguntas(fk_pais = 3):
        db = get_db()
        cursor = db.cursor()
        if fk_pais == 3:
                query = """
                SELECT 
                        p.fk_pergunta,
                        p.texto_pergunta,
                        p.texto_pergunta_es,
                        c.desc_categoria,
                        p.mega_pulso,
                        c.fk_categoria
                FROM
                        pulsa.perguntas p
                JOIN
                        pulsa.categorias c ON p.fk_categoria = c.fk_categoria
                """
        else:
                query = """
                SELECT 
                        p.fk_pergunta,
                        p.texto_pergunta,
                        p.texto_pergunta_es,
                        c.desc_categoria_es,
                        p.mega_pulso,
                        c.fk_categoria
                FROM
                        pulsa.perguntas p
                JOIN
                        pulsa.categorias c ON p.fk_categoria = c.fk_categoria
                """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        if result:
                return result
        else:
               return None

def consulta_categorias(fk_pais = 3):
        db = get_db()
        cursor = db.cursor()
        if fk_pais != 3:
               cursor.execute('SELECT desc_categoria_es FROM categorias')
        else:
                cursor.execute('SELECT desc_categoria FROM categorias')
        result = cursor.fetchall()
        cursor.close()
        return result

def consulta_fk_categoria_pela_desc_categoria(desc_categoria, fk_pais = 3):
        db = get_db()
        cursor = db.cursor()
        if fk_pais != 3:
               cursor.execute('SELECT fk_categoria FROM categorias where desc_categoria_es = %s',(desc_categoria,))
        else:
                cursor.execute('SELECT fk_categoria FROM categorias where desc_categoria = %s',(desc_categoria,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result

def consulta_desc_categoria_pelo_fk_categoria(fk_categoria, fk_pais = 3):
        db = get_db()
        cursor = db.cursor()
        if fk_pais != 3:
               cursor.execute('SELECT desc_categoria_es FROM categorias where fk_categoria = %s',(fk_categoria,))
        else:
                cursor.execute('SELECT desc_categoria FROM categorias where fk_categoria = %s',(fk_categoria,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result

def consulta_dados_gestor(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM gestores WHERE globalId = %s',(user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

def consulta_usuarios_por_unidade(fk_unidade):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE fk_unidade = %s ORDER BY globalId asc', (fk_unidade,))
    result = cursor.fetchall()
    cursor.close()
    if result:
        return result
    else:
        return None
    
def consulta_todos_gestores():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT globalId, gestor_nome, perfil FROM gestores ORDER BY globalId asc')
    result = cursor.fetchall()
    cursor.close()
    if result:
        return result
    else:
        return None
    
def consulta_tabela_dimensao(tabela, coluna=None, pesquisa=None):
        query = f'SELECT * FROM {tabela}'
        params = []
        conditions = []
        fetchone = False

        if coluna is not None:
            conditions.append(f'{coluna} = {pesquisa}')
            params.append(coluna)
            fetchone = True
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query)
        if not fetchone:
                result = cursor.fetchall()
        else:
                result = cursor.fetchone()

        cursor.close()
        if result:
                return result
        else:
                return None
        
def consulta_fk_dimensao(tabela, coluna_retorno, coluna_pesquisa=None, pesquisa=None):
        query = f'SELECT {coluna_retorno} FROM {tabela}'
        params = []
        conditions = []
        fetchone = False

        if coluna_pesquisa is not None:
                if type(pesquisa) == int:
                       conditions.append(f"{coluna_pesquisa} = {pesquisa}")   
                else:
                        conditions.append(f"{coluna_pesquisa} = '{pesquisa}'")
                        params.append(coluna_pesquisa)
                        fetchone = True

        if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query)
        if not fetchone:
                result = cursor.fetchall()
        else:
                result = cursor.fetchone()

        cursor.close()
        if result:
                return result
        else:
                return None
        
def consulta_dados_respostas(fk_gestor=None, data_min=None, data_max = None):
        query = f'SELECT COUNT(*) FROM respostas'
        params = []
        conditions = []

        if fk_gestor is not None:
                conditions.append('fk_gestor = %s')
                params.append(fk_gestor)

        if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        if result:
                return result
        else:
                return None

def consulta_semana_mes_media_respostas(fk_gestor=None, fk_categoria=None, fk_pergunta=None):
        query = '''
        SELECT 
                weekofyear(data_hora) as semana_ano, 
                month(data_hora) as mes, 
                avg(resposta) as media, 
                ROUND(ceiling(count(*)/10) / 
                (SELECT COUNT(globalId) 
                FROM pulsa.usuarios 
                WHERE fk_gestor = %s) * 100, 0) as aderencia
        FROM pulsa.respostas
        WHERE resposta >= 0
        AND fk_gestor = %s
        '''

        params = [fk_gestor, fk_gestor]  # fk_gestor para subconsulta e para WHERE principal
        conditions = []

        if fk_categoria is not None:
                conditions.append('fk_categoria = %s')
                params.append(fk_categoria)

        if fk_pergunta is not None:
                conditions.append('fk_pergunta = %s')
                params.append(fk_pergunta)

        # Se houver condições extras (fk_categoria, fk_pergunta), adicioná-las após "resposta >= 0"
        if conditions:
                query += ' AND ' + ' AND '.join(conditions)

        query += ' GROUP BY semana_ano, mes ORDER BY semana_ano ASC'
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()

        return result if result else None

def consulta_time_por_fk_gestor(fk_gestor):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT globalId FROM usuarios WHERE fk_gestor = %s ORDER BY globalId asc', (fk_gestor,))
        result = cursor.fetchall()
        cursor.close()
        if result:
                return result
        else:
                return None

def get_id_nome_time(fk_gestor):
       db = get_db()
       cursor = db.cursor()
       query = 'SELECT globalId, nome FROM usuarios WHERE fk_gestor = %s order by nome asc'
       cursor.execute(query, (fk_gestor,))
       result = cursor.fetchall()
       if result:
                return result
       else:
              return None

def get_id_nome_time_area(fk_gestor):
       db = get_db()
       cursor = db.cursor()
       query = '''
        SELECT 
                u.globalId, 
                u.nome,
                g.gestor_nome
        FROM 
                usuarios u
        JOIN
                lideres_com_liderados ll 
                        ON ll.fk_gestor_liderado = u.fk_gestor
        JOIN 
	        gestores g
		        ON g.fk_gestor = ll.fk_gestor_liderado
        WHERE 
                ll.fk_gestor_lider = %s
        ORDER BY 
                u.nome ASC
        '''
       cursor.execute(query, (fk_gestor,))
       result = cursor.fetchall()
       if result:
                return result
       else:
              return None

def get_tamanho_time_area(fk_gestor):
        db = get_db()
        cursor = db.cursor()
        query = """
        SELECT
                sum(tamanho_time)
        FROM
                lideres_com_liderados
        WHERE
                fk_gestor_lider = %s
        """
        cursor.execute(query, (fk_gestor,))
        result = cursor.fetchone()
        cursor.close()
        if result:
                return result[0]
        else:
                return None
        
def consulta_usuario_respondeu():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM usuario_respondeu')
        result = cursor.fetchall()
        cursor.close()
        if result:
                return result
        else:
                return None
        
def consulta_pesquisa_gestor(id):
       parametro_pesquisa = [f'%{id}%']
       db = get_db()
       cursor = db.cursor()
       cursor.execute(f"SELECT globalId, gestor_nome, perfil FROM gestores WHERE globalId LIKE %s",(parametro_pesquisa))
       result = cursor.fetchall()
       cursor.close()
       if result:
              return result
       else:
              return None
       
def consulta_pesquisa_usuario(id, unidade=None):
       parametro_pesquisa = f'%{id}%'
       db = get_db()
       cursor = db.cursor()
       cursor.execute('''SELECT * FROM usuarios WHERE fk_unidade = %s AND globalId LIKE %s ORDER BY globalId asc''',(unidade, parametro_pesquisa))

       result = cursor.fetchall()
       cursor.close()
       if result:
              return result
       else:
              return None
       
def consulta_sugestoes_por_gestor(fk_gestor):
        query = '''SELECT 
                        s.id_sugestao, 
                        date_format(s.data_hora, '%d-%m-%y'), 
                        g.gestor_nome, 
                        c.desc_categoria, 
                        p.texto_pergunta, 
                        s.texto_sugestao
                FROM sugestoes s
                INNER JOIN
                        gestores g ON s.fk_gestor = g.fk_gestor
                INNER JOIN
                categorias c ON s.fk_categoria = c.fk_categoria
                INNER JOIN
                        perguntas p ON s.fk_pergunta = p.fk_pergunta
                WHERE s.fk_gestor = %s  
                ORDER BY data_hora ASC
        '''
        params = [fk_gestor,]
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        if result:
                return result
        else:
                return None

def consulta_sugestoes_por_gestor_area(fk_gestor):
        query = '''SELECT 
                        s.id_sugestao, 
                        date_format(s.data_hora, '%d-%m-%y'), 
                        g.gestor_nome, 
                        c.desc_categoria, 
                        p.texto_pergunta, 
                        s.texto_sugestao
                FROM lideres_com_liderados_sugestoes s
                INNER JOIN
                        gestores g ON s.fk_gestor_liderado = g.fk_gestor
                INNER JOIN
                        categorias c ON s.fk_categoria = c.fk_categoria
                INNER JOIN
                        perguntas p ON s.fk_pergunta = p.fk_pergunta
                WHERE s.fk_gestor_lider = %s
                ORDER BY data_hora ASC
        '''
        params = [fk_gestor,]
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        if result:
                return result
        else:
                return None

def consulta_qtd_sugestoes(fk_gestor, fk_categoria=None, fk_pergunta=None):
        conditions = []
        params = []
        query = '''SELECT count(*) FROM sugestoes'''
        if fk_gestor:
               conditions.append('fk_gestor = %s')
               params.append(fk_gestor)
        if fk_categoria:
               conditions.append('fk_categoria = %s')
               params.append(fk_categoria)
        if fk_pergunta:
               conditions.append('fk_pergunta = %s')
               params.append(fk_pergunta)
        if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result:
               return result
        else:
               return None

def consulta_qtd_sugestoes_area(fk_gestor, fk_categoria=None, fk_pergunta=None):
        conditions = []
        params = []
        query = '''SELECT count(*) FROM lideres_com_liderados_sugestoes'''
        if fk_gestor:
               conditions.append('fk_gestor_lider = %s')
               params.append(fk_gestor)
        if fk_categoria:
               conditions.append('fk_categoria = %s')
               params.append(fk_categoria)
        if fk_pergunta:
               conditions.append('fk_pergunta = %s')
               params.append(fk_pergunta)
        if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result:
               return result
        else:
               return None

def consulta_resumo_respostas_categoria_gestor(fk_gestor):
       db = get_db()
       cursor = db.cursor()
       cursor.execute('''
                SELECT 
                        IFNULL(c.fk_categoria, 0) AS fk_categoria,
                        IF(IFNULL(c.fk_categoria, 'Resultado Geral'), MIN(c.desc_categoria),'Resultado Geral') AS desc_categoria,
                        COUNT(*) as qtd, 
                        IF(COUNT(*) > 3, ROUND(AVG(r.resposta), 2), NULL) AS media,
                        DATE_FORMAT(MIN(r.data_hora), '%d-%m') as minimo,
                        DATE_FORMAT(MAX(r.data_hora), '%d-%m') as maximo
                FROM pulsa.categorias c
                LEFT JOIN pulsa.respostas r ON c.fk_categoria = r.fk_categoria
                        AND r.fk_gestor = %s
                        AND r.resposta > 0
                WHERE c.fk_categoria < 11
                GROUP BY c.fk_categoria WITH ROLLUP
                ORDER BY c.fk_categoria ASC''',
                (fk_gestor,))
       result = cursor.fetchall()
       if result:
              return result
       else:
              return None
       
def quantidade_perguntas_pesquisa():
        db = get_db()
        cursor = db.cursor()
        query = "SELECT qtd_perguntas FROM qtd_perguntas_pesquisa"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        if result:
                return result[0]
        else:
                return 10
        
def quantidade_perguntas_mega_pulso():
        db = get_db()
        cursor = db.cursor()
        query = "SELECT count(*) FROM perguntas WHERE mega_pulso = 1"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        if result:
                return result[0]
        
def consulta_fk_perguntas_mega_pulso():
        db = get_db()
        cursor = db.cursor()
        query = "SELECT fk_pergunta FROM perguntas WHERE mega_pulso = 1"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        if result:
                lista_perguntas = [item[0] for item in result]
                return lista_perguntas
        else:
                return 10

def get_perfil_gestor(globalId):
        db = get_db()
        cursor = db.cursor()
        query = "SELECT perfil FROM gestores WHERE globalId = %s"
        cursor.execute(query, (globalId,))
        result = cursor.fetchone()
        cursor.close()
        if result:
               return result[0]