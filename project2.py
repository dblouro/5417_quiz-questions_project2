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

conn.commit()
conn.close()


#criar a janela, titulo e dimensões
root = tk.Tk()
root.title("Quiz Cinquenta e Quatro Dezasete")
root.geometry("400x400")

