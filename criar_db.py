import sqlite3
import os

# Defina o caminho para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'clima_organizacional.db')

# Conecte-se ao banco de dados
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Exclua a tabela 'respostas' se ela existir
cursor.execute('DROP TABLE IF EXISTS respostas')

# Crie a tabela 'usuarios'
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY
)
''')

# Insira alguns registros na tabela 'usuarios'
# usuarios = [(1,), (2,), (3,)]
# cursor.executemany('''
# INSERT INTO usuarios (id) VALUES (?)
# ''', usuarios)

# Crie a tabela 'respostas'
cursor.execute('''
CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER,
    data TEXT,
    datetime TEXT,
    descricao_pergunta TEXT,
    resposta REAL,
    sugestao TEXT,
    FOREIGN KEY (id) REFERENCES usuarios (id)
)
''')

# Confirme as mudanças e feche a conexão
conn.commit()
conn.close()
