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
import openpyxl
from openpyxl.styles import Alignment

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
        INSERT OR IGNORE INTO questions (question, option1, option2, option3, option4, correct)
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
        user_id = utilizador[0]
        messagebox.showinfo("Login com sucesso", f"Bem-vindo, {name}!")
        mostrar_menu_principal(user_id, name)
    else:
        messagebox.showerror("Erro de Login", "Nome ou senha errados!")


#funçao MENU PRINCIPAL
def mostrar_menu_principal(user_id, name): 
    # Esconder o frame de login
    login_frame.pack_forget()
    
    # Mostrar o frame do menu principal
    menu_frame.pack()

    # Cria o menu de boas-vindas
    welcome_label = tk.Label(menu_frame, text=f"Bem-vindo, {name}!", font=("Arial", 14))
    welcome_label.pack(pady=10)

    # Criação do Canvas com Scroll
    canvas = tk.Canvas(menu_frame)
    scrollbar = tk.Scrollbar(menu_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    #limpar o conteúdo anterior no frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    #historico de pontuaçoes no menu
    ver_progresso_com_scroll(user_id, scrollable_frame)
    #exportar resultados
    tk.Button(menu_frame, text="Exportar Resultados", 
              command=lambda: exportar_resultados(user_id)).pack(pady=5)

    #botao para iniciar o quiz
    tk.Button(menu_frame, text="Iniciar Quiz", command=lambda: iniciar_quiz(user_id)).pack(pady=10)

    #botao para sair do jogo
    tk.Button(menu_frame, text="Sair", command=root.quit).pack(pady=5)
    
    #canvas + scroll
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


#função REGISTAR USER
def registar():
    name = entry_name.get()
    pw = entry_pw.get()
    
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


#função PROGRESSO
def ver_progresso_com_scroll(user_id, frame):
    conn = sqlite3.connect('quiz-questions.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT score, date FROM scores WHERE user_id = ? ORDER BY date DESC', (user_id,))
    
    pontuacoes = cursor.fetchall()
    conn.close()

    for i, pontuacao in enumerate(pontuacoes[:10]):  #mostrar apenas as 10 ultimas pontuaçoes
        label = tk.Label(frame, text=f"Jogo {i+1}: {pontuacao[0]} pontos - {pontuacao[1]}")
        label.pack(anchor="w", padx=10, pady=2)

    if len(pontuacoes) > 10:
        scroll_label = tk.Label(frame, text="Exibindo as últimas 10 pontuações")
        scroll_label.pack(pady=10)


def iniciar_quiz(user_id):
    login_frame.pack_forget()
    quiz_frame.pack()

    quiz_frame.timer_id = None
    quiz_frame.user_id = user_id
    quiz_frame.score = 0 #contador de pontos
    quiz_frame.correct_count = 0 #contador de certas
    quiz_frame.incorrect_count = 0 #contador de erradas
    quiz_frame.questions_asked = 0 #contador de perguntas feitas
    quiz_frame.quiz_active = True

    mostrar_pergunta()

def atualizar_timer():
    if quiz_frame.time_left > 0:
        lbl_timer.config(text=f"Tempo restante: {quiz_frame.time_left} segundos")
        quiz_frame.time_left -= 1
        quiz_frame.timer_id = root.after(1000, atualizar_timer)
    else:
        lbl_timer.config(text="Tempo esgotado!")
        quiz_frame.questions_asked += 1
        mostrar_pergunta()

def mostrar_pergunta():
    # verificar se já foram feitas 10 perguntas
    if quiz_frame.questions_asked >= 10:
        finalizar_quiz()
        return

    #cancela temporizador anterior de forma a evitar sobreposiçao
    if quiz_frame.timer_id is not None:
        root.after_cancel(quiz_frame.timer_id)
        quiz_frame.timer_id = None
    
    conn = sqlite3.connect('quiz-questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT 1')
    pergunta = cursor.fetchone()
    conn.close()

    if pergunta:
        quiz_frame.current_question = pergunta
        question_id, question, *options, correct = pergunta

        #logica para as respontas random funcionar
        options_with_indices = list(enumerate(options))
        random.shuffle(options_with_indices)
        #atualizar as opções e o índice correto
        shuffled_options = [opt[1] for opt in options_with_indices]
        new_correct_index = [opt[0] for opt in options_with_indices].index(correct)

        lbl_question.config(text=question)
        for i, opt in enumerate(shuffled_options):
            radio_buttons[i].config(text=opt, value=i)

        quiz_frame.correct_answer = new_correct_index

        #reinicia o timer
        quiz_frame.time_left = 10  #inicia com 10 segundos
        atualizar_timer()
    else:
        finalizar_quiz()




def verificar_resposta():
    resposta = var_answer.get()
    if resposta == quiz_frame.correct_answer:
        messagebox.showinfo("Correto!", "A sua resposta está certa!")
        quiz_frame.score += 1 #contador de pontos
        quiz_frame.correct_count += 1 #contador de certas
        lbl_score.config(text=f"Pontuação: {quiz_frame.score}")
    else:
        correct_option = quiz_frame.current_question[quiz_frame.correct_answer + 2]
        messagebox.showinfo("Errado!", f"A resposta correta era: {correct_option}")
        quiz_frame.incorrect_count += 1 #contador de erradas
    
    quiz_frame.questions_asked += 1 #contador de perguntas feitas
    mostrar_pergunta()

def exportar_resultados(user_id):
    conn = sqlite3.connect('quiz-questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT score, date FROM scores WHERE user_id = ?', (user_id,))
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        messagebox.showinfo("Exportação", "Não há resultados para exportar.")
        return

    #criar o ficheiro Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultados do Quiz"

    #adicionar campos
    ws.append(["Jogo", "Pontuação", "Data"])
    for i, (score, date) in enumerate(resultados, start=1):
        ws.append([i, score, date])

    #organizar os campos
    for cell in ws[1]:
        cell.alignment = Alignment(horizontal="center", vertical="center")

    #guardar no ficheiro
    nome_ficheiro = f"resultados_quiz_{user_id}.xlsx"
    wb.save(nome_ficheiro)
    messagebox.showinfo("Exportação", f"Resultados exportados para '{nome_ficheiro}'.")


def finalizar_quiz():
    registar_pontuacao(quiz_frame.user_id, quiz_frame.score)
    messagebox.showinfo("Fim do Quiz", f"Sua pontuação final é: {quiz_frame.score}\n" f"Respostas certas: {quiz_frame.correct_count}\n" f"Respostas erradas: {quiz_frame.incorrect_count}\n")

    mostrar_menu_principal(quiz_frame.user_id, entry_name.get())
    quiz_frame.pack_forget()



##INTERFACE

#criar a janela, titulo e dimensões
root = tk.Tk()
root.title("Quiz Cinquenta e Quatro Dezasete")
root.geometry("600x800")

#widget login
login_frame = tk.Frame(root)
login_frame.pack()

tk.Label(login_frame, text="Nome").pack()
entry_name = tk.Entry(login_frame)
entry_name.pack()

tk.Label(login_frame, text="Senha").pack()
entry_pw = tk.Entry(login_frame, show="*")
entry_pw.pack()

#widget botao
tk.Button(login_frame, text="Login", command=login).pack(pady=5)
tk.Button(login_frame, text="Registar", command=registar).pack(pady=5)

# Frame do menu principal
menu_frame = tk.Frame(root)
menu_frame.pack()
# Frame do Quiz
quiz_frame = tk.Frame(root)

#label do timer
lbl_timer = tk.Label(quiz_frame, text="", font=("Arial", 14), fg="red")
lbl_timer.pack(pady=10)

#label da pontuaçao
lbl_score = tk.Label(quiz_frame, text="Pontuação: 0", font=("Arial", 14), fg="blue")
lbl_score.pack(pady=5)


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