from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from conexao import cursor, conexao
from emprestimo import Emprestimo
from funcionario import buscar_funcionario, calcular_pagamento_total
from cores  import  CORES, FONT_TITULO, FONT_NORMAL



def apenas_numeros(valor):
    return valor.isdigit() or valor == ""

def apenas_letras(valor):
    return valor.replace(" ", "").isalpha() or valor == ""

def validar_data(valor):
    for c in valor:
        if not (c.isdigit() or c == "-"):
            return False
    return True

usuario_logado = None

def estilizar_janela(j):
    j.configure(bg=CORES["bg_janela"])

    for widget in j.winfo_children():

        if isinstance(widget, tk.Label):
            widget.configure(
                bg=CORES["bg_janela"],
                fg=CORES["texto"],
                font=FONT_NORMAL
            )

        elif isinstance(widget, tk.Button):
            widget.configure(
                bg=CORES["primaria"],
                fg=CORES["texto_claro"]
            )

        elif isinstance(widget, ttk.Combobox):
            continue   # ttk usa Style

        elif isinstance(widget, tk.Entry):
            widget.configure(
                bg="white",
                fg=CORES["texto"]
            )

        elif isinstance(widget, tk.Frame):
            widget.configure(bg=CORES["bg_janela"])


# ================= USUARIO =================
def tela_usuario():

    #Tela de cadstro do usuario
    janela = tk.Toplevel()
    janela.title("Cadastro de Usuário")
    janela.geometry("520x520")


    tk.Label(janela, text="Nome").pack(pady=5)
    vcmd_letras =(janela.register(apenas_letras), '%P')
    nome= tk.Entry(janela, validate='key', validatecommand=vcmd_letras)
    nome.pack()

    tk.Label(janela, text="Data de Nascimento (yyyy-mm-dd)").pack(pady=5)
    vcmd_data =(janela.register(validar_data), '%P')
    data_nascimento = tk.Entry(janela, validate='key', validatecommand=vcmd_data)
    data_nascimento.pack()

    tk.Label(janela, text="Email").pack(pady=5)
    email = tk.Entry(janela)
    email.pack()

    tk.Label(janela, text="Telefone").pack(pady=5)
    vcmd_numeros =(janela.register(apenas_numeros), '%P')
    telefone = tk.Entry(janela, validate='key', validatecommand=vcmd_numeros)
    telefone.pack()

    estilizar_janela(janela)

   #Salvando usuario na banco de dados
    def salvar():
        global usuario_logado

        nome_valor = nome.get().strip()
        data_nascimento_valor = data_nascimento.get().strip()
        email_valor = email.get().strip()
        telefone_valor = telefone.get().strip()

        if not nome_valor or not data_nascimento_valor or not email_valor or not telefone_valor:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
     
        if not telefone_valor.isdigit():
            messagebox.showerror("Erro", "Telefone deve conter apenas números!")
            telefone.delete(0, tk.END)
            telefone.focus()
            return
        
        try: 
            datetime.strptime(data_nascimento.get(), "%Y-%m-%d")

            cursor.execute(
                "INSERT INTO Usuario (nome, data_nascimento, email, telefone) VALUES (?, ?, ?, ?)",
                (nome.get(), data_nascimento.get(), email.get(), telefone.get())
            )
            conexao.commit()

            cursor.execute("SELECT SCOPE_IDENTITY()")
            id_usuario = cursor.fetchone()[0]

            usuario_logado = (id_usuario, nome.get())
            
            messagebox.showinfo("Sucesso", f"Usuário cadastrado! ID: {id_usuario}")

            janela.destroy()
            abrir_area_usuario()

        except ValueError:
            messagebox.showerror("Erro", "Data deve estar no formato yyyy-mm-dd")
            data_nascimento.delete(0, tk.END)
            data_nascimento.focus()

    frame = tk.Frame(janela)
    frame.pack(pady=10)

    tk.Button(frame, text="Salvar", command=salvar).pack(side="left", padx=5)
    tk.Button(frame, text="Voltar", command=lambda: abrir_atendimento(janela)).pack(side="left", padx=5)
    
    estilizar_janela(janela)


