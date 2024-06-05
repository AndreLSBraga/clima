import sqlite3

conn = sqlite3.connect('clima_organizacional.db')
cursor = conn.cursor()

cursor.execute('''
DROP TABLE respostas
''')

# cursor.execute('''
# CREATE TABLE respostas (
#     id INTEGER,
#     data TEXT,
#     datetime TEXT,
#     descricao_pergunta TEXT,
#     resposta REAL,
#     sugestao TEXT
# )
# ''')

conn.commit()
conn.close()
