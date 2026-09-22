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

## Deploy
Em produção, o app roda via `gunicorn` (ver `Procfile`, adicionado na etapa de deploy). Hospedagem gratuita recomendada: [Render.com](https://render.com).

## Status
Projeto em desenvolvimento. Acompanhamento das etapas em `.temp/tarefas/` (fora deste repositório de código).