#Login do usuario ja exixtente
def tela_login(janela_anterior):
    

    janela = tk.Toplevel()
    janela.title("Login")
    janela.geometry("520x520")

    tk.Label(janela, text="Digite seu ID").pack(pady=10)
    entrada_id = tk.Entry(janela)
    entrada_id.pack()

    def entrar():
        global usuario_logado

        try:
            id_user = int(entrada_id.get())

            cursor.execute("SELECT id, nome FROM Usuario WHERE id = ?", (id_user,))
            user = cursor.fetchone()

            if user:
                usuario_logado = user
                janela_anterior.destroy()
                messagebox.showinfo("Sucesso", f"Bem-vindo {user[1]}!")
                janela.destroy()
                abrir_area_usuario()
            else:
                messagebox.showerror("Erro", "Usuário não encontrado")

        except:
            messagebox.showerror("Erro", "Digite um ID válido")

    tk.Button(janela, text="Entrar", command=entrar).pack(pady=10)

    estilizar_janela(janela)

#Area do usuario (menu do usuario)
def abrir_area_usuario():
    global usuario_logado

    j = tk.Toplevel()
    j.title("Área do Usuário")
    j.geometry("400x300")

    tk.Label(j, text=f"Usuário: {usuario_logado[1]} (ID: {usuario_logado[0]})",
             font=("Arial", 12)).pack(pady=10)

    tk.Button(j, text="Ver Livros", width=25,
              command=ver_livros_usuario).pack(pady=5)

    tk.Button(j, text="Meus Empréstimos", width=25,
              command=ver_meus_emprestimos).pack(pady=5)
    

    tk.Button(j, text="Voltar", command=lambda: [j.destroy(), abrir_atendimento(j)]).pack(pady=10)
    estilizar_janela(j)
    

def print_usuarios():
    cursor.execute("SELECT id, nome FROM Usuario")
    usuarios = cursor.fetchall()

    print("\n=== USUÁRIOS CADASTRADOS ===")
    for u in usuarios:
        print(f"ID: {u[0]} | Nome: {u[1]}")

#Listar livros disponivel para o usuario 
def ver_livros_usuario():
    janela = tk.Toplevel()
    janela.title("Livros Disponíveis")
    janela.geometry("400x400")

    listbox = tk.Listbox(janela, width=100)
    listbox.pack(pady=10)

    ids = []

    cursor.execute("SELECT * FROM Livro")
    for l in cursor.fetchall():
        status = "Disponível" if l[6] else "Indisponível"
        listbox.insert(tk.END, f"{l[0]} - {l[1]} | {l[2]} | {status}")
        ids.append(l[0])

    def selecionar_livro():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um livro!")
            return

        i = sel[0]
        id_livro = ids[i]

        # abre empréstimo com livro já preenchido
        tela_emprestimo(id_livro)

    tk.Button(janela, text="Selecionar Livro", command=selecionar_livro).pack(pady=10)
    tk.Button(janela, text="Voltar", command=janela.destroy).pack()

    estilizar_janela(janela)
     

#  EMPRESTIMO e DEVOLUCAO (usuario)
def tela_emprestimo(id_livro_pre=None):
    global usuario_logado

    if not usuario_logado:
        messagebox.showerror("Erro", "Faça login primeiro!")
        return

    janela = tk.Toplevel()
    janela.title("Empréstimo")
    janela.geometry("520x520")

    tk.Label(janela, text="ID Usuário").pack()
    id_usuario = tk.Entry(janela)
    id_usuario.pack()
    id_usuario.insert(0, str(usuario_logado[0]))
    id_usuario.config(state="disabled")

    tk.Label(janela, text="ID Livro").pack()
    id_livro = tk.Entry(janela)
    id_livro.pack()

    if id_livro_pre:
        id_livro.insert(0, str(id_livro_pre))

    def emprestar():
        try:
            if not id_livro.get():
                messagebox.showwarning("Aviso", "Digite o ID do livro!")
                return
            
            cursor.execute("EXEC sp_emprestar_livro ?, ?", (usuario_logado[0], int(id_livro.get())))
            conexao.commit()

            messagebox.showinfo("Sucesso", "Livro emprestado!")
            id_livro.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def devolver():
        try:
            if not id_livro.get():
                messagebox.showwarning("Aviso", "Digite o ID do livro!")
                return
            
            cursor.execute("EXEC sp_devolver_livro ?, ?", (usuario_logado[0], int(id_livro.get())))
            conexao.commit()

            messagebox.showinfo("Sucesso", "Livro devolvido!")
            id_livro.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    freme = tk.Frame(janela)
    freme.pack(pady=10)


    tk.Button(freme, text="Emprestar", command=emprestar).pack(side="left", padx=5)
    tk.Button(freme, text="Devolver", command=devolver).pack(side="left", padx=5)
    
    tk.Button(freme, text="Voltar", command=janela.destroy).pack(side="left", padx=5)

    estilizar_janela(janela)

