from app.utils.db import get_db  # Importando a função get_db
from flask import current_app as app, flash


def consulta_promotores(datas_min_max,fk_gestor=None, fk_pergunta=None, fk_categoria=None):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = f'''
    SELECT
        ROUND(100.0 * SUM(CASE WHEN resposta >= 6 THEN 1 ELSE 0 END) / COUNT(*),1) AS percentual_promotores,
        SUM(CASE WHEN resposta >= 6 THEN 1 ELSE 0 END) as promotoras,
        COUNT(DISTINCT(identificador)) as respostas_unicas, 
        COUNT(*) AS total_respostas,
        DATE_FORMAT(MIN(data_hora), '%d-%m')AS menor_data,
        DATE_FORMAT(MAX(data_hora), '%d-%m') AS maior_data
    FROM
        pulsa.respostas
    WHERE
        fk_categoria != 11        
    '''
    
    params = []
    conditions = []

    if fk_gestor is not None:
        conditions.append('fk_gestor = %s')
        params.append(fk_gestor)
    if fk_pergunta is not None:
        conditions.append('fk_pergunta = %s')
        params.append(fk_pergunta)
    if fk_categoria is not None:
        conditions.append('fk_categoria = %s')
        params.append(fk_categoria)
    if data_min is not None:
        conditions.append('data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('data_hora <= %s')
        params.append(data_max)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None

def consulta_promotores_area(datas_min_max,fk_gestor=None, fk_pergunta=None, fk_categoria=None):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = f'''
    SELECT
        ROUND(100.0 * SUM(CASE WHEN resposta >= 6 THEN 1 ELSE 0 END) / COUNT(*),1) AS percentual_promotores,
        SUM(CASE WHEN resposta >= 6 THEN 1 ELSE 0 END) as promotoras,
        COUNT(DISTINCT(identificador)) as respostas_unicas, 
        COUNT(*) AS total_respostas,
        DATE_FORMAT(MIN(data_hora), '%d-%m')AS menor_data,
        DATE_FORMAT(MAX(data_hora), '%d-%m') AS maior_data
    FROM
        pulsa.lideres_com_liderados_respostas
    WHERE
        fk_categoria != 11        
    '''
    
    params = []
    conditions = []

    if fk_gestor is not None:
        conditions.append('fk_gestor_lider = %s')
        params.append(fk_gestor)
    if fk_pergunta is not None:
        conditions.append('fk_pergunta = %s')
        params.append(fk_pergunta)
    if fk_categoria is not None:
        conditions.append('fk_categoria = %s')
        params.append(fk_categoria)
    if data_min is not None:
        conditions.append('data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('data_hora <= %s')
        params.append(data_max)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None

def consulta_promotores_categorias(datas_min_max, fk_gestor):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = f'''
    SELECT
        c.fk_categoria, 
        c.desc_categoria,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 1) AS percentual_promotores,
        COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) AS promotoras,
        COALESCE(COUNT(DISTINCT r.identificador), 0) AS respostas_unicas, 
        COALESCE(COUNT(r.identificador), 0) AS total_respostas,
        COALESCE(DATE_FORMAT(MIN(r.data_hora), '%d-%m'), '-') AS menor_data,
        COALESCE(DATE_FORMAT(MAX(r.data_hora), '%d-%m'), '-') AS maior_data
    FROM
        pulsa.categorias c
    INNER JOIN 
        pulsa.respostas r ON r.fk_categoria = c.fk_categoria
    '''

    params = []
    conditions = []

    if fk_gestor is not None:
        conditions.append('fk_gestor = %s')
        params.append(fk_gestor)
    if data_min is not None:
        conditions.append('data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('data_hora <= %s')
        params.append(data_max)
    if conditions:
        query += ' AND ' + ' AND '.join(conditions)
    
    query += ' WHERE c.fk_categoria != 11 GROUP BY c.fk_categoria, c.desc_categoria;'
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None

def consulta_promotores_categorias_area(datas_min_max, fk_gestor):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = f'''
    SELECT
        c.fk_categoria, 
        c.desc_categoria,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 1) AS percentual_promotores,
        COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) AS promotoras,
        COALESCE(COUNT(DISTINCT r.identificador), 0) AS respostas_unicas, 
        COALESCE(COUNT(r.identificador), 0) AS total_respostas,
        COALESCE(DATE_FORMAT(MIN(r.data_hora), '%d-%m'), '-') AS menor_data,
        COALESCE(DATE_FORMAT(MAX(r.data_hora), '%d-%m'), '-') AS maior_data
    FROM
        pulsa.categorias c
    INNER JOIN 
        pulsa.lideres_com_liderados_respostas r ON r.fk_categoria = c.fk_categoria
    '''

    params = []
    conditions = []

    if fk_gestor is not None:
        conditions.append('fk_gestor_lider = %s')
        params.append(fk_gestor)
    if data_min is not None:
        conditions.append('data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('data_hora <= %s')
        params.append(data_max)
    if conditions:
        query += ' AND ' + ' AND '.join(conditions)
    
    query += ' WHERE c.fk_categoria != 11 GROUP BY c.fk_categoria, c.desc_categoria;'
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None

def consulta_promotores_perguntas(datas_min_max, fk_gestor, fk_categoria):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = '''
    SELECT 
        p.fk_pergunta, 
        p.texto_pergunta,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 1) AS percentual_promotores,
        COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) AS promotoras,
        COALESCE(COUNT(DISTINCT r.identificador), 0) AS respostas_unicas, 
        COALESCE(COUNT(r.identificador), 0) AS total_respostas,
        COALESCE(DATE_FORMAT(MIN(r.data_hora), '%d-%m'), '-') AS menor_data,
        COALESCE(DATE_FORMAT(MAX(r.data_hora), '%d-%m'), '-') AS maior_data
    FROM 
        pulsa.perguntas p
    INNER JOIN 
        pulsa.respostas r ON r.fk_pergunta = p.fk_pergunta
    '''

    conditions = []
    params = []
    if fk_gestor is not None:
        conditions.append('r.fk_gestor = %s')
        params.append(fk_gestor)
    if data_min is not None:
        conditions.append('r.data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('r.data_hora <= %s')
        params.append(data_max)
    
    if conditions:
        query += ' AND ' + ' AND '.join(conditions)
    
    query += ' WHERE p.fk_categoria = %s GROUP BY p.fk_pergunta, p.texto_pergunta'
    params.append(fk_categoria)
    #Adiciona a categoria para o último placeholder
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None
def consulta_promotores_perguntas_area(datas_min_max, fk_gestor, fk_categoria):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = '''
    SELECT 
        p.fk_pergunta, 
        p.texto_pergunta,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 1) AS percentual_promotores,
        COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) AS promotoras,
        COALESCE(COUNT(DISTINCT r.identificador), 0) AS respostas_unicas, 
        COALESCE(COUNT(r.identificador), 0) AS total_respostas,
        COALESCE(DATE_FORMAT(MIN(r.data_hora), '%d-%m'), '-') AS menor_data,
        COALESCE(DATE_FORMAT(MAX(r.data_hora), '%d-%m'), '-') AS maior_data
    FROM 
        pulsa.perguntas p
    INNER JOIN 
        pulsa.lideres_com_liderados_respostas r ON r.fk_pergunta = p.fk_pergunta
    '''

    conditions = []
    params = []
    if fk_gestor is not None:
        conditions.append('r.fk_gestor_lider = %s')
        params.append(fk_gestor)
    if data_min is not None:
        conditions.append('r.data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('r.data_hora <= %s')
        params.append(data_max)
    
    if conditions:
        query += ' AND ' + ' AND '.join(conditions)
    
    query += ' WHERE p.fk_categoria = %s GROUP BY p.fk_pergunta, p.texto_pergunta'
    params.append(fk_categoria)
    #Adiciona a categoria para o último placeholder
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None

def consulta_promotores_grafico_geral(datas_min_max, fk_gestor):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]

    query = '''
    SELECT 
        i.intervalo_pesquisa,
        count(distinct(r.identificador)) as respondentes_unicos,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 2) AS percentual_promotores,
        ROUND(
            (SELECT count(*) FROM pulsa.respondentes_por_pesquisa where fk_gestor = %s and data between i.data_referencia_min and i.data_referencia_max) /
            (SELECT COUNT(globalId) FROM pulsa.usuarios WHERE fk_gestor = %s) * 100, 0) as aderencia
    FROM 
        pulsa.intervalos_pesquisa_view i
    INNER JOIN 
        pulsa.respostas r ON
            r.data_hora BETWEEN i.data_referencia_min AND i.data_referencia_max
            AND r.fk_gestor = %s
    '''
    conditions = []
    params =[fk_gestor, fk_gestor, fk_gestor]
    if data_min is not None:
        conditions.append('data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('data_hora <= %s')
        params.append(data_max)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    query += '''
        GROUP BY 
            i.intervalo_pesquisa, i.data_referencia_min, i.data_referencia_max
        ORDER BY 
            i.data_referencia_min ASC;
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None

def consulta_promotores_grafico_geral_area(datas_min_max, fk_gestor):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]

    query = '''
    SELECT 
        i.intervalo_pesquisa,
        count(distinct(r.identificador)) as respondentes_unicos,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 2) AS percentual_promotores,
        ROUND(
            (SELECT count(*) FROM pulsa.respondentes_por_pesquisa where fk_gestor = %s and data between i.data_referencia_min and i.data_referencia_max) /
            (SELECT COUNT(globalId) FROM pulsa.usuarios WHERE fk_gestor = %s) * 100, 0) as aderencia
    FROM 
        pulsa.intervalos_pesquisa_view i
    INNER JOIN 
        pulsa.lideres_com_liderados_respostas r ON
            r.data_hora BETWEEN i.data_referencia_min AND i.data_referencia_max
            AND r.fk_gestor_lider = %s
    '''
    conditions = []
    params =[fk_gestor, fk_gestor, fk_gestor]
    if data_min is not None:
        conditions.append('data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('data_hora <= %s')
        params.append(data_max)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    query += '''
        GROUP BY 
            i.intervalo_pesquisa, i.data_referencia_min, i.data_referencia_max
        ORDER BY 
            i.data_referencia_min ASC;
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
        return result
    else:
        return None

def consulta_promotores_grafico_categoria(datas_min_max, fk_gestor, fk_categoria):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = '''
    SELECT 
        i.intervalo_pesquisa,
        count(distinct(r.identificador)) as respondentes_unicos,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 1) AS percentual_promotores
    FROM 
        intervalos_pesquisa_view i
    INNER JOIN 
        pulsa.respostas r ON r.data_hora BETWEEN i.data_referencia_min AND i.data_referencia_max
        AND r.fk_gestor = %s AND r.fk_categoria = %s
    '''
    
    conditions = []
    params =[fk_gestor, fk_categoria]
    if data_min is not None:
        conditions.append('r.data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('r.data_hora <= %s')
        params.append(data_max)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    query += '''
    GROUP BY 
        i.intervalo_pesquisa, i.data_referencia_min
    ORDER BY 
        i.data_referencia_min ASC;
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None
    
def consulta_promotores_grafico_categoria_area(datas_min_max, fk_gestor, fk_categoria):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = '''
    SELECT 
        i.intervalo_pesquisa,
        count(distinct(r.identificador)) as respondentes_unicos,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 1) AS percentual_promotores
    FROM 
        intervalos_pesquisa_view i
    INNER JOIN 
        pulsa.lideres_com_liderados_respostas r ON r.data_hora BETWEEN i.data_referencia_min AND i.data_referencia_max
        AND r.fk_gestor_lider = %s AND r.fk_categoria = %s
    '''
    
    conditions = []
    params =[fk_gestor, fk_categoria]
    if data_min is not None:
        conditions.append('r.data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('r.data_hora <= %s')
        params.append(data_max)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    query += '''
    GROUP BY 
        i.intervalo_pesquisa, i.data_referencia_min
    ORDER BY 
        i.data_referencia_min ASC;
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None
    
def consulta_promotores_grafico_pergunta(datas_min_max, fk_gestor, fk_categoria=None):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = '''
    SELECT 
        i.intervalo_pesquisa,
        r.fk_pergunta,
        count(distinct(r.identificador)) as respondentes_unicos,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 1) AS percentual_promotores
    FROM 
        intervalos_pesquisa_view i
    INNER JOIN 
        pulsa.respostas r ON r.data_hora BETWEEN i.data_referencia_min AND i.data_referencia_max
        AND r.fk_gestor = %s AND r.fk_categoria = %s
    '''

    conditions = []
    params =[fk_gestor, fk_categoria]
    if data_min is not None:
        conditions.append('r.data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('r.data_hora <= %s')
        params.append(data_max)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)
    query += '''
    GROUP BY 
        i.intervalo_pesquisa, r.fk_pergunta, i.data_referencia_min
    ORDER BY 
        r.fk_pergunta ASC, i.data_referencia_min ASC;
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None

def consulta_promotores_grafico_pergunta_area(datas_min_max, fk_gestor, fk_categoria=None):
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]
    query = '''
    SELECT 
        i.intervalo_pesquisa,
        r.fk_pergunta,
        count(distinct(r.identificador)) as respondentes_unicos,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 1) AS percentual_promotores
    FROM 
        intervalos_pesquisa_view i
    INNER JOIN 
        pulsa.lideres_com_liderados_respostas r ON r.data_hora BETWEEN i.data_referencia_min AND i.data_referencia_max
        AND r.fk_gestor_lider = %s AND r.fk_categoria = %s
    '''

    conditions = []
    params =[fk_gestor, fk_categoria]
    if data_min is not None:
        conditions.append('r.data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('r.data_hora <= %s')
        params.append(data_max)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)
    query += '''
    GROUP BY 
        i.intervalo_pesquisa, r.fk_pergunta, i.data_referencia_min
    HAVING 
        COUNT(DISTINCT r.identificador) >= 3
    ORDER BY 
        r.fk_pergunta ASC, i.data_referencia_min ASC;
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None

def consulta_intervalo_respostas():
    query = f'''
    SELECT * FROM pulsa.intervalos_pesquisa_view;
    '''

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None
    
def consulta_promotores_por_categoria_gestor(datas_min_max, fk_gestor_lider):
     
    data_min = datas_min_max[0]
    data_max = datas_min_max[1]

    query = '''SELECT
        ll.fk_gestor_liderado,
        CONCAT(
            SUBSTRING_INDEX(g.gestor_nome, ' ', 1), ' ',
            SUBSTRING_INDEX(g.gestor_nome, ' ', -1)
        ) AS nome_completo,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT r.identificador) >= 3 
                THEN COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) 
                    / NULLIF(COUNT(r.resposta), 0)
                ELSE NULL
            END,
            1
        ) AS percentual_promotores,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 1 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 1 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 1 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Engagement,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 2 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 2 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 2 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Eficacia_gestor,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 3 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 3 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 3 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Funcoes_desempenhadas,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 4 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 4 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 4 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Plano_carreira,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 5 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 5 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 5 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Ambientes_ferramentas,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 6 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 6 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 6 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Salarios_beneficios,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 7 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 7 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 7 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Feedback_reconhecimento,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 8 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 8 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 8 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Comunicacao_colaboracao,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 9 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 9 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 9 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Servicos_gerais,
        ROUND(
            100.0 * CASE 
                WHEN COUNT(DISTINCT CASE WHEN c.fk_categoria = 10 THEN r.identificador END) >= 3 
                THEN COALESCE(SUM(CASE WHEN c.fk_categoria = 10 AND r.resposta >= 6 THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(CASE WHEN c.fk_categoria = 10 THEN 1 END), 0)
                ELSE NULL
            END,
            1
        ) AS Seguranca_psicologica
    FROM
        pulsa.categorias c
    JOIN 
        pulsa.lideres_com_liderados_respostas r ON r.fk_categoria = c.fk_categoria
    JOIN
        pulsa.lideres_com_liderados ll ON ll.fk_gestor_liderado = r.fk_gestor_liderado
    JOIN
        pulsa.gestores g ON ll.fk_gestor_liderado = g.fk_gestor
    WHERE ll.fk_gestor_lider = %s
    '''
    conditions = []
    params =[fk_gestor_lider]
    if data_min is not None:
        conditions.append('r.data_hora >= %s')
        params.append(data_min)
    if data_max is not None:
        conditions.append('r.data_hora <= %s')
        params.append(data_max)
    
    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    query += '''GROUP BY
        ll.fk_gestor_liderado, g.gestor_nome
    ORDER BY
        g.gestor_nome ASC
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None