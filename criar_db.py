import sqlite3
import os

# Defina o caminho para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'clima_organizacional.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn, conn.cursor()

def drop_tables():
    conn, cursor = get_db()
    cursor.execute('DROP TABLE IF EXISTS pergunta_dim')
    cursor.execute('DROP TABLE IF EXISTS categoria_dim')
    cursor.execute('DROP TABLE IF EXISTS usuarios_dim')
    cursor.execute('DROP TABLE IF EXISTS usuarios_respostas_fato')
    cursor.execute('DROP TABLE IF EXISTS cargo_dim')
    cursor.execute('DROP TABLE IF EXISTS area_dim')
    cursor.execute('DROP TABLE IF EXISTS subarea_dim')
    cursor.execute('DROP TABLE IF EXISTS gestor_dim')
    cursor.execute('DROP TABLE IF EXISTS respostas_fato')
    cursor.execute('DROP TABLE IF EXISTS sugestoes_fato')

    conn.commit()
    conn.close()

def create_tables():
    conn, cursor = get_db()
    # Crie a tabela 'pergunta_dim'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pergunta_dim (
        fk_pergunta INTEGER PRIMARY KEY,
        desc_pergunta TEXT,
        fk_categoria INTEGER,
        FOREIGN KEY (fk_pergunta) REFERENCES respostas_fato (fk_pergunta)
    )
    ''')

    # Crie a tabela 'categoria_dim'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categoria_dim (
        fk_categoria INTEGER PRIMARY KEY,
        desc_categoria TEXT,
        FOREIGN KEY (fk_categoria) REFERENCES pergunta_dim (fk_categoria)
    )
    ''')

    # Crie a tabela 'usuarios_dim'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios_dim (
        id INTEGER PRIMARY KEY,
        fk_cargo INTEGER,
        fk_area INTEGER,
        fk_subarea INTEGER,
        fk_gestor INTEGER,
        data_inicio_companhia DATE,
        data_inicio_funcao DATE
    )
    ''')

    # Crie a tabela 'usuarios_respostas_fato'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios_respostas_fato (
        id INTEGER PRIMARY KEY,
        data TEXT,
        datetime TEXT,
        FOREIGN KEY (id) REFERENCES usuarios_dim (id)
    )
    ''')

    # Crie a tabela 'cargo_dim'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cargo_dim (
        fk_cargo INTEGER PRIMARY KEY,
        desc_cargo TEXT,
        FOREIGN KEY (fk_cargo) REFERENCES usuarios_dim(fk_cargo)
    )
    ''')

    # Crie a tabela 'area_dim'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS area_dim (
        fk_area INTEGER PRIMARY KEY,
        desc_area TEXT,
        FOREIGN KEY (fk_area) REFERENCES usuarios_dim(fk_area)
    )
    ''')

    # Crie a tabela 'subarea_dim'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subarea_dim (
        fk_subarea INTEGER PRIMARY KEY,
        desc_subarea TEXT,
        FOREIGN KEY (fk_subarea) REFERENCES usuarios_dim(fk_subarea)
    )
    ''')

    # Crie a tabela 'gestor_dim'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gestor_dim (
        fk_gestor INTEGER PRIMARY KEY,
        desc_gestor TEXT,
        FOREIGN KEY (fk_gestor) REFERENCES usuarios_dim(fk_gestor)
    )
    ''')

    # Crie a tabela 'respostas_fato'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS respostas_fato (
        id_fantasia TEXT PRIMARY KEY,
        fk_cargo INTEGER,
        fk_area INTEGER,
        fk_subarea INTEGER,
        fk_gestor INTEGER,
        fk_pergunta INTEGER,
        fk_categoria INTEGER,
        data TEXT,
        datetime TEXT,
        resposta REAL,
        FOREIGN KEY (fk_cargo) REFERENCES cargo_dim (fk_cargo),
        FOREIGN KEY (fk_area) REFERENCES area_dim (fk_area),
        FOREIGN KEY (fk_subarea) REFERENCES subarea_dim (fk_subarea),
        FOREIGN KEY (fk_gestor) REFERENCES gestor_dim (fk_gestor),
        FOREIGN KEY (fk_pergunta) REFERENCES pergunta_dim (fk_pergunta),
        FOREIGN KEY (fk_categoria) REFERENCES categoria_dim (fk_categoria)
    )
    ''')


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sugestoes_fato (
        id_fantasia TEXT,
        fk_cargo INTEGER,
        fk_area INTEGER,
        fk_subarea INTEGER,
        fk_gestor INTEGER,
        fk_pergunta INTEGER,
        fk_categoria INTEGER,
        data TEXT,
        datetime TEXT,
        sugestao TEXT,
        id_autoidentificacao INTERGER,
        FOREIGN KEY (fk_cargo) REFERENCES cargo_dim (fk_cargo),
        FOREIGN KEY (fk_area) REFERENCES area_dim (fk_area),
        FOREIGN KEY (fk_subarea) REFERENCES subarea_dim (fk_subarea),
        FOREIGN KEY (fk_gestor) REFERENCES gestor_dim (fk_gestor),
        FOREIGN KEY (fk_pergunta) REFERENCES pergunta_dim (fk_pergunta),
        FOREIGN KEY (fk_categoria) REFERENCES categoria_dim (fk_categoria)
        FOREIGN KEY (id_autoidentificacao) REFERENCES usuarios_dim (id) 
    )
    ''')

    conn.commit()
    conn.close()

