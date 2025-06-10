import tkinter as tk
from tkinter import messagebox
import sqlite3


conn = sqlite3.connect('alunos.db3')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS alunos (
        matricula INTEGER PRIMARY KEY,
        nome TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS disciplinas (
        codigo TEXT PRIMARY KEY,
        nome TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS notas (
        matricula INTEGER,
        disciplina TEXT,
        Nota REAL,
        PRIMARY KEY (matricula, disciplina),
        FOREIGN KEY (matricula) REFERENCES alunos(matricula),
        FOREIGN KEY (disciplina) REFERENCES disciplinas(nome)
    )
''')

conn.commit()



class Aluno:
    def __init__(self, nome, matricula):
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Nome deve ser uma string não vazia.")
        if not isinstance(matricula, int) or matricula <= 0:
            raise ValueError("Matrícula deve ser um número inteiro positivo.")
        self.nome = nome
        self.matricula = matricula
        self.notas = {}

    def adicionar_nota(self, disciplina, nota):
        if not isinstance(disciplina, Disciplina):
            raise ValueError("Disciplina inválida.")
        if not isinstance(nota, (int, float)) or nota < 0 or nota > 10:
            raise ValueError("Nota deve ser um número entre 0 e 10.")
        self.notas[disciplina.nome] = nota

    def mostrar_notas(self):
        return self.notas


class Disciplina:
    def __init__(self, nome, codigo):
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Nome da disciplina deve ser uma string não vazia.")
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("Código da disciplina deve ser uma string não vazia.")
        self.nome = nome
        self.codigo = codigo


class Aplicacao:
    def __init__(self, root):
        self.root = root
        self.root.title("old school")
        self.root.configure(bg="#696773")

        self.frame = tk.Frame(root, bg="white", padx=60, pady=60)
        self.frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

        self.alunos = {}
        self.disciplinas = {}

        label_font = ("Arial", 12)
        entry_font = ("Arial", 12)
        button_font = ("Arial", 12)

        def label(text, row):
            return tk.Label(self.frame, text=text, bg="#F1F1F1", font=label_font).grid(row=row, column=0, sticky="e", pady=3)

        def entry(row):
            e = tk.Entry(self.frame, font=entry_font, width=22)
            e.grid(row=row, column=1, pady=3)
            return e

        label("Nome do Aluno:", 0)
        self.nome_aluno = entry(0)

        label("Matrícula:", 1)
        self.matricula_aluno = entry(1)

        tk.Button(self.frame, text="Adicionar Aluno", font=button_font, width=18, command=self.adicionar_aluno).grid(row=2, columnspan=2, pady=7)

        label("Nome da Disciplina:", 3)
        self.nome_disciplina = entry(3)

        label("Código da Disciplina:", 4)
        self.codigo_disciplina = entry(4)

        tk.Button(self.frame, text="Adicionar Disciplina", font=button_font, width=18, command=self.adicionar_disciplina).grid(row=5, columnspan=2, pady=7)

        label("Matrícula para Nota:", 6)
        self.matricula_nota = entry(6)

        label("Disciplina:", 7)
        self.disciplina_nota = entry(7)

        label("Nota:", 8)
        self.nota = entry(8)

        tk.Button(self.frame, text="Adicionar Nota", font=button_font, width=18, command=self.adicionar_nota).grid(row=9, columnspan=2, pady=7)

        label("Matrícula para Ver Notas:", 10)
        self.matricula_ver_notas = entry(10)

        tk.Button(self.frame, text="Mostrar Notas", font=button_font, width=18, command=self.mostrar_notas).grid(row=11, columnspan=2, pady=7)

    def adicionar_aluno(self):
        nome = self.nome_aluno.get()
        try:
            matricula = int(self.matricula_aluno.get())
            if matricula in self.alunos:
                messagebox.showerror("Erro", "Matrícula já cadastrada.")
                return
            self.alunos[matricula] = Aluno(nome, matricula)

            cursor.execute("INSERT INTO alunos (matricula, nome) VALUES (?, ?)", (matricula, nome))
            conn.commit()

            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            self.nome_aluno.delete(0, tk.END)
            self.matricula_aluno.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Matrícula deve ser um número inteiro positivo.")

    def adicionar_disciplina(self):
        nome = self.nome_disciplina.get()
        codigo = self.codigo_disciplina.get()
        if codigo in self.disciplinas:
            messagebox.showerror("Erro", "Código da disciplina já cadastrado.")
            return
        self.disciplinas[codigo] = Disciplina(nome, codigo)

        cursor.execute("INSERT INTO disciplinas (codigo, nome) VALUES (?, ?)", (codigo, nome))
        conn.commit()

        messagebox.showinfo("Sucesso", "Disciplina cadastrada com sucesso!")
        self.nome_disciplina.delete(0, tk.END)
        self.codigo_disciplina.delete(0, tk.END)

    def adicionar_nota(self):
        try:
            matricula = int(self.matricula_nota.get())
            disciplina_nome = self.disciplina_nota.get()
            nota = float(self.nota.get())

            if matricula not in self.alunos:
                messagebox.showerror("Erro", "Aluno não encontrado.")
                return

            disciplina = next((d for d in self.disciplinas.values() if d.nome == disciplina_nome), None)
            if not disciplina:
                messagebox.showerror("Erro", "Disciplina não encontrada.")
                return

            self.alunos[matricula].adicionar_nota(disciplina, nota)
            with sqlite3.connect('alunos.db3') as c:
                print("Teste")
                cc = c.cursor()
                cc.execute("INSERT OR REPLACE INTO notas (matricula, disciplina, nota) VALUES (?, ?, ?)",
                           (matricula, disciplina_nome, nota))
                c.commit()

            messagebox.showinfo("Sucesso", "Nota adicionada com sucesso!")
            self.matricula_nota.delete(0, tk.END)
            self.disciplina_nota.delete(0, tk.END)
            self.nota.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos. Certifique-se de inserir um número válido para matrícula e nota.")

    def mostrar_notas(self):
        try:
            matricula = int(self.matricula_ver_notas.get())
            if matricula not in self.alunos:
                messagebox.showerror("Erro", "Aluno não encontrado.")
                return

            cursor.execute("SELECT disciplina, nota FROM notas WHERE matricula = ?", (matricula,))
            resultados = cursor.fetchall()

            if not resultados:
                messagebox.showinfo("Notas", "Nenhuma nota cadastrada.")
            else:
                resultado = "\n".join(f"{disc}: {nota}" for disc, nota in resultados)
                messagebox.showinfo("Notas", resultado)
        except ValueError:
            messagebox.showerror("Erro", "Matrícula inválida.")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x700")
    root.configure(bg="#696773")
    

    titulo = tk.Label(root, text="Old School", font=("Helvetica", 32, "bold"), bg="#696773", fg="black")
    titulo.pack(pady=20)

    app = Aplicacao(root)

    def ao_sair():
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", ao_sair)
    root.mainloop()
