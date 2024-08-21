import mysql.connector
import random
from datetime import datetime, timedelta
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

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
    cursor.execute('DROP TABLE IF EXISTS usuarios')
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
            nome VARCHAR(255),
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
            id_sugestao VARCHAR(255) PRIMARY KEY,
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            fk_gestor INTEGER PRIMARY KEY,
            senha VARCHAR(255),
            tipo_usuario VARCHAR(255),
            logou INTEGER, 
            FOREIGN KEY (fk_gestor) REFERENCES gestor_dim(fk_gestor)
        )
    ''')
    print("Tabela gestor_dim criada com sucesso.")

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
        (1,'Aline Carvalho De Freitas','Aline',10,99788655),
        (2,'Alinne Priscila Goncalves Carvalho','Alinne',10,99752766),
        (3,'Amanda Machado Lesnik','Amanda',8,4449),
        (4,'Andressa Pereira De Castro','Andressa',8,99816511),
        (5,'Dayane Pereira Batista','Dayane',1,99750397),
        (6,'Enio Warley Mendes Eborgano','Enio',6,99772214),
        (7,'Everton Campelo Moreira De Oliveira','Everton',6,99739946),
        (8,'Ezequiel Pepe','Ezequiel',5,99739264),
        (9,'Filipe Moraes Nogueira','Filipe',3,99815888),
        (10,'Flavio Aparecido Correa De Carvalho','Flavio',6,99746018),
        (11,'Gabriel Henrique Franco Teodoro','Gabriel',8,99740736),
        (12,'Gabrielle Da Veiga Militao','Gabrielle',8,99786728),
        (13,'Graziele Rezende Miranda Menezes','Graziele',2,99767037),
        (14,'Guilherme Goncalves Barbosa','Guilherme',6,0),
        (15,'Helien Martins Figueiredo Junior','Helien',5,99762472),
        (16,'Henrique Pereira Lopes','Henrique',6,99740751),
        (17,'Izac Amon Alves Dos Santos','Izac',1,99755670),
        (18,'Jose Pedro Brandao Filho','Jose',6,99744801),
        (19,'Juliana Cristina Martins Da Costa','Juliana',11,99749835),
        (20,'Laura Cristina Goncalves Brandao','Laura',5,99804166),
        (21,'Luana Duarte Martins','Luana',3,99801843),
        (22,'Marcelo David Chahine','Marcelo',6,99784896),
        (23,'Markson Augusto Correa De Souza','Markson',2,99813229),
        (24,'Mauricio Ayres De Araujo','Mauricio',4,99771272),
        (25,'Mauricio Vieira De Sousa','Mauricio',2,99767843),
        (26,'Nathan Pereira Dos Santos Rodrigues','Nathan',2,99755408),
        (27,'Paulo Cesar Peixoto Rodrigues','Paulo',9,99705996),
        (28,'Pollyanna Do Nascimento Souza','Pollyanna',9,99766693),
        (29,'Rafael Martins Araujo Alves','Rafael',6,99729471),
        (30,'Raimundo Alberto Marques Dos Santos','Raimundo',2,99779845),
        (31,'Raquel Coradine Meireles','Raquel',9,99783026),
        (32,'Robson Machado De Freitas','Robson',7,99718077),
        (33,'Rodrigo Saraiva Dos Santos','Rodrigo',6,99739948),
        (34,'Rogerio Rodrigues Cardoso','Rogerio',6,99729181),
        (35,'Suelen Guadalupe Santiago','Suelen',6,99823774)
    ]
    cursor.executemany('INSERT INTO gestor_dim (fk_gestor, desc_gestor, nome, fk_area, id_gestor) VALUES (%s, %s, %s, %s, %s)', gestor)
    print("Insert na tabela gestor_dim com sucesso.")
    
    categoria = [
        (1,'Engagment'),
        (2,'Eficácia do Gestor'),
        (3,'Funções Desempenhadas'),
        (4,'Plano de Carreira'),
        (5,'Ambiente e Ferramentas de trabalho'),
        (6,'Salários e Benefícios'),
        (7,'Feedback e Reconhecimento'),
        (8,'Comunicação e Colaboração'),
        (9,'Serviços Gerais'),
        (10,'Segurança Psicológica')
    ]
    cursor.executemany('INSERT INTO categoria_dim (fk_categoria, desc_categoria) VALUES (%s, %s)', categoria)
    print("Insert na tabela categoria_dim com sucesso.")
    
    perguntas = [
        (1,'Tenho orgulho em trabalhar para a minha empresa?',1),
        (2,'Recomendo a Minha Empresa como um ótimo local para trabalhar?',1),
        (3,'Tendo a ficar na Minha Empresa por pelo menos mais 12 meses?',1),
        (4,'Estou extremamente satisfeito com a Minha Empresa como um local de trabalho?',1),
        (5,'O meu superior hierárquico preocupa-se realmente com o meu bem-estar?',2),
        (6,'Quando faço um excelente trabalho, as minhas conquistas são reconhecidas?',2),
        (7,'Quanto recomendaria o meu superior hierárquico a outras pessoas?',2),
        (8,'O meu superior hierárquico encoraja o trabalho de equipe?',2),
        (9,'O meu superior hierárquico fornece um feedback regular que me ajuda a crescer e a desenvolver-me?',2),
        (10,'Quão satisfeito eu estou com as funções desempenhadas no meu dia a dia?',3),
        (11,'Quanto eu enxergo conexão entre a minha rotina e a estratégia da cervejaria?',3),
        (12,'Quanto eu me sinto capacitado para realizar meus papéis e responsabilidades?',3),
        (13,'Nos últimos 3 meses, sinto que tive tempo suficiente para realizar minhas funções?',3),
        (14,'Quanto eu sinto que tenho autonomia para executar as minhas tarefas?',3),
        (15,'Quanto eu tenho interesse em ocupar outros cargos dentro da Cia?',4),
        (16,'Eu tenho um plano de desenvolvimento individual (PDI) e ele é claro?',4),
        (17,'Quanto eu estou preparado para dar um próximo passo na Cia?',4),
        (18,'Quanto eu entendo quais são as entregas necessárias para alcançar novas posições?',4),
        (19,'Quanto meu ambiente de trabalho é adequado para realizar as minhas atividades?',5),
        (20,'Como eu avalio o conforto e segurança do espaço em que trabalho?',5),
        (21,'Quanto eu possuo acesso a todas ferramentas físicas e digitais para desempenhar as minhas funções?',5),
        (22,'O ambiente de trabalho possibilita a concentração necessária para desempenhar as minhas funções?',5),
        (23,'Quanto eu meu sinto capacitado para utilizar todas as ferramentas digitais (SPLAN, SAP, SmartCheck, etc)?',5),
        (24,'Quanto sinto que minhas necessidades ergonométricas são atendidas?',5),
        (25,'A minha remuneração total (salário, RVO, GCA, Benefícios) é justa quando comparado com posições semelhantes em outras empresas?',6),
        (26,'Quanto eu acho que o meu salário é justo para as atividades que eu desempenho?',6),
        (27,'Quanto me sinto satisfeito com os benefícios da Cia?',6),
        (28,'Quão claro são as regras da Remuneração variável (RVO) e o acompanhamento das metas?',6),
        (29,'Qual a probabilidade de indicar a empresa para um amigo trabalhar?',7),
        (30,'Sinto que minhas ideias são ouvidas pelo meu gestor?',7),
        (31,'O meu time enxerga e valoriza a minha contribuição nas conquistas da área?',7),
        (32,'Eu recebo os feedbacks necessários para meu desenvolvimento?',7),
        (33,'Quanto eu me sinto realizado profissionalmente?',7),
        (34,'Como avalio o reconhecimento do meu trabalho pela empresa?',7),
        (35,'Como avalio a transparência da comunicação da empresa sobre objetivos e metas?',8),
        (36,'A comunicação nas reuniões de resultados é clara e transparente?',8),
        (37,'Como avalio a frequência e qualidade das reuniões de equipe?',8),
        (38,'Sinto que há colaboração entre as áreas?',8),
        (39,'Sinto que há colaboração entre eu e meus colegas de trabalho?',8),
        (40,'O quanto estou satisfeito com o restaurante?',9),
        (41,'O quanto estou satisfeito com o fretado?',9),
        (42,'O quanto estou satisfeito com a limpeza dos banheiros?',9),
        (43,'O quanto estou satisfeito com a limpeza das áreas produtivas?',9),
        (44,'Quanto me sinto pertencente ao time que estou?',10),
        (45,'Quanto eu me sinto confortável para pedir feedbacks e ajuda para meu gestor?',10),
        (46,'Tenho liberdade para sugerir mudanças na cervejaria?',10),
        (47,'Tenho segurança para não realizar atividades nas quais não sou treinado e capacitado?',10),

        #Perguntas adicionadas posteriormente
        (48,'Quanto meu trabalho impacta positivamente na minha vida pessoal?',1),
        (49,'Quanto a comunicação entre você e seu gestor direto é transparente?',8)
    ]

    cursor.executemany('INSERT INTO pergunta_dim (fk_pergunta, desc_pergunta, fk_categoria) VALUES (%s, %s, %s)', perguntas)
    print("Insert na tabela pergunta_dim com sucesso.")
    
    usuarios = [
        (1,'pulsa7l'),
        (2,'pulsa7l'),
        (3,'pulsa7l'),
        (4,'pulsa7l'),
        (5,'pulsa7l'),
        (6,'pulsa7l'),
        (7,'pulsa7l'),
        (8,'pulsa7l'),
        (9,'pulsa7l'),
        (10,'pulsa7l'),
        (11,'pulsa7l'),
        (12,'pulsa7l'),
        (13,'pulsa7l'),
        (14,'pulsa7l'),
        (15,'pulsa7l'),
        (16,'pulsa7l'),
        (17,'pulsa7l'),
        (18,'pulsa7l'),
        (19,'pulsa7l'),
        (20,'pulsa7l'),
        (21,'pulsa7l'),
        (22,'pulsa7l'),
        (23,'pulsa7l'),
        (24,'pulsa7l'),
        (25,'pulsa7l'),
        (26,'pulsa7l'),
        (27,'pulsa7l'),
        (28,'pulsa7l'),
        (29,'pulsa7l'),
        (30,'pulsa7l'),
        (31,'pulsa7l'),
        (32,'pulsa7l'),
        (33,'pulsa7l'),
        (34,'pulsa7l'),
        (35,'pulsa7l')
    ]
    cursor.executemany('INSERT INTO usuarios (fk_gestor, senha) VALUES (%s, %s)', usuarios)
    print("Insert na tabela usuarios com sucesso.")

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
# cursor.execute('select distinct fk_gestor from respostas_fato')
# gestor = cursor.fetchall()
# print(f'Gestor: {gestor}')
# conn.commit()
# conn.close()
