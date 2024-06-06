import sqlite3

conn = sqlite3.connect('clima_organizacional.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE respostas')

# Criar a tabela 'usuarios'
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY
)
''')

# cursor.execute('''
# INSERT INTO usuarios (id) VALUES (?)
# ''', [(1,), (2,), (3,)])

# Criar a tabela 'RESPOSTAS'
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



conn.commit()
conn.close()
