from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from src.models import Usuario, db

auth_bp = Blueprint("auth", __name__)

TAMANHO_MINIMO_SENHA = 6


def _validar_troca_senha(usuario, form):
    """Valida o formulário de troca de senha e retorna a mensagem de erro (ou None)."""
    senha_atual = form.get("senha_atual", "")
    nova_senha = form.get("nova_senha", "")
    confirmacao = form.get("confirmacao", "")

    if not usuario.checar_senha(senha_atual):
        return "A senha atual está incorreta."
    if len(nova_senha) < TAMANHO_MINIMO_SENHA:
        return f"A nova senha deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres."
    if nova_senha != confirmacao:
        return "A confirmação não confere com a nova senha."
    if nova_senha == senha_atual:
        return "A nova senha deve ser diferente da senha atual."
    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.checar_senha(senha):
            login_user(usuario)
            proximo = request.args.get("next")
            return redirect(proximo or url_for("index"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("login.html")


@auth_bp.route("/alterar-senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    if request.method == "POST":
        erro = _validar_troca_senha(current_user, request.form)
        if erro:
            flash(erro, "danger")
            return render_template("alterar_senha.html", tamanho_minimo=TAMANHO_MINIMO_SENHA)

        current_user.set_senha(request.form["nova_senha"])
        db.session.commit()
        flash("Senha alterada com sucesso!", "success")
        return redirect(url_for("index"))

    return render_template("alterar_senha.html", tamanho_minimo=TAMANHO_MINIMO_SENHA)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
