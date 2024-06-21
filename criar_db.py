import mysql.connector
import random
from datetime import datetime, timedelta
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, ADMIN_LOGIN, ADMIN_LOGIN_SENHA

def get_db():
    conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
    return conn, conn.cursor()

def create_db():
    conn, cursor = get_db()
    try:
        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {MYSQL_DB}')  # Cria o banco de dados pulsa se ele não existir
        conn.commit()
        print("Banco de dados 'pulsa' criado com sucesso.")
    except mysql.connector.Error as err:
        print(f"Erro ao criar o banco de dados 'pulsa': {err}")
    finally:
        conn.close()

def drop_tables():
    conn, cursor = get_db()
    cursor.execute(f"USE {MYSQL_DB}")
    cursor.execute('DROP TABLE IF EXISTS pergunta_dim')
    cursor.execute('DROP TABLE IF EXISTS categoria_dim')
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
    cursor.execute(f"USE {MYSQL_DB}")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cargo_dim (
            fk_cargo INTEGER PRIMARY KEY,
            desc_cargo VARCHAR(255)
        )
    ''')
    print("Tabela cargo_dim criada com sucesso.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS area_dim (
            fk_area INTEGER PRIMARY KEY,
            desc_area VARCHAR(255)
        )
    ''')
    print("Tabela area_dim criada com sucesso.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subarea_dim (
            fk_subarea INTEGER PRIMARY KEY,
            desc_subarea VARCHAR(255)
        )
    ''')
    print("Tabela subarea_dim criada com sucesso.")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gestor_dim (
            fk_gestor INTEGER PRIMARY KEY,
            desc_gestor VARCHAR(255),
            fk_area INTEGER,
            id_gestor INTEGER,
            FOREIGN KEY (fk_area) REFERENCES area_dim(fk_area)
        )
    ''')
    print("Tabela gestor_dim criada com sucesso.")
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categoria_dim (
            fk_categoria INTEGER PRIMARY KEY,
            desc_categoria VARCHAR(255)
        )
    ''')
    print("Tabela categoria_dim criada com sucesso.")
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pergunta_dim (
            fk_pergunta INTEGER PRIMARY KEY,
            desc_pergunta VARCHAR(255),
            fk_categoria INTEGER,
            FOREIGN KEY (fk_categoria) REFERENCES categoria_dim(fk_categoria)
        )
    ''')
    print("Tabela pergunta_dim criada com sucesso.")
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas_fato (
            fk_subarea INTEGER,
            fk_gestor INTEGER,
            fk_cargo INTEGER,
            idade VARCHAR(255),
            genero VARCHAR(255),
            fk_pergunta INTEGER,
            fk_categoria INTEGER,
            semana VARCHAR(255),
            data DATE,
            datetime DATETIME,
            resposta REAL,
            FOREIGN KEY (fk_cargo) REFERENCES cargo_dim(fk_cargo),
            FOREIGN KEY (fk_subarea) REFERENCES subarea_dim(fk_subarea),
            FOREIGN KEY (fk_gestor) REFERENCES gestor_dim(fk_gestor),
            FOREIGN KEY (fk_pergunta) REFERENCES pergunta_dim(fk_pergunta),
            FOREIGN KEY (fk_categoria) REFERENCES categoria_dim(fk_categoria)
        )
    ''')
    print("Tabela respostas_fato criada com sucesso.")
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sugestoes_fato (
            id VARCHAR(255) PRIMARY KEY,
            fk_cargo INTEGER,
            fk_area INTEGER,
            fk_subarea INTEGER,
            fk_gestor INTEGER,
            idade VARCHAR(255),
            genero VARCHAR(255),
            fk_pergunta INTEGER,
            fk_categoria INTEGER,
            semana VARCHAR(255),
            data DATE,
            datetime DATETIME,
            sugestao TEXT,
            respondido INTEGER,
            FOREIGN KEY (fk_cargo) REFERENCES cargo_dim(fk_cargo),
            FOREIGN KEY (fk_area) REFERENCES area_dim(fk_area),
            FOREIGN KEY (fk_subarea) REFERENCES subarea_dim(fk_subarea),
            FOREIGN KEY (fk_gestor) REFERENCES gestor_dim(fk_gestor),
            FOREIGN KEY (fk_pergunta) REFERENCES pergunta_dim(fk_pergunta),
            FOREIGN KEY (fk_categoria) REFERENCES categoria_dim(fk_categoria)
        )
    ''')
    print("Tabela sugestoes_fato criada com sucesso.")
    

    conn.commit()
    conn.close()

