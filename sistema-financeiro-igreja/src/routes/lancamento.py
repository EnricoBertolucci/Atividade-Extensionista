from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import extract

from src.models import db
from src.models.categoria import Categoria
from src.models.contribuinte import Contribuinte
from src.models.lancamento import Lancamento

lancamento_bp = Blueprint("lancamento", __name__, url_prefix="/lancamentos")


def _parse_valor(valor_str):
    valor_str = (valor_str or "").strip()
    if not valor_str:
        return None
    if "," in valor_str:
        valor_str = valor_str.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(valor_str)
    except InvalidOperation:
        return None
    if valor <= 0:
        return None
    return valor


def _parse_form(form):
    categoria_id = form.get("categoria_id", "").strip()
    data_str = form.get("data", "").strip()
    descricao = form.get("descricao", "").strip()
    contribuinte_id = form.get("contribuinte_id", "").strip()

    categoria = Categoria.query.get(int(categoria_id)) if categoria_id.isdigit() else None
    if not categoria:
        return None, "Selecione uma categoria válida."

    valor = _parse_valor(form.get("valor"))
    if valor is None:
        return None, "Valor inválido. Use um número maior que zero (ex.: 150,00)."

    try:
        data_lancamento = datetime.strptime(data_str, "%d/%m/%Y").date()
    except ValueError:
        return None, "Data inválida. Use o formato DD/MM/AAAA."

    contribuinte = Contribuinte.query.get(int(contribuinte_id)) if contribuinte_id.isdigit() else None

    dados = {
        "tipo": categoria.tipo,
        "valor": valor,
        "data": data_lancamento,
        "descricao": descricao or None,
        "categoria_id": categoria.id,
        "contribuinte_id": contribuinte.id if contribuinte else None,
    }
    return dados, None


def _contexto_formulario(valores):
    return {
        "valores": valores,
        "categorias": Categoria.query.order_by(Categoria.tipo, Categoria.nome).all(),
        "contribuintes": Contribuinte.query.order_by(Contribuinte.nome).all(),
    }


@lancamento_bp.route("/")
@login_required
def listar():
    hoje = date.today()
    mes = request.args.get("mes", type=int) or hoje.month
    ano = request.args.get("ano", type=int) or hoje.year
    tipo = request.args.get("tipo", "").strip()
    categoria_id = request.args.get("categoria_id", type=int)

    query = Lancamento.query.filter(
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano,
    )
    if tipo in ("entrada", "saida"):
        query = query.filter(Lancamento.tipo == tipo)
    if categoria_id:
        query = query.filter(Lancamento.categoria_id == categoria_id)

    lancamentos = query.order_by(Lancamento.data.desc(), Lancamento.id.desc()).all()

    total_entradas = sum((l.valor for l in lancamentos if l.tipo == "entrada"), Decimal("0"))
    total_saidas = sum((l.valor for l in lancamentos if l.tipo == "saida"), Decimal("0"))
    saldo = total_entradas - total_saidas

    return render_template(
        "lancamentos/lista.html",
        lancamentos=lancamentos,
        mes=mes,
        ano=ano,
        tipo=tipo,
        categoria_id=categoria_id,
        categorias=Categoria.query.order_by(Categoria.tipo, Categoria.nome).all(),
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        saldo=saldo,
    )


@lancamento_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        dados, erro = _parse_form(request.form)
        if erro:
            flash(erro, "danger")
            return render_template(
                "lancamentos/form.html", lancamento=None, **_contexto_formulario(request.form)
            )

        dados["usuario_id"] = current_user.id
        lancamento = Lancamento(**dados)
        db.session.add(lancamento)
        db.session.commit()
        flash("Lançamento registrado com sucesso!", "success")
        return redirect(url_for("lancamento.listar"))

    return render_template("lancamentos/form.html", lancamento=None, **_contexto_formulario({}))


@lancamento_bp.route("/<int:lancamento_id>/editar", methods=["GET", "POST"])
@login_required
def editar(lancamento_id):
    lancamento = Lancamento.query.get_or_404(lancamento_id)

    if request.method == "POST":
        dados, erro = _parse_form(request.form)
        if erro:
            flash(erro, "danger")
            return render_template(
                "lancamentos/form.html", lancamento=lancamento, **_contexto_formulario(request.form)
            )

        lancamento.tipo = dados["tipo"]
        lancamento.valor = dados["valor"]
        lancamento.data = dados["data"]
        lancamento.descricao = dados["descricao"]
        lancamento.categoria_id = dados["categoria_id"]
        lancamento.contribuinte_id = dados["contribuinte_id"]
        db.session.commit()
        flash("Lançamento atualizado com sucesso!", "success")
        return redirect(url_for("lancamento.listar"))

    valores = {
        "categoria_id": str(lancamento.categoria_id),
        "valor": f"{lancamento.valor:.2f}".replace(".", ","),
        "data": lancamento.data.strftime("%d/%m/%Y"),
        "descricao": lancamento.descricao or "",
        "contribuinte_id": str(lancamento.contribuinte_id) if lancamento.contribuinte_id else "",
    }
    return render_template("lancamentos/form.html", lancamento=lancamento, **_contexto_formulario(valores))


@lancamento_bp.route("/<int:lancamento_id>/remover", methods=["GET", "POST"])
@login_required
def remover(lancamento_id):
    lancamento = Lancamento.query.get_or_404(lancamento_id)

    if request.method == "POST":
        db.session.delete(lancamento)
        db.session.commit()
        flash("Lançamento removido com sucesso!", "success")
        return redirect(url_for("lancamento.listar"))

    return render_template("lancamentos/confirmar_remocao.html", lancamento=lancamento)