#Ver emprestimo do usuario logado
def ver_meus_emprestimos():
    global usuario_logado

    janela = tk.Toplevel()
    janela.title("Meus Empréstimos")
    janela.geometry("600x300")

    listbox = tk.Listbox(janela, width=100)
    listbox.pack(pady=10)

    cursor.execute("""
        SELECT COUNT(*)
        FROM Emprestimo
        WHERE id_usuario = ?
    """, (usuario_logado[0],))

    total = cursor.fetchone()[0]

    tk.Label(
        janela,
        text=f"Total de Empréstimos: {total}",
        font=("Arial", 12)
    ).pack(pady=5)

    cursor.execute("""
        SELECT titulo,
               data_prevista,
               data_devolvida,
               status
        FROM vw_meus_emprestimos
        WHERE id_usuario = ?
    """, (usuario_logado[0],))

    dados = cursor.fetchall()

    for titulo, prevista, devolvida, status in dados:

        prevista = prevista.strftime('%d/%m/%Y') if prevista else "-"
        devolvida = devolvida.strftime('%d/%m/%Y') if devolvida else "-"

        listbox.insert(
            tk.END,
            f"{titulo} | {status} | Prazo: {prevista} | Devolvido em: {devolvida}"
        )

    frame = tk.Frame(janela)
    frame.pack(pady=10)

    tk.Button(frame, text="Voltar", command=janela.destroy).pack(side="left", padx=5)
    tk.Button(frame, text="Devolver Livro",
              command=lambda: tela_emprestimo()).pack(side="left", padx=5)

    estilizar_janela(janela)

# ================= Administrador  =================

# listar  usuario 
def ver_usuarios():
    janela = tk.Toplevel()
    janela.title("Usuários")
    janela.geometry("520x520")

    tk.Label(janela, text="Lista de Usuários").pack(pady=5)

    listbox = tk.Listbox(janela, width=100)
    listbox.pack(pady=10)

    ids = []

    cursor.execute("SELECT id, nome, data_nascimento, email, telefone FROM Usuario")
    for u in cursor.fetchall():
        texto = f"ID: {u[0]} | Nome: {u[1]} | Nascimento: {u[2]} | Email: {u[3]} | Telefone: {u[4]}"
        listbox.insert(tk.END, texto)
        ids.append(u[0])

    def deletar():
        sel = listbox.curselection()
        if not sel:
            return

        i = sel[0]
        id_usuario = ids[i]

        if not messagebox.askyesno("Confirmação", "Deseja deletar?"):
            return

        try:
            cursor.execute("DELETE FROM Usuario WHERE id = ?", (id_usuario,))
            conexao.commit()
            listbox.delete(i)
            ids.pop(i)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

        janela.destroy()
        ver_usuarios()

    frame = tk.Frame(janela)
    frame.pack()

    tk.Button(frame, text="Deletar", command=deletar).pack(side="left", padx=5)
    tk.Button(frame, text="Voltar", command=janela.destroy).pack(side="left", padx=5)

    estilizar_janela(janela)

#Cadastro de livros 
def tela_livro():
    janela = tk.Toplevel()
    janela.title("Cadastro de Livro")
    janela.geometry("520x520")

    tk.Label(janela, text="Título").pack()
    titulo = tk.Entry(janela)
    titulo.pack()

    tk.Label(janela, text="Autor").pack()
    vcmd_letras =(janela.register(apenas_letras), '%P')
    autor = tk.Entry(janela, validate='key', validatecommand=vcmd_letras)
    autor.pack()

    tk.Label(janela, text = "Ano de Publicação").pack()
    vcmd_numeros =(janela.register(apenas_numeros), '%P')
    ano = tk.Entry(janela, validate='key', validatecommand=vcmd_numeros)
    ano.pack()

    tk.Label(janela, text="Gênero").pack()
    genero = tk.Entry(janela)
    genero.pack()

    tk.Label(janela, text="Editora").pack()
    editora = tk.Entry(janela)
    editora.pack()

    def salvar():

        titulo_valor = titulo.get().strip()
        autor_valor = autor.get().strip()
        ano_valor = ano.get().strip()
        genero_valor = genero.get().strip()
        editora_valor = editora.get().strip()

        if not titulo_valor or not autor_valor or not ano_valor or not genero_valor or not editora_valor:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        
        if not ano_valor.isdigit():
            messagebox.showerror("Erro", "Ano deve ser um número!")
            ano.delete(0, tk.END)
            ano.focus()
            return
        
        cursor.execute(
            "INSERT INTO Livro (titulo, autor, ano, genero, editora, disponivel) VALUES (?, ?, ?, ?, ?, 1)",
            (titulo.get(), autor.get(), ano.get(), genero.get(), editora.get())
        )
        conexao.commit()

        messagebox.showinfo("Sucesso", "Livro cadastrado!")
  
        janela.destroy()
        ver_livros()
        
        

       
    frame = tk.Frame(janela)
    frame.pack(pady=10)

    tk.Button(frame, text="Salvar", command=salvar).pack(side="left", padx=5)

    tk.Button(frame, text="Voltar", command=janela.destroy).pack(side="left", padx=5)
   
    estilizar_janela(janela)


