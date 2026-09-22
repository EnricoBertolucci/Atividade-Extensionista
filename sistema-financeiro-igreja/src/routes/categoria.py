from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from src.models import db
from src.models.categoria import TIPOS_CATEGORIA, Categoria

categoria_bp = Blueprint("categoria", __name__, url_prefix="/categorias")


def _parse_form(form):
    nome = form.get("nome", "").strip()
    tipo = form.get("tipo", "").strip()

    if not nome:
        return None, "O nome da categoria é obrigatório."
    if tipo not in TIPOS_CATEGORIA:
        return None, "Selecione um tipo válido (entrada ou saída)."

    return {"nome": nome, "tipo": tipo}, None


@categoria_bp.route("/")
@login_required
def listar():
    categorias = Categoria.query.order_by(Categoria.tipo, Categoria.nome).all()
    return render_template("categorias/lista.html", categorias=categorias)


@categoria_bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    if request.method == "POST":
        dados, erro = _parse_form(request.form)
        if not erro and Categoria.query.filter_by(nome=dados["nome"]).first():
            erro = "Já existe uma categoria com esse nome."

        if erro:
            flash(erro, "danger")
            return render_template("categorias/form.html", categoria=None, valores=request.form)

        categoria = Categoria(**dados)
        db.session.add(categoria)
        db.session.commit()
        flash(f"Categoria '{categoria.nome}' criada com sucesso!", "success")
        return redirect(url_for("categoria.listar"))

    return render_template("categorias/form.html", categoria=None, valores={})


@categoria_bp.route("/<int:categoria_id>/editar", methods=["GET", "POST"])
@login_required
def editar(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)

    if request.method == "POST":
        dados, erro = _parse_form(request.form)
        if not erro:
            existente = Categoria.query.filter_by(nome=dados["nome"]).first()
            if existente and existente.id != categoria.id:
                erro = "Já existe uma categoria com esse nome."

        if erro:
            flash(erro, "danger")
            return render_template("categorias/form.html", categoria=categoria, valores=request.form)

        categoria.nome = dados["nome"]
        categoria.tipo = dados["tipo"]
        db.session.commit()
        flash(f"Categoria '{categoria.nome}' atualizada com sucesso!", "success")
        return redirect(url_for("categoria.listar"))

    valores = {"nome": categoria.nome, "tipo": categoria.tipo}
    return render_template("categorias/form.html", categoria=categoria, valores=valores)


@categoria_bp.route("/<int:categoria_id>/remover", methods=["GET", "POST"])
@login_required
def remover(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)

    if request.method == "POST":
        if categoria.lancamentos:
            flash(
                f"Não é possível remover '{categoria.nome}': existem lançamentos usando essa categoria.",
                "danger",
            )
            return redirect(url_for("categoria.listar"))

        db.session.delete(categoria)
        db.session.commit()
        flash(f"Categoria '{categoria.nome}' removida com sucesso!", "success")
        return redirect(url_for("categoria.listar"))

    return render_template("categorias/confirmar_remocao.html", categoria=categoria)