def insert_dados():
    conn, cursor = get_db()
    cursor.execute(f"USE {MYSQL_DB}")
    cargo = [
        (1,'Analista'),
        (2,'Aprendiz'),
        (4,'Conferente'),
        (5,'Coordenador'),
        (6,'Estagiário'),
        (7,'Gerente'),
        (3,'Operador'),
        (8,'Supervisor'),
        (9,'Técnico')
    ]
    cursor.executemany('INSERT INTO cargo_dim (fk_cargo, desc_cargo) VALUES (%s, %s)', cargo)
    print("Insert na tabela cargo_dim com sucesso.")
    
    area = [
        (1,'Bblend'),
        (2,'Energia e Fluídos'),
        (3,'Gente e Gestão'),
        (4,'Gerência'),
        (5,'Logística'),
        (6,'Packaging Cerveja'),
        (7,'Packaging Refri'),
        (8,'Processo Cerveja'),
        (9,'Processo Refri'),
        (10,'Qualidade'),
        (11,'Segurança do Trabalho')
    ]
    cursor.executemany('INSERT INTO area_dim (fk_area, desc_area) VALUES (%s, %s)', area)
    print("Insert na tabela area_dim com sucesso.")
    

    subarea = [
        (1,'Bblend'),
        (2,'Energia e Fluídos'),
        (3,'Gente e Gestão'),
        (4,'Gerência'),
        (5,'Logística'),
        (6,'Packaging Cerveja'),
        (7,'Packaging Refri'),
        (8,'Processo Cerveja'),
        (9,'Processo Refri'),
        (10,'Qualidade'),
        (11,'Segurança do Trabalho')
    ]
    cursor.executemany('INSERT INTO subarea_dim (fk_subarea, desc_subarea) VALUES (%s, %s)', subarea)
    print("Insert na tabela subarea_dim com sucesso.")
    
    gestor = [
        (1,'Aline Carvalho De Freitas',10,1),
        (2,'Alinne Priscila Goncalves Carvalho',10,1),
        (3,'Amanda Machado Lesnik',8,1),
        (4,'Andressa Pereira De Castro',8,1),
        (5,'Dayane Pereira Batista',1,1),
        (6,'Diogo Figueiredo Turbay Rangel',4,1),
        (7,'Enio Warley Mendes Eborgano',6,1),
        (8,'Everton Campelo Moreira De Oliveira',6,1),
        (9,'Ezequiel Pepe',5,1),
        (10,'Filipe Moraes Nogueira',3,1),
        (11,'Flavio Aparecido Correa De Carvalho',6,1),
        (12,'Gabriel Henrique Franco Teodoro',8,1),
        (13,'Gabrielle Da Veiga Militao',8,1),
        (14,'Graziele Rezende Miranda Menezes',2,1),
        (15,'Guilherme Goncalves Barbosa',6,1),
        (16,'Helien Martins Figueiredo Junior',5,1),
        (17,'Henrique Pereira Lopes',6,1),
        (18,'Izac Amon Alves Dos Santos',1,1),
        (19,'Jose Pedro Brandao Filho',6,1),
        (20,'Juliana Cristina Martins Da Costa',11,1),
        (21,'Laura Cristina Goncalves Brandao',5,1),
        (22,'Luana Duarte Martins',3,1),
        (23,'Marcelo David Chahine',6,1),
        (24,'Markson Augusto Correa De Souza',2,1),
        (25,'Mauricio Ayres De Araujo',4,1),
        (26,'Mauricio Vieira De Sousa',2,1),
        (27,'Nathan Pereira Dos Santos Rodrigues',2,1),
        (28,'Paulo Cesar Peixoto Rodrigues',9,1),
        (29,'Pollyanna Do Nascimento Souza',9,1),
        (30,'Rafael Martins Araujo Alves',6,1),
        (31,'Raimundo Alberto Marques Dos Santos',2,1),
        (32,'Raquel Coradine Meireles',9,1),
        (33,'Robson Machado De Freitas',7,1),
        (34,'Rodrigo Saraiva Dos Santos',6,1),
        (35,'Rogerio Rodrigues Cardoso',6,1),
        (36,'Suelen Guadalupe Santiago',6,1)
    ]
    cursor.executemany('INSERT INTO gestor_dim (fk_gestor, desc_gestor, fk_area, id_gestor) VALUES (%s, %s, %s, %s)', gestor)
    print("Insert na tabela gestor_dim com sucesso.")
    
    categoria = [
        (1,'Clima Organizacional'),
        (2,'Liderança'),
        (3,'Funções Desempenhadas'),
        (4,'Plano de Carreira e Desenvolvimento'),
        (5,'Ambiente e Condições de Trabalho'),
        (6,'Salários e Benefícios'),
        (7,'Feedback e Reconhecimento'),
        (8,'Comunicação e Transparência'),
        (9,'Segurança Psicológica'),
        (10,'Serviços Gerais')
    ]
    cursor.executemany('INSERT INTO categoria_dim (fk_categoria, desc_categoria) VALUES (%s, %s)', categoria)
    print("Insert na tabela categoria_dim com sucesso.")
    
    perguntas = [
        # Clima Organizacional
        (1, 'Como avalio a frequência e qualidade das reuniões de equipe?', 1),
        (2, 'Como avalio a transparência da comunicação da empresa sobre objetivos e metas?', 1),
        (3, 'Como avalio o feedback construtivo que recebo sobre o meu desempenho?', 1),
        (4, 'Como avalio o reconhecimento do meu trabalho pela empresa?', 1),
        (5, 'Nos últimos 3 meses em algum momento eu senti que não tinha tempo suficiente para realizar minhas funções?', 1),
        (6, 'Quanto me sinto feliz na empresa?', 1),
        (7, 'Quanto me sinto pertencente à empresa?', 1),
        (8, 'Sinto que há colaboração entre eu e meus colegas de trabalho?', 1),

        # Liderança
        (9, 'O quanto a cultura da empresa está alinhada com os meus valores?', 2),
        (10, 'Quanto trabalhar aqui é motivo de orgulho para mim?', 2),
        (11, 'Qual a probabilidade de indicar a empresa para um amigo/familiar?', 2),
        (12, 'Quanto a comunicação entre gestor e funcionários é transparente?', 2),
        (13, 'Quanto eu acredito que o meu chefe reconhece o meu potencial?', 2),
        (14, 'Quão claro é o meu gestor nas funções que delega?', 2),
        (15, 'Sinto que minhas ideias são ouvidas pelo meu gestor?', 2),

        # Funções Desempenhadas
        (16, 'Como eu avalio o conforto e segurança do espaço em que trabalho?', 3),
        (17, 'O ambiente de trabalho possibilita a concentração necessária para desempenhar as minhas funções?', 3),
        (18, 'Quanto eu entendo a importância das minhas atividades para os objetivos da organização?', 3),
        (19, 'Quanto eu enxergo valor nas minhas atividades para o sucesso do negócio?', 3),
        (20, 'Quanto eu me sinto capacitado para realizar no meu trabalho?', 3),
        (21, 'Quanto eu me sinto confortável com as minhas atividades?', 3),
        (22, 'Quão satisfeito eu estou com as funções desempenhadas no meu dia a dia?', 3),
        (23, 'Quanto meu trabalho impacta positivamente na minha vida pessoal?', 3),

        # Plano de Carreira e Desenvolvimento
        (24, 'Quanto eu entendo quais são as entregas necessárias para alcançar novas posições?', 4),
        (25, 'Quanto eu enxergo meu crescimento dentro da empresa?', 4),
        (26, 'Quanto eu me sinto confortável para pedir feedbacks ou desabafar com o meu chefe?', 4),
        (27, 'Quanto eu me sinto realizado profissionalmente?', 4),
        (28, 'Quanto eu possuo acesso a todas ferramentas físicas e digitais para desempenhar as minhas funções?', 4),
        (29, 'Quanto eu tenho interesse em ocupar outros cargos dentro da organização?', 4),
        (30, 'Quanto o meu gestor me incentiva a aprender e impulsionar minha carreira?', 4),
        (31, 'Quanto o plano de carreira para a minha posição é claro?', 4),

        # Ambiente e Condições de Trabalho
        (32, 'Quanto eu sinto que tenho autonomia para executar as minhas tarefas?', 5),
        (33, 'Quanto meu ambiente de trabalho é adequado para realizar as minhas atividades?', 5),
        (34, 'Sinto que meu ambiente de trabalho é agradável?', 5),
        (35, 'Sinto que as instalações de trabalho são adequadas e bem mantidas?', 5),
        (36, 'Sinto que as ferramentas e equipamentos fornecidos são adequados para minhas tarefas diárias?', 5),
        (37, 'Sinto que recebo o suporte necessário para realizar meu trabalho de maneira eficaz?', 5),
        (38, 'Sinto que os procedimentos de segurança são seguidos corretamente em meu local de trabalho?', 5),
        (39, 'Sinto que meu ambiente de trabalho é limpo e organizado?', 5),

        # Salários e Benefícios
        (40, 'Quanto as formas de bonificações e recompensas fazem sentido para mim?', 6),
        (41, 'Quanto estou satisfeito com a minha remuneração?', 6),
        (42, 'Quanto eu acho que o meu salário é justo para as atividades que eu desempenho?', 6),
        (43, 'Quanto me sinto satisfeito com os benefícios que recebo?', 6),

        # Feedback e Reconhecimento
        (44, 'Como avalio o feedback construtivo que recebo sobre o meu desempenho?', 7),
        (45, 'Como avalio o reconhecimento do meu trabalho pela empresa?', 7),
        (46, 'Quanto eu sinto que a minha opinião é levada em consideração para a solução de problemas?', 7),
        (47, 'Quanto minhas entregas são valorizadas?', 7),

        # Comunicação e Transparência
        (48, 'Como avalio a transparência da comunicação da empresa sobre objetivos e metas?', 8),
        (49, 'Quanto a comunicação entre gestor e funcionários é transparente?', 8),
        (50, 'Quanto meu superior informa sobre os fatos importantes que estão acontecendo na empresa?', 8),
        (51, 'Quanto meu superior oferece suporte para a realização do meu trabalho?', 8),
        (52, 'Quão claro é o meu gestor nas funções que delega?', 8),
        (53, 'Sinto que minhas ideias são ouvidas pelo meu gestor?', 8),

        # Segurança Psicológica
        (54, 'Quanto eu me sinto confortável para pedir feedbacks ou desabafar com o meu chefe?', 9),
        (55, 'Sinto que posso cometer erros sem medo de ser punido?', 9),
        (56, 'Sinto que posso expressar minhas opiniões sem receio de represálias?', 9),
        (57, 'Sinto que meu gestor valoriza meu bem-estar emocional?', 9),
        (58, 'Sinto que há abertura para discutir problemas ou preocupações no trabalho?', 9),
        (59, 'Sinto que sou tratado com respeito e dignidade por meus colegas de trabalho?', 9),

        # Serviços Gerais
        (60, 'Sinto que as instalações de trabalho são adequadas e bem mantidas?', 10),
        (61, 'Sinto que as ferramentas e equipamentos fornecidos são adequados para minhas tarefas diárias?', 10),
        (62, 'Sinto que recebo o suporte necessário para realizar meu trabalho de maneira eficaz?', 10),
        (63, 'Sinto que os procedimentos de segurança são seguidos corretamente em meu local de trabalho?', 10),
        (64, 'Sinto que meu ambiente de trabalho é limpo e organizado?', 10)
    ]
    cursor.executemany('INSERT INTO pergunta_dim (fk_pergunta, desc_pergunta, fk_categoria) VALUES (%s, %s, %s)', perguntas)
    print("Insert na tabela pergunta_dim com sucesso.")
    
    conn.commit()
    conn.close()

