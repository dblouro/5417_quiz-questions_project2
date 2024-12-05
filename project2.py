"""
Lab ProjectoFinal_2
Trabalho efetuado por Diogo Louro, Ricardo Conceição e João Fernandes Silva
"""

import pandas as pd

#carregar o ficheiro .csv
df = pd.read_csv('quiz-questions.csv')

#mostrar as primeiras linhas
print(df.head(3))

import sqlite3
import tkinter as tk
import random

##ATIVIDADE 3.1

#verificar a versão do SQLite
print(f"SQLite version: {sqlite3.sqlite_version}")

#ligação à BD
conn = sqlite3.connect("quiz-questions.db")
cursor = conn.cursor()

#criar tabela
cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    option1 TEXT NOT NULL,
    option2 TEXT NOT NULL,
    option3 TEXT NOT NULL,
    option4 TEXT NOT NULL,
    correct INTEGER NOT NULL CHECK(correct BETWEEN 0 AND 3)
)
''')

for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO questions (question, option1, option2, option3, option4, correct)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['question'], row['option1'], row['option2'], row['option3'], row['option4'], row['correct']))

conn.commit()
conn.close()
print("Dados inseridos na BD")

#criar a janela, titulo e dimensões
root = tk.Tk()
root.title("Quiz Cinquenta e Quatro Dezasete")
root.geometry("400x400")

#voltar a abrir a ligação
conn = sqlite3.connect('quiz-questions.db')
cursor = conn.cursor()

#sacar uma pergunta aleatoriamente
cursor.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT 1')
perguntas = cursor.fetchone()

#mostrar a pergunta
print(perguntas)

#fechar a ligação à BD
conn.close()
