import pytest

from app import create_app
from src.models import Usuario, db

SENHA_TESTE = "senha123"


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )
    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuario(app):
    with app.app_context():
        usuario = Usuario(nome="Tesoureiro Teste", email="tesoureiro@teste.com")
        usuario.set_senha(SENHA_TESTE)
        db.session.add(usuario)
        db.session.commit()
        return usuario.id


@pytest.fixture
def client_logado(client, usuario):
    client.post(
        "/login",
        data={"email": "tesoureiro@teste.com", "senha": SENHA_TESTE},
        follow_redirects=True,
    )
    return client
