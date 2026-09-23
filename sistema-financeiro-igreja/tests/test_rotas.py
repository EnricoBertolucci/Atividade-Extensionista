from src.models import Categoria, Contribuinte, Lancamento


def test_index_redireciona_para_login_quando_nao_autenticado(client):
    resposta = client.get("/", follow_redirects=False)

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_lista_contribuintes_exige_login(client):
    resposta = client.get("/contribuintes/", follow_redirects=False)

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_login_com_credenciais_validas(client_logado):
    resposta = client_logado.get("/")

    assert resposta.status_code == 200


def test_login_com_credenciais_invalidas(client, usuario):
    resposta = client.post(
        "/login",
        data={"email": "tesoureiro@teste.com", "senha": "senha-errada"},
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "inválidos" in resposta.get_data(as_text=True)


def test_crud_contribuinte(client_logado, app):
    resposta_criar = client_logado.post(
        "/contribuintes/novo",
        data={"nome": "Maria Teste", "bairro": "Centro", "data_primeira_contribuicao": "10/01/2020"},
        follow_redirects=True,
    )
    assert resposta_criar.status_code == 200
    assert "Maria Teste" in resposta_criar.get_data(as_text=True)

    with app.app_context():
        contribuinte_id = Contribuinte.query.filter_by(nome="Maria Teste").first().id

    resposta_editar = client_logado.post(
        f"/contribuintes/{contribuinte_id}/editar",
        data={"nome": "Maria Editada", "bairro": "Centro", "data_primeira_contribuicao": "10/01/2020"},
        follow_redirects=True,
    )
    assert resposta_editar.status_code == 200
    assert "Maria Editada" in resposta_editar.get_data(as_text=True)

    resposta_remover = client_logado.post(f"/contribuintes/{contribuinte_id}/remover", follow_redirects=True)
    assert resposta_remover.status_code == 200

    with app.app_context():
        assert Contribuinte.query.get(contribuinte_id) is None


def test_crud_lancamento(client_logado, app):
    with app.app_context():
        categoria = Categoria.query.filter_by(tipo="entrada").first()
        categoria_id = categoria.id

    resposta_criar = client_logado.post(
        "/lancamentos/novo",
        data={
            "categoria_id": str(categoria_id),
            "valor": "150,00",
            "data": "15/03/2026",
            "descricao": "Contribuição de teste",
            "contribuinte_id": "",
        },
        follow_redirects=True,
    )
    assert resposta_criar.status_code == 200
    assert "registrado com sucesso" in resposta_criar.get_data(as_text=True)

    with app.app_context():
        lancamento = Lancamento.query.filter_by(descricao="Contribuição de teste").first()
        lancamento_id = lancamento.id

    resposta_remover = client_logado.post(f"/lancamentos/{lancamento_id}/remover", follow_redirects=True)
    assert resposta_remover.status_code == 200
    assert "removido com sucesso" in resposta_remover.get_data(as_text=True)