def consulta_db():
    conn, cursor = get_db()
    cursor.execute('SELECT desc_pergunta FROM perguta_dim WHERE fk_pergunta = %s', (2,))
    pergunta = cursor.fetchone()[0]
    conn.close()
    print(pergunta)

def random_date(start_date, end_date):
    """ Gera uma data aleatória entre start_date e end_date """
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

def insert_respostas_fato():
    conn, cursor = get_db()

    fixed_time = '10:00:00'

    # Possíveis valores para idade e genero
    idades = ["24", "25-39", "40-54", "55+"]
    generos = ["M", "F", "ND"]

    # Gerar 500 linhas de dados de exemplo
    for i in range(1, 501):
        # Gerar dados aleatórios
        fk_cargo = random.randint(1, 8)
        fk_subarea = random.randint(1, 9)
        fk_gestor = random.randint(1, 4)
        fk_pergunta = random.randint(1, 57 )
        fk_categoria = random.randint(1, 10)
        
        # Selecionar idade e genero aleatórios
        idade = random.choice(idades)
        genero = random.choice(generos)
        
        # Gerar data aleatória nos últimos 3 meses
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 90 dias para trás
        data = random_date(start_date, end_date)
        
        # Utilizar o horário fixo definido
        datetime_str = f'{data.strftime("%Y-%m-%d")} {fixed_time}'
        semana_atual = data.isocalendar()[1]
        resposta = round(random.uniform(0, 10), 2)

        # Inserir na tabela respostas_fato
        cursor.execute('''
            INSERT INTO respostas_fato 
            (fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_pergunta, fk_categoria, semana, data, datetime, resposta) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (fk_subarea, fk_gestor, fk_cargo, idade, genero, fk_pergunta, fk_categoria, semana_atual, data.strftime('%Y-%m-%d'), datetime_str, resposta))

    conn.commit()
    conn.close()

create_db()
drop_tables()
create_tables()
insert_dados()
# insert_respostas_fato()


# conn, cursor = get_db()
# # cursor.execute('DROP TABLE IF EXISTS sugestoes_fato')
# # # Crie a tabela 'usuarios_respostas_fato'
# # cursor.execute('''
# #     CREATE TABLE IF NOT EXISTS sugestoes_fato (
# #         id TEXT,
# #         fk_cargo INTEGER,
# #         fk_area INTEGER,
# #         fk_subarea INTEGER,
# #         fk_gestor INTEGER,
# #         idade TEXT,
# #         genero TEXT,
# #         fk_pergunta INTEGER,
# #         fk_categoria INTEGER,
# #         semana TEXT,
# #         data TEXT,
# #         datetime TEXT,
# #         sugestao TEXT,
# #         respondido INTEGER,
# #         FOREIGN KEY (fk_cargo) REFERENCES cargo_dim (fk_cargo),
# #         FOREIGN KEY (fk_subarea) REFERENCES subarea_dim (fk_subarea),
# #         FOREIGN KEY (fk_gestor) REFERENCES gestor_dim (fk_gestor),
# #         FOREIGN KEY (fk_pergunta) REFERENCES pergunta_dim (fk_pergunta),
# #         FOREIGN KEY (fk_categoria) REFERENCES categoria_dim (fk_categoria)
# #     )
# #     ''')

# cursor.execute('INSERT into categoria_dim (fk_categoria, desc_categoria) values(%s, %s)', (10, "Serviços Gerais"))
# conn.commit()
# conn.close()
