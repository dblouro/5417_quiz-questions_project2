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
from tkinter import messagebox
import random

questions = []
index_question = 0
correct_answer = 0

##ESTRUTURA DA BD

#verificar a versão do SQLite
print(f"SQLite version: {sqlite3.sqlite_version}")

#ligação à BD
conn = sqlite3.connect("quiz-questions.db")
cursor = conn.cursor()
#criar tabela das questões
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
print("Tabela Questions inserida na BD (perguntas idem)")


conn = sqlite3.connect("quiz-questions.db")
cursor = conn.cursor()
#criar tabelas USERS e SCORES
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        pw TEXT NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        date DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')
conn.commit()
conn.close()
print("Tabelas USERS e SCORES inseridos na BD")



#voltar a abrir a ligação
conn = sqlite3.connect('quiz-questions.db')
cursor = conn.cursor()

#sacar uma pergunta aleatoriamente
cursor.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT 1')
perguntas = cursor.fetchone()

#mostrar a pergunta
print(perguntas)
conn.close()

##FUNÇÔES

#função LOGIN
def login():
    name = entry_name.get()
    pw = entry_pw.get()

      
    conn = sqlite3.connect('quiz-questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name = ? AND pw = ?', (name, pw))
    utilizador = cursor.fetchone()
    conn.close()

    if utilizador:
        messagebox.showinfo("Login com sucesso", f"Bem-vindo, {name}!")
        iniciar_quiz(utilizador[0])
    else:
        messagebox.showerror("Erro de Login", "Nome ou senha errados!")

#função REGISTAR
def registar():
    name = entry_name.get()
    pw = entry_pw.get()

    if not name or not pw:
        messagebox.showinfo(text="Preencha todos os campos")
        return
      
    try:
        conn = sqlite3.connect('quiz-questions.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, pw) VALUES (?, ?)', (name, pw))
        conn.commit()
        conn.close()
        messagebox.showinfo("Registo com sucesso", "Utilizador registado!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Nome de utilizador já existe!")

#função REGISTAR SCORES
def registar_pontuacao(user_id, score):
    conn = sqlite3.connect('quiz-questions.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scores (user_id, score) VALUES (?, ?)', (user_id, score))
    conn.commit()
    conn.close()
    messagebox.showinfo("Pontuação Registada", "A sua pontuação foi guardada!")

#função VERIFICA RESPOSTA
def verificar_resposta(opcao):
    if opcao == perguntas[6]:  #Índice 6 corresponde à coluna `correct`
        messagebox.showinfo("Correto!", "Resposta certa!")
    else:
        messagebox.showerror("Errado!", "Resposta errada!")
    carregar_nova_pergunta()



#função PROGRESSO
def ver_progresso(user_id):
    conn = sqlite3.connect('quiz-questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT score, date FROM scores WHERE user_id = ? ORDER BY date DESC', (user_id,))
    historico = cursor.fetchall()
    conn.close()
    
    if historico:
        progresso = "\n".join([f"Pontuação: {p[0]} - Data: {p[1]}" for p in historico])
        messagebox.showinfo("Progresso", progresso)
    else:
        messagebox.showinfo("Progresso", "Nenhuma pontuação registada")

def iniciar_quiz(user_id):
    login_frame.pack_forget()
    quiz_frame.pack()

    quiz_frame.user_id = user_id
    quiz_frame.score = 0
    quiz_frame.questions_asked = 0 
    mostrar_pergunta()

def mostrar_pergunta():
    # Verificar se já foram feitas 10 perguntas
    if quiz_frame.questions_asked >= 10:
        finalizar_quiz()
        return
    
    conn = sqlite3.connect('quiz-questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT 1')
    pergunta = cursor.fetchone()
    conn.close()

    if pergunta:
        quiz_frame.current_question = pergunta
        question_id, question, *options, correct = pergunta

        lbl_question.config(text=question)
        for i in range(4):
            radio_buttons[i].config(text=options[i], value=i)

        quiz_frame.correct_answer = correct
    else:
        finalizar_quiz()

def verificar_resposta():
    resposta = var_answer.get()
    if resposta == quiz_frame.correct_answer:
        messagebox.showinfo("Correto!", "A sua resposta está certa!")
        quiz_frame.score += 1
    else:
        correct_option = quiz_frame.current_question[quiz_frame.correct_answer + 2]
        messagebox.showinfo("Errado!", f"A resposta correta era: {correct_option}")
    
    # Incrementar o contador de perguntas
    quiz_frame.questions_asked += 1
    mostrar_pergunta()

def finalizar_quiz():
    registar_pontuacao(quiz_frame.user_id, quiz_frame.score)
    messagebox.showinfo("Fim do Quiz", f"Sua pontuação final é: {quiz_frame.score}")
    quiz_frame.pack_forget()
    login_frame.pack()


##INTERFACE

#criar a janela, titulo e dimensões
root = tk.Tk()
root.title("Quiz Cinquenta e Quatro Dezasete")
root.geometry("400x400")

#widget login
frame_login = tk.Frame(root)
frame_login.pack()

tk.Label(frame_login, text="Nome").pack()
entry_name = tk.Entry(frame_login)
entry_name.pack()

tk.Label(frame_login, text="Senha").pack()
entry_pw = tk.Entry(frame_login, show="*")
entry_pw.pack()

#widget botao
tk.Button(login_frame, text="Login", command=login).pack(pady=5)
tk.Button(login_frame, text="Registar", command=registar).pack(pady=5)

# Frame do Quiz
quiz_frame = tk.Frame(root)

lbl_question = tk.Label(quiz_frame, text="", wraplength=300)
lbl_question.pack(pady=10)

var_answer = tk.IntVar()
radio_buttons = []
for i in range(4):
    rb = tk.Radiobutton(quiz_frame, text="", variable=var_answer, value=i)
    rb.pack(anchor="w")
    radio_buttons.append(rb)

tk.Button(quiz_frame, text="Responder", command=verificar_resposta).pack(pady=10)
tk.Button(quiz_frame, text="Terminar", command=finalizar_quiz).pack(pady=10)

#produzir o resultado
root.mainloop()