def insert_dados():
    conn, cursor = get_db()

    cargo = [
        (1, 'Analista'),
        (2, 'Assistente'),
        (3, 'Coordenador'),
        (4, 'Designer'),
        (5, 'Engenheiro'),
        (6, 'Gerente'),
        (7, 'Supervisor'),
        (8, 'Técnico')
    ]
    cursor.executemany('INSERT INTO cargo_dim (fk_cargo, desc_cargo) VALUES (?, ?)', cargo)

    area = [
        (1, 'Criação'),
        (2, 'Financeiro'),
        (3, 'Manutenção'),
        (4, 'Marketing'),
        (5, 'Produção'),
        (6, 'Projetos'),
        (7, 'RH'),
        (8, 'TI'),
        (9, 'Vendas')
    ]
    cursor.executemany('INSERT INTO area_dim (fk_area, desc_area) VALUES (?, ?)', area)

    subarea = [
        (1, 'Criação'),
        (2, 'Financeiro'),
        (3, 'Manutenção'),
        (4, 'Marketing'),
        (5, 'Produção'),
        (6, 'Projetos'),
        (7, 'RH'),
        (8, 'TI'),
        (9, 'Vendas')
    ]
    cursor.executemany('INSERT INTO subarea_dim (fk_subarea, desc_subarea) VALUES (?, ?)', subarea)

    gestor = [
        (1, 'Ana Costa'),
        (2, 'Lucas Costa'),
        (3, 'Mariana Ferreira'),
        (4, 4)
    ]
    cursor.executemany('INSERT INTO gestor_dim (fk_gestor, desc_gestor) VALUES (?, ?)', gestor)

    categoria = [
        (1,'Clima Organizacional'),
        (2,'Liderança'),
        (3,'Funções Desempenhadas'),
        (4,'Plano de Carreira e Desenvolvimento'),
        (5,'Ambiente e Condições de Trabalho'),
        (6,'Salários e Benefícios'),
        (7,'Satisfação e Engajamento'),
        (8,'Comunicação e Transparência')
    ]
    cursor.executemany('INSERT INTO categoria_dim (fk_categoria, desc_categoria) VALUES (?, ?)', categoria)

    # Insira alguns registros na tabela 'usuarios'
    usuarios = [
        (1, 6, 9, 9, 4),
        (2, 1, 8, 8, 1),
        (3, 2, 7, 7, 4),
        (4, 7, 5, 5, 3),
        (5, 3, 4, 4, 4),
        (6, 8, 3, 3, 3),
        (7, 1, 2, 2, 4),
        (8, 1, 8, 8, 1),
        (9, 4, 1, 1, 4),
        (10, 5, 6, 6, 2)
    ]
    cursor.executemany('INSERT INTO usuarios_dim (id, fk_cargo, fk_area, fk_subarea, fk_gestor) VALUES (?, ?, ?, ?, ?)', usuarios)

    perguntas = [
        (1,'Como avalio a frequência e qualidade das reuniões de equipe?',1),
        (2,'Como avalio a transparência da comunicação da empresa sobre objetivos e metas?',1),
        (3,'Como avalio o feedback construtivo que recebo sobre o meu desempenho?',1),
        (4,'Como avalio o reconhecimento do meu trabalho pela empresa?',1),
        (5,'Como eu avalio o conforto e segurança do espaço em que trabalho?',1),
        (6,'Nos últimos 3 meses em algum momento eu senti que não tinha tempo suficiente para realizar minhas funções?',1),
        (7,'O ambiente de trabalho possibilita a concentração necessária para desempenhar as minhas funções?',1),
        (8,'O quanto a cultura da empresa está alinhada com os meus valores?',2),
        (9,'Qaunto trabalhar aqui é motivo de orgulho para mim?', 2),
        (10,'Qual a probabilidade de indicar a empresa para um amigo?',2),
        (11,'Quanto a comunicação entre gestor e funcionários é transparente?',2),
        (12,'Quanto as formas de bonificações e recompensas fazem sentido para mim?',2),
        (13,'Quanto estou satisfeito com a minha remuneração?',2),
        (14,'Quanto eu acho que o meu salário é justo para as atividades que eu desempenho?',2),
        (15,'Quanto eu acredito que o meu chefe reconhece o meu potencial?',2),
        (16,'Quanto eu acredito que os valores da companhia são realmente colocados em prática?',2),
        (17,'Quanto eu entendo a importância das minhas atividades para os objetivos da organização?',3),
        (18,'Quanto eu entendo quais são as entregas necessárias para alcançar novas posições?',3),
        (19,'Quanto eu enxergo meu crescimento dentro da empresa?',3),
        (20,'Quanto eu enxergo valor nas minhas atividades para o sucesso do negócio?',3),
        (21,'Quanto eu me identifico com os propósitos da empresa?',3),
        (22,'Quanto eu me sinto capacitado para realizar no meu trabalho?',3),
        (23,'Quanto eu me sinto confortável com as minhas atividades?',3),
        (24,'Quanto eu me sinto confortável para pedir feedbacks ou desabafar com o meu chefe?',4),
        (25,'Quanto eu me sinto realizado profissionalmente?',4),
        (26,'Quanto eu possuo acesso a todas ferramentas físicas e digitais para desempenhar as minhas funções?',4),
        (27,'Quanto eu sinto que a minha opinião é levada em consideração para a solução de problemas?',4),
        (28,'Quanto eu sinto que tenho autonomia para executar as minhas tarefas?',5),
        (29,'Quanto eu tenho interesse em ocupar outros cargos dentro da organização?',5),
        (30,'Quanto me sinto feliz na empresa?',5),
        (31,'Quanto me sinto pertencente à empresa?',5),
        (32,'Quanto me sinto satisfeito com os benefícios que recebo?',5),
        (33,'Quanto meu ambiente de trabalho é adequado para realizar as minhas atividades?',6),
        (34,'Quanto meu superior informa sobre os fatos importantes que estão acontecendo na empresa?',6),
        (35,'Quanto meu superior oferece suporte para a realização do meu trabalho?',6),
        (36,'Quanto meu trabalho impacta positivamente na minha vida pessoal?',6),
        (37,'Quanto minhas entregas são valorizadas?',7),
        (38,'Quanto o dia a dia de trabalho é agradável para mim?',7),
        (39,'Quanto o meu gestor me incentiva a aprender e impulsionar minha carreira?',7),
        (40,'Quanto o plano de carreira para a minha posição é claro?',7),
        (41,'Quanto sinto confortável com a minha equipe de trabalho?',7),
        (42,'Quanto sinto que minhas necessidades ergonométricas são atendidas?',7),
        (43,'Quão claro é o meu gestor nas funções que delega?',8),
        (44,'Quão satisfeito eu estou com as funções desempenhadas no meu dia a dia?',8),
        (45,'Sinto que há colaboração entre eu e meus colegas de trabalho?',8),
        (46,'Sinto que meu ambiente de trabalho é agradável?',8),
        (47,'Sinto que minhas ideias são ouvidas pelo meu gestor?',8)
    ]
    cursor.executemany('INSERT INTO pergunta_dim (fk_pergunta, desc_pergunta, fk_categoria) VALUES (?, ?, ?)', perguntas)

    conn.commit()
    conn.close()

