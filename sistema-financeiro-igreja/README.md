# Sistema Financeiro da Igreja

Sistema web de controle financeiro para uma igreja local, desenvolvido como projeto de extensão acadêmica.

## Objetivos
1. Controle financeiro digital simples e prático para a gestão dos recursos da igreja.
2. Promover inclusão digital em uma instituição com pouca familiaridade com tecnologia.
3. Capacitar os responsáveis pela tesouraria para uso autônomo do sistema.

## Tecnologias
- Python 3 + Flask
- Flask-SQLAlchemy + SQLite
- Flask-Login (autenticação)
- Jinja2 + Bootstrap 5 (via CDN)

## Como rodar localmente

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Acesse http://localhost:5000

## Como rodar os testes

```powershell
pip install -r requirements.txt
pytest
```

Os testes usam um banco SQLite em memória, isolado do banco de produção (`database/app.db`).

## Estrutura do projeto

```
sistema-financeiro-igreja/
├── app.py
├── requirements.txt
├── src/
│   ├── models/
│   ├── routes/
│   ├── templates/
│   └── static/
├── database/
└── tests/
```

## Deploy (PythonAnywhere — gratuito)

Hospedagem escolhida: **[PythonAnywhere](https://www.pythonanywhere.com)**, conta free. Motivo: é a única opção gratuita testada que mantém o arquivo do banco SQLite (`database/app.db`) realmente persistente — outras opções (ex.: Render free) apagam o disco a cada "sono"/reinício do serviço, o que arriscaria perder os dados financeiros da igreja. O PythonAnywhere free também não exige nenhum cartão de crédito e já inclui HTTPS no domínio `seu-usuario.pythonanywhere.com`.

> Importante: quem faz o deploy é o mantenedor/desenvolvedor do sistema. O tesoureiro da igreja **nunca precisa mexer nisso** — só acessa a URL final pelo navegador, como qualquer site.

### Passo a passo (primeira vez)

1. Criar uma conta gratuita em [pythonanywhere.com](https://www.pythonanywhere.com/registration/register/beginner/).
2. Abrir um **Bash console** (aba "Consoles" → "Bash") e clonar o repositório:
   ```bash
   git clone https://github.com/<seu-usuario>/<seu-repo>.git sistema-financeiro-igreja
   cd sistema-financeiro-igreja
   ```
3. Criar o virtualenv e instalar as dependências (a conta free já vem com `mkvirtualenv` configurado):
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 venv-igreja
   pip install -r requirements.txt
   ```
4. Ir na aba **Web** → **Add a new web app** → domínio padrão gratuito → **Manual configuration** → escolher a mesma versão de Python do passo 3.
5. Na seção **Code** da aba Web, configurar:
   - **Source code**: `/home/<seu-usuario>/sistema-financeiro-igreja`
   - **Working directory**: `/home/<seu-usuario>/sistema-financeiro-igreja`
   - **Virtualenv**: `/home/<seu-usuario>/.virtualenvs/venv-igreja`
6. Clicar no link do **WSGI configuration file** (fica fora do repositório, em `/var/www/...`) e substituir o conteúdo por:
   ```python
   import sys
   import os

   path = '/home/<seu-usuario>/sistema-financeiro-igreja'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['SECRET_KEY'] = 'troque-por-uma-chave-aleatoria-longa'

   from app import app as application
   ```
   A `SECRET_KEY` fica só nesse arquivo (fora do Git), nunca no código-fonte versionado — gere uma string aleatória própria, por exemplo com `python -c "import secrets; print(secrets.token_hex(32))"`.
7. Voltar à aba Web e clicar no botão verde **Reload**.
8. Acessar `https://<seu-usuario>.pythonanywhere.com` e testar de ponta a ponta: login, cadastro de contribuinte, lançamento, relatório.
9. Rodar `python criar_usuario.py` dentro do Bash console (com o virtualenv ativado) para criar o primeiro usuário/tesoureiro, se ainda não existir.

### Atualizações futuras (depois da primeira vez)

Sempre que houver uma nova versão no GitHub:
```bash
cd ~/sistema-financeiro-igreja
git pull
workon venv-igreja
pip install -r requirements.txt   # só se requirements.txt mudou
```
Depois, voltar na aba **Web** e clicar em **Reload** novamente. Não há deploy automático (diferente de plataformas como Render) — é sempre esse "pull + reload" manual, mas simples o suficiente para não depender de conhecimento técnico avançado.

### Backup dos dados

Como o banco é um arquivo único (`database/app.db`), o backup é literalmente baixar esse arquivo pela aba **Files** do PythonAnywhere periodicamente. Task `10-capacitacao-usuarios.md` deve incluir esse passo no material de capacitação.

