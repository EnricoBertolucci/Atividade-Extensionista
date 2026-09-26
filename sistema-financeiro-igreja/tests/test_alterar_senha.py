import pytest

from src.models import Usuario
from tests.conftest import SENHA_TESTE

NOVA_SENHA = "novaSenha456"


def _alterar(client, senha_atual, nova_senha, confirmacao):
    return client.post(
        "/alterar-senha",
        data={"senha_atual": senha_atual, "nova_senha": nova_senha, "confirmacao": confirmacao},
        follow_redirects=True,
    )


def _senha_confere(app, usuario_id, senha):
    with app.app_context():
        return Usuario.query.get(usuario_id).checar_senha(senha)


def test_alterar_senha_exige_login(client):
    resposta = client.get("/alterar-senha", follow_redirects=False)

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_alterar_senha_com_sucesso(client_logado, app, usuario):
    resposta = _alterar(client_logado, SENHA_TESTE, NOVA_SENHA, NOVA_SENHA)

    assert "Senha alterada com sucesso" in resposta.get_data(as_text=True)
    assert _senha_confere(app, usuario, NOVA_SENHA)
    assert not _senha_confere(app, usuario, SENHA_TESTE)


def test_login_funciona_com_a_nova_senha(client_logado, usuario):
    _alterar(client_logado, SENHA_TESTE, NOVA_SENHA, NOVA_SENHA)
    client_logado.get("/logout")

    resposta = client_logado.post(
        "/login",
        data={"email": "tesoureiro@teste.com", "senha": NOVA_SENHA},
        follow_redirects=False,
    )

    assert resposta.status_code == 302
    assert "/login" not in resposta.headers["Location"]


@pytest.mark.parametrize(
    "senha_atual, nova_senha, confirmacao, mensagem",
    [
        ("senha-errada", NOVA_SENHA, NOVA_SENHA, "senha atual está incorreta"),
        (SENHA_TESTE, "abc", "abc", "pelo menos 6 caracteres"),
        (SENHA_TESTE, NOVA_SENHA, "outraSenha789", "confirmação não confere"),
        (SENHA_TESTE, SENHA_TESTE, SENHA_TESTE, "diferente da senha atual"),
    ],
)
def test_alterar_senha_invalida_nao_altera(client_logado, app, usuario, senha_atual, nova_senha, confirmacao, mensagem):
    resposta = _alterar(client_logado, senha_atual, nova_senha, confirmacao)

    assert mensagem in resposta.get_data(as_text=True)
    assert _senha_confere(app, usuario, SENHA_TESTE)
