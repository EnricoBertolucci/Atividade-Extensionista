from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from src.models import db
from src.models.contribuinte import Contribuinte

contribuinte_bp = Blueprint("contribuinte", __name__, url_prefix="/contribuintes")


def _parse_form(form):
    """Valida os campos do formulário e retorna (dados, erro)."""
    nome = form.get("nome", "").strip()
    bairro = form.get("bairro", "").strip()
    data_str = form.get("data_primeira_contribuicao", "").strip()

    if not nome:
        return None, "O nome é obrigatório."

    try:
        data_primeira = datetime.strptime(data_str, "%d/%m/%Y").date()
    except ValueError:
        return None, "Data inválida. Use o formato DD/MM/AAAA."

    dados = {
        "nome": nome,
        "bairro": bairro or None,
        "data_primeira_contribuicao": data_primeira,
    }
    return dados, None


@contribuinte_bp.route("/")
@login_required
def listar():
    busca = request.args.get("q", "").strip()
    query = Contribuinte.query

    if busca:
        if busca.isdigit():
            query = query.filter(Contribuinte.id == int(busca))
        else:
            query = query.filter(Contribuinte.nome.ilike(f"%{busca}%"))

    contribuintes = query.order_by(Contribuinte.nome).all()
    return render_template("contribuintes/lista.html", contribuintes=contribuintes, busca=busca)


@contribuinte_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        dados, erro = _parse_form(request.form)
        if erro:
            flash(erro, "danger")
            return render_template("contribuintes/form.html", contribuinte=None, valores=request.form)

        contribuinte = Contribuinte(**dados)
        db.session.add(contribuinte)
        db.session.commit()
        flash(f"Contribuinte '{contribuinte.nome}' cadastrado com sucesso!", "success")
        return redirect(url_for("contribuinte.listar"))

    return render_template("contribuintes/form.html", contribuinte=None, valores={})


@contribuinte_bp.route("/<int:contribuinte_id>/editar", methods=["GET", "POST"])
@login_required
def editar(contribuinte_id):
    contribuinte = Contribuinte.query.get_or_404(contribuinte_id)

    if request.method == "POST":
        dados, erro = _parse_form(request.form)
        if erro:
            flash(erro, "danger")
            return render_template("contribuintes/form.html", contribuinte=contribuinte, valores=request.form)

        contribuinte.nome = dados["nome"]
        contribuinte.bairro = dados["bairro"]
        contribuinte.data_primeira_contribuicao = dados["data_primeira_contribuicao"]
        db.session.commit()
        flash(f"Contribuinte '{contribuinte.nome}' atualizado com sucesso!", "success")
        return redirect(url_for("contribuinte.listar"))

    valores = {
        "nome": contribuinte.nome,
        "bairro": contribuinte.bairro or "",
        "data_primeira_contribuicao": contribuinte.data_primeira_contribuicao.strftime("%d/%m/%Y"),
    }
    return render_template("contribuintes/form.html", contribuinte=contribuinte, valores=valores)


@contribuinte_bp.route("/<int:contribuinte_id>/remover", methods=["GET", "POST"])
@login_required
def remover(contribuinte_id):
    contribuinte = Contribuinte.query.get_or_404(contribuinte_id)

    if request.method == "POST":
        nome = contribuinte.nome
        db.session.delete(contribuinte)
        db.session.commit()
        flash(f"Contribuinte '{nome}' removido com sucesso!", "success")
        return redirect(url_for("contribuinte.listar"))

    return render_template("contribuintes/confirmar_remocao.html", contribuinte=contribuinte)
