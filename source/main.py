from client import Client
from servidor import Server
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Supondo que Server e Client já estejam definidos/importados

def criar_janela_inicial(cli):
    """Cria a interface de login."""
    janela = tk.Tk()
    janela.title("Sistema de Arquivos Seguro")
    janela.geometry("320x220")
    janela.resizable(False, False)

    tk.Label(janela, text="Login de Acesso", font=("Arial", 12, "bold")).pack(pady=10)

    # Campo de usuário
    frame_user = tk.Frame(janela)
    tk.Label(frame_user, text="Usuário:").pack(side=tk.LEFT)
    entry_username = tk.Entry(frame_user, width=25)
    entry_username.pack(side=tk.RIGHT)
    frame_user.pack(pady=5)

    # Campo de senha
    frame_pass = tk.Frame(janela)
    tk.Label(frame_pass, text="Senha:  ").pack(side=tk.LEFT)
    entry_password = tk.Entry(frame_pass, show="*", width=25)
    entry_password.pack(side=tk.RIGHT)
    frame_pass.pack(pady=5)

    # Função de login
    def tentar_login():
        username = entry_username.get().strip()
        password = entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        try:
            result_password, result_totp = cli.login(username, password)
            if result_password and result_totp:
                messagebox.showinfo("Sucesso", "Login bem-sucedido!")
                janela.destroy()
            else:
                erros = []
                if not result_password:
                    erros.append("Senha incorreta")
                if not result_totp:
                    erros.append("Código TOTP incorreto")
                messagebox.showerror("Falha no Login", "\n".join(erros))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro durante o login:\n{e}")
    
    # Função para registrar novo usuário
    def registrar_usuario():
        username = entry_username.get().strip()
        password = entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos para registrar.")
            return

        try:
            result = cli.register(username, password)
            if result["ok"]:
                messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")
            else:
                messagebox.showerror("Erro", result.get("error", "Erro desconhecido"))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro durante o registro:\n{e}")

    # Botão de login
    tk.Button(
        janela,
        text="Entrar",
        command=tentar_login,
        width=12,
        bg="#0078D7",
        fg="white"
    ).pack(padx=5)

    # Botão de registro
    tk.Button(
        janela,
        text="Registrar",
        command=registrar_usuario,
        width=12,
        bg="#0078D7",
        fg="white"
    ).pack(padx=5)

    janela.mainloop()

def criar_janela_principal(cli):
    janela = tk.Tk()
    janela.title("Gerenciador de Arquivos Seguro")
    janela.geometry("360x200")
    janela.resizable(False, False)

    tk.Label(
        janela,
        text="Bem-vindo ao Sistema de Arquivos",
        font=("Arial", 12, "bold")
    ).pack(pady=15)

    def subir_arquivo():
        caminho = filedialog.askopenfilename(title="Selecione um arquivo para enviar")
        if not caminho:
            return
        try:
            cli.enviar_arquivo(caminho)
            messagebox.showinfo("Sucesso", "Arquivo enviado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar o arquivo:\n{e}")

    def resgatar_arquivo():
        arquivos = cli.listar_arquivos()
        if not arquivos:
            messagebox.showinfo("Info", "Nenhum arquivo disponível no servidor.")
            return

        # Criar nova janela para listar arquivos
        janela_lista = tk.Toplevel(janela)
        janela_lista.title("Arquivos no Servidor")
        janela_lista.geometry("300x250")

        tk.Label(janela_lista, text="Selecione um arquivo para baixar:").pack(pady=5)

        listbox = tk.Listbox(janela_lista, width=40, height=10)
        for arq in arquivos:
            listbox.insert(tk.END, arq)
        listbox.pack(pady=5)

        def baixar():
            selecao = listbox.curselection()
            if not selecao:
                messagebox.showwarning("Aviso", "Selecione um arquivo.")
                return
            nome = listbox.get(selecao[0])
            destino = filedialog.asksaveasfilename(initialfile=nome, title="Salvar como")
            if not destino:
                return
            sucesso = cli.baixar_arquivo(nome, destino)
            if sucesso:
                messagebox.showinfo("Sucesso", "Arquivo baixado com sucesso!")
            else:
                messagebox.showerror("Erro", "Falha ao baixar o arquivo.")

        tk.Button(janela_lista, text="Baixar", command=baixar, bg="#0078D7", fg="white").pack(pady=10)

    # Frame com botões lado a lado
    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=30)

    tk.Button(frame_botoes, text="Subir Arquivo", command=subir_arquivo, width=15, bg="#0078D7", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Button(frame_botoes, text="Resgatar Arquivo", command=resgatar_arquivo, width=15, bg="#0078D7", fg="white").pack(side=tk.LEFT, padx=10)

    janela.mainloop()

if __name__ == "__main__":
    srv = Server()
    cli = Client(srv)

   # cli.register("aa", "123")
    cli.login("aa", "123")
    print(cli.username)
    cli.enviar_arquivo("source/texto.txt")

    #criar_janela_inicial(cli)
    # if cli.logado:
    #     criar_janela_principal(cli)

