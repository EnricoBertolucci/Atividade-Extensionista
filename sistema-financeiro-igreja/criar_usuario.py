import getpass

from app import app
from src.models import Usuario, db


def main():
    with app.app_context():
        nome = input("Nome do responsável: ").strip()
        email = input("E-mail de login: ").strip().lower()
        senha = getpass.getpass("Senha: ")

        if Usuario.query.filter_by(email=email).first():
            print(f"Já existe um usuário com o e-mail '{email}'.")
            return

        usuario = Usuario(nome=nome, email=email)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        print(f"Usuário '{nome}' criado com sucesso!")


if __name__ == "__main__":
    main()