#Listar e  deletar livro 
def ver_livros():
    janela = tk.Toplevel()
    janela.title("Livros")
    janela.geometry("520x520")

    listbox = tk.Listbox(janela, width=100)
    listbox.pack(pady=10)

    ids = []

    cursor.execute("SELECT * FROM Livro")
    for l in cursor.fetchall():
        status = "Disponível" if l[6] else "Indisponível"
        listbox.insert(tk.END, f"{l[0]} - {l[1]} | {l[2]} | {status}")
        ids.append(l[0])

    def deletar():
        sel = listbox.curselection()
        if not sel:
            return

        i = sel[0]
        id_livro = ids[i]

        if not messagebox.askyesno("Confirmação", "Deseja deletar?"):
            return

        try:
            cursor.execute("DELETE FROM Livro WHERE id = ?", (id_livro,))
            conexao.commit()
            listbox.delete(i)
            ids.pop(i)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        
        janela.destroy()
        abrir_painel_funcionario()

    frame = tk.Frame(janela)
    frame.pack()

    tk.Button(frame, text="Deletar", command=deletar).pack(side="left", padx=5)
    tk.Button(frame, text="Voltar", command=janela.destroy).pack(side="left", padx=5)

    estilizar_janela(janela)

#Cadstro de funcionario 
def tela_funcionario():
    janela = tk.Toplevel()
    janela.title("Funcionário")
    janela.geometry("520x520")

    tk.Label(janela, text="Nome").pack()
    vcmd_letras =(janela.register(apenas_letras), '%P')
    nome = tk.Entry(janela, validate='key', validatecommand=vcmd_letras)
    nome.pack()

    tk.Label(janela, text="Salário").pack()
    vcmd_numeros =(janela.register(apenas_numeros), '%P')
    salario = tk.Entry(janela, validate='key', validatecommand=vcmd_numeros)
    salario.pack()

    tk.Label(janela, text="Tipo").pack()
    tipo = ttk.Combobox(janela, values=["Bibliotecario", "Gerente"])
    tipo.pack()

    def salvar():

        nome_valor = nome.get().strip()
        salario_valor = salario.get().strip()
        tipo_valor = tipo.get().strip()
        
        if not nome_valor or not salario_valor or not tipo_valor:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        
        try:
            salario_valor = float(salario_valor)
        except ValueError:
            messagebox.showerror("Erro", "Salário deve ser um número!")
            salario.delete(0, tk.END)
            salario.focus()
            return

        cursor.execute(
            "INSERT INTO Funcionario (nome, salario, tipo) VALUES (?, ?, ?)",
            (nome.get(), salario.get(), tipo.get())
        )
        conexao.commit()
        messagebox.showinfo("Sucesso", "Funcionário cadastrado!")
        
        janela.destroy()
        tela_folha_pagamento()

    frame = tk.Frame(janela)
    frame.pack(pady=10)
    tk.Button(frame, text="Salvar", command=salvar).pack(side="left", padx=5)
    tk.Button(frame, text="Voltar", command=janela.destroy).pack(side="left", padx=5)
 
    estilizar_janela(janela)


