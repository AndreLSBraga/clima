from app.utils.db import get_db  # Importando a função get_db
from flask import current_app as app, flash


def consulta_promotores(fk_gestor=None, fk_pergunta=None, fk_categoria=None):
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
    
def consulta_promotores_categorias(fk_gestor):
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
    LEFT JOIN 
        pulsa.respostas r ON r.fk_categoria = c.fk_categoria
    '''

    params = []
    conditions = []

    if fk_gestor is not None:
        conditions.append('fk_gestor = %s')
        params.append(fk_gestor)

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
    
def consulta_promotores_grafico_geral(fk_gestor):
    query = '''
    WITH intervalos AS (
        SELECT DISTINCT
            CASE
                WHEN data_hora < '2024-09-30' THEN
                    CONCAT(
                        DATE_FORMAT(
                            DATE_ADD('2024-09-02', INTERVAL FLOOR(DATEDIFF(data_hora, '2024-09-02') / 7) * 7 DAY),
                            '%d/%m'
                        ),
                        ' - ',
                        DATE_FORMAT(
                            DATE_ADD('2024-09-02', INTERVAL (FLOOR(DATEDIFF(data_hora, '2024-09-02') / 7) * 7 + 6) DAY),
                            '%d/%m'
                        )
                    )
                ELSE
                    CONCAT(
                        DATE_FORMAT(
                            DATE_ADD('2024-09-30', INTERVAL FLOOR(DATEDIFF(data_hora, '2024-09-30') / 14) * 14 DAY),
                            '%d/%m'
                        ),
                        ' - ',
                        DATE_FORMAT(
                            DATE_ADD('2024-09-30', INTERVAL (FLOOR(DATEDIFF(data_hora, '2024-09-30') / 14) * 14 + 13) DAY),
                            '%d/%m'
                        )
                    )
            END AS intervalo_pesquisa
        FROM
            pulsa.respostas
    )
    SELECT 
        i.intervalo_pesquisa,
        count(distinct(r.identificador)) as respondentes_unicos,
        ROUND(100.0 * COALESCE(SUM(CASE WHEN r.resposta >= 6 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(r.resposta), 0), 2) AS percentual_promotores,
        ROUND(count(distinct(r.identificador)) / 
                    (SELECT COUNT(globalId) 
                    FROM pulsa.usuarios 
                    WHERE fk_gestor = %s) * 100, 0) as aderencia
    FROM 
        intervalos i
    LEFT JOIN 
        pulsa.respostas r ON 
            (CASE 
                WHEN r.data_hora < '2024-09-30' THEN 
                    i.intervalo_pesquisa = CONCAT(
                        DATE_FORMAT(DATE_ADD('2024-09-02', INTERVAL FLOOR(DATEDIFF(r.data_hora, '2024-09-02') / 7) * 7 DAY), '%d/%m'), 
                        ' - ', 
                        DATE_FORMAT(DATE_ADD('2024-09-02', INTERVAL (FLOOR(DATEDIFF(r.data_hora, '2024-09-02') / 7) * 7 + 6) DAY), '%d/%m')
                    )
                ELSE 
                    i.intervalo_pesquisa = CONCAT(
                        DATE_FORMAT(DATE_ADD('2024-09-30', INTERVAL FLOOR(DATEDIFF(r.data_hora, '2024-09-30') / 14) * 14 DAY), '%d/%m'), 
                        ' - ', 
                        DATE_FORMAT(DATE_ADD('2024-09-30', INTERVAL (FLOOR(DATEDIFF(r.data_hora, '2024-09-30') / 14) * 14 + 13) DAY), '%d/%m')
                    )
            END)
            AND r.fk_gestor = %s  -- Filtro aplicado no JOIN
    GROUP BY 
        i.intervalo_pesquisa
    ORDER BY 
        i.intervalo_pesquisa;
    '''

    params =[fk_gestor, fk_gestor]
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    if result:
            return result
    else:
            return None