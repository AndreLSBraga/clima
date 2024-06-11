import sqlite3
import os

# Defina o caminho para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'clima_organizacional.db')

# Conecte-se ao banco de dados
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Exclua a tabela 'respostas' se ela existir
cursor.execute('DROP TABLE IF EXISTS usuarios')
cursor.execute('DROP TABLE IF EXISTS respostas')
cursor.execute('DROP TABLE IF EXISTS sugestoes')

# Crie a tabela 'usuarios'
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY,
    cargo TEXT,
    area TEXT,
    gestor TEXT
)
''')

# Crie a tabela 'respostas'
cursor.execute('''
CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER,
    data TEXT,
    datetime TEXT,
    descricao_pergunta TEXT,
    resposta REAL,
    FOREIGN KEY (id) REFERENCES usuarios (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sugestoes (
    id INTEGER,
    area TEXT,
    data TEXT,
    datetime TEXT,
    categoria TEXT,
    pergunta TEXT,
    sugestao TEXT,
    auto_identificacao INT,
    id_auto_identificacao INT,
    FOREIGN KEY (id) REFERENCES usuarios (id)
)
''')

# Insira alguns registros na tabela 'usuarios'
usuarios = [
    (1, 'Gerente', 'Vendas', 'Carlos Silva'),
    (2, 'Analista', 'TI', 'Ana Costa'),
    (3, 'Assistente', 'RH', 'Pedro Souza'),
    (4, 'Supervisor', 'Produção', 'Fernanda Lima'),
    (5, 'Coordenador', 'Marketing', 'João Pereira'),
    (6, 'Técnico', 'Manutenção', 'Mariana Ferreira'),
    (7, 'Consultor', 'Financeiro', 'Rodrigo Oliveira'),
    (8, 'Desenvolvedor', 'TI', 'Paula Santos'),
    (9, 'Designer', 'Criação', 'Juliana Almeida'),
    (10, 'Engenheiro', 'Projetos', 'Lucas Costa')
]
cursor.executemany('INSERT INTO usuarios (id, cargo, area, gestor) VALUES (?, ?, ?, ?)', usuarios)




# Confirme as mudanças e feche a conexão
conn.commit()
conn.close()