#tela de pagamento dos funcionarios 
def tela_folha_pagamento():
    janela = tk.Toplevel()
    janela.title("Folha de Pagamento")
    janela.geometry("600x400")

    lista = tk.Listbox(janela, width=100)
    lista.pack(pady=20)

    total_geral = 0

    cursor.execute("SELECT nome, salario, bonus, total FROM Funcionario")
    funcionarios = cursor.fetchall()

    for nome, salario, bonus, total in funcionarios:

        total_geral += total

        lista.insert(
            tk.END,
            f"{nome} | Salário: R$ {salario} | Bônus: R$ {bonus} | Total: R$ {total}"
        )

    tk.Label(janela, text=f"TOTAL GERAL: R$ {total_geral}", font=("CORES['font_normal']")).pack(pady=10)

    tk.Button(janela, text="Voltar", command=janela.destroy).pack()
    
    estilizar_janela(janela)

#Painel administrativo 
def abrir_painel_funcionario():
    j = tk.Toplevel()
    j.title("Acesso Administrativo")
    j.geometry("520x520")


    tk.Button(j, text="Cadastrar Funcionário", width=25, command=tela_funcionario).pack(pady=5)

    tk.Button(j, text="Cadastrar Livro", width=25, command=tela_livro).pack(pady=5)

    tk.Button(j, text="Ver Livros", width=25, command=ver_livros).pack(pady=5)

    tk.Button(j, text="Ver Usuários", width=25, command=ver_usuarios).pack(pady=5)

    tk.Button(j, text="Folha de Pagamento", width=25, command=tela_folha_pagamento).pack(pady=5)

    tk.Button(j, text="Voltar", command=lambda:[j.destroy(), escolher_interface()]).pack(pady=5)

    estilizar_janela(j)

# ================= INTERFACES =================

def escolher_interface():
    janela_escolha = tk.Toplevel()
    janela_escolha.title("Escolha de Acesso")
    janela_escolha.geometry("520x520")


    tk.Label(janela_escolha, text="Escolha o acesso").pack(pady=20)

    tk.Button(janela_escolha, text="Painel Administrativo", width=25, 
              command=lambda: [janela_escolha.destroy(), abrir_painel_funcionario()]).pack(pady=5)

    
    tk.Button(janela_escolha, text="Atendimento", width=25, 
              command=lambda: [janela_escolha.destroy(), abrir_atendimento(janela_escolha)]).pack(pady=5)
    

    estilizar_janela(janela_escolha)

def abrir_atendimento(tela):
    tela.destroy()

    j = tk.Toplevel()
    j.title("Atendimento")
    j.geometry("520x520")

    tk.Label(j, text="Bem-vindo").pack(pady=20)

    tk.Button(j, text="Já sou cadastrado", width=25,
              command=lambda: tela_login(j)).pack(pady=5)

    tk.Button(j, text="Cadastrar novo usuário", width=25,
              command=lambda: [j.destroy(), tela_usuario()]).pack(pady=5)
    
    tk.Button(j, text="Voltar", width=25, command=lambda: [j.destroy(), escolher_interface()]).pack(pady=5)
    
    estilizar_janela(j)

# ================= PRINCIPAL =================
janela = tk.Tk()
janela.title("Biblioteca")
janela.geometry("520x520")
janela.configure(bg=CORES["bg_principal"])

canvas = tk.Canvas(
    janela,
    width=220,
    height=180,
    bg=CORES["bg_principal"],
    highlightthickness=0
)
canvas.pack(pady=20)

# livros
canvas.create_rectangle(30,40,70,150, fill="#DC3545", outline="")
canvas.create_rectangle(75,30,115,150, fill="#28A745", outline="")
canvas.create_rectangle(120,50,160,150, fill="#FFC107", outline="")
canvas.create_rectangle(165,20,205,150, fill="#2D6CDF", outline="")

# prateleira
canvas.create_rectangle(20,150,210,160, fill="#6C757D", outline="")

# título
tk.Label(janela,text="Sistema Biblioteca",font=FONT_TITULO,bg=CORES["bg_principal"],fg=CORES["texto"]).pack(pady=8)

# subtítulo
tk.Label(janela,text="Gerencie livros, usuários e empréstimos",font=FONT_NORMAL,bg=CORES["bg_principal"],fg=CORES["secundaria"]).pack()

# botão entrar
tk.Button(janela,text="Entrar",width=20,font=FONT_NORMAL,bg=CORES["primaria"],fg=CORES["texto_claro"],
activebackground=CORES["primaria_hover"],relief="flat",command=lambda: [janela.withdraw(), escolher_interface()]).pack(pady=30)

print_usuarios()

janela.mainloop()