def consulta_db():
    conn, cursor = get_db()
    cursor.execute('SELECT desc_pergunta FROM perguta_dim WHERE fk_pergunta = ?', (2,))
    pergunta = cursor.fetchone()[0]
    conn.close()
    print(pergunta)

conn, cursor = get_db()
cursor.execute('DROP TABLE IF EXISTS sugestoes_fato')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sugestoes_fato (
        id_fantasia TEXT,
        fk_cargo INTEGER,
        fk_area INTEGER,
        fk_subarea INTEGER,
        fk_gestor INTEGER,
        fk_pergunta INTEGER,
        fk_categoria INTEGER,
        data TEXT,
        datetime TEXT,
        sugestao TEXT,
        id_autoidentificacao INTERGER,
        FOREIGN KEY (fk_cargo) REFERENCES cargo_dim (fk_cargo),
        FOREIGN KEY (fk_area) REFERENCES area_dim (fk_area),
        FOREIGN KEY (fk_subarea) REFERENCES subarea_dim (fk_subarea),
        FOREIGN KEY (fk_gestor) REFERENCES gestor_dim (fk_gestor),
        FOREIGN KEY (fk_pergunta) REFERENCES pergunta_dim (fk_pergunta),
        FOREIGN KEY (fk_categoria) REFERENCES categoria_dim (fk_categoria)
        FOREIGN KEY (id_autoidentificacao) REFERENCES usuarios_dim (id) 
    )
    ''')
conn.commit()
conn.close()