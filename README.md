# Configuração de Ambiente para o Sistema de Arquivos Seguro

## 1️⃣ Pré-requisitos

Antes de executar o projeto, você precisa ter instalado:

- **Python 3.8 ou superior**  
  Baixe em [python.org](https://www.python.org/downloads/) e siga as instruções de instalação.

- **pip** (gerenciador de pacotes do Python)  
  Normalmente já vem junto com o Python.

- **Virtualenv (opcional, mas recomendado)**  
  Permite criar um ambiente isolado para o projeto:

```bash
pip install virtualenv
```

---

## 2️⃣ Criando o ambiente virtual (opcional, mas recomendado)

Abra o terminal e navegue até a pasta do projeto.

Crie o ambiente virtual:

```bash
# Windows
python -m venv venv

# macOS / Linux
python3 -m venv venv
```

Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```
Após ativar, o prompt do terminal mostrará o nome do ambiente entre parênteses, ex:
```bash
(venv) C:\github\trabalho-seguranca-redes
```

## 3️⃣ Instalando as dependências

Basta rodar:
```bash
pip install -r requirements.txt
```

## 4️⃣ Executando o projeto

Certifique-se de estar com o ambiente virtual ativado.

Execute o script principal:

```bash
python source/main.py
```

### Interface de Login

- Ao abrir o sistema, a interface de login será exibida.

- Para novos usuários: preencha os campos e clique em Registrar. O sistema armazenará o salt e o hash da senha no arquivo source/users.json.

- Login existente: ao entrar, a autenticação TOTP será realizada automaticamente.

### Funcionalidades após o login

- Enviar Arquivo: envie arquivos para o servidor simulado. Eles serão armazenados em source/arquivos_servidor/#nome_usuario. Recomenda-se enviar arquivos .txt para facilitar a visualização na interface ou utilizar os exemplos disponíveis em source/arquivos_para_envio.

- Baixar Arquivo: consulte a lista de arquivos disponíveis no servidor e faça o download. Os arquivos baixados são criptografados e armazenados em source/arquivos_locais.

- Arquivos Baixados: visualize e decifre os arquivos locais. Eles ficam armazenados em source/arquivos_locais_decifrados.
