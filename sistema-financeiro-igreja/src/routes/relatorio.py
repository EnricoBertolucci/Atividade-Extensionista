import csv
import io
from datetime import date
from decimal import Decimal

from flask import Blueprint, Response, render_template, request
from flask_login import login_required
from sqlalchemy import extract

from src.models.categoria import Categoria
from src.models.lancamento import Lancamento

relatorio_bp = Blueprint("relatorio", __name__, url_prefix="/relatorios")

NOME_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _totais_por_tipo(lancamentos):
    entradas = sum((l.valor for l in lancamentos if l.tipo == "entrada"), Decimal("0"))
    saidas = sum((l.valor for l in lancamentos if l.tipo == "saida"), Decimal("0"))
    return entradas, saidas


def _lancamentos_do_mes(mes, ano):
    return Lancamento.query.filter(
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano,
    ).all()


@relatorio_bp.route("/arrecadacao")
@login_required
def arrecadacao():
    ano = request.args.get("ano", type=int) or date.today().year
    hoje = date.today()

    meses = []
    total_entradas_ano = Decimal("0")
    total_saidas_ano = Decimal("0")
    for numero_mes in range(1, 13):
        entradas, saidas = _totais_por_tipo(_lancamentos_do_mes(numero_mes, ano))
        meses.append({
            "numero": numero_mes,
            "nome": NOME_MESES[numero_mes - 1],
            "entradas": entradas,
            "saidas": saidas,
            "saldo": entradas - saidas,
        })
        total_entradas_ano += entradas
        total_saidas_ano += saidas

    # Projeção anual: média mensal de arrecadação (entradas) no ano × 12.
    meses_decorridos = hoje.month if ano == hoje.year else 12
    media_mensal = total_entradas_ano / meses_decorridos if meses_decorridos else Decimal("0")
    projecao_anual = media_mensal * 12

    return render_template(
        "relatorios/arrecadacao.html",
        ano=ano,
        ano_atual=hoje.year,
        meses=meses,
        total_entradas_ano=total_entradas_ano,
        total_saidas_ano=total_saidas_ano,
        saldo_ano=total_entradas_ano - total_saidas_ano,
        media_mensal=media_mensal,
        projecao_anual=projecao_anual,
    )


@relatorio_bp.route("/categoria")
@login_required
def categoria():
    hoje = date.today()
    mes = request.args.get("mes", type=int) or hoje.month
    ano = request.args.get("ano", type=int) or hoje.year

    lancamentos = _lancamentos_do_mes(mes, ano)

    por_categoria = {}
    for l in lancamentos:
        chave = l.categoria_id
        if chave not in por_categoria:
            por_categoria[chave] = {"categoria": l.categoria, "entradas": Decimal("0"), "saidas": Decimal("0")}
        if l.tipo == "entrada":
            por_categoria[chave]["entradas"] += l.valor
        else:
            por_categoria[chave]["saidas"] += l.valor

    linhas = sorted(por_categoria.values(), key=lambda item: item["categoria"].nome)
    total_entradas, total_saidas = _totais_por_tipo(lancamentos)

    return render_template(
        "relatorios/categoria.html",
        mes=mes,
        ano=ano,
        nome_mes=NOME_MESES[mes - 1],
        linhas=linhas,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
    )


@relatorio_bp.route("/exportar-csv")
@login_required
def exportar_csv():
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

    lancamentos = query.order_by(Lancamento.data.asc(), Lancamento.id.asc()).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(["Data", "Tipo", "Categoria", "Contribuinte", "Descrição", "Valor (R$)"])
    for l in lancamentos:
        writer.writerow([
            l.data.strftime("%d/%m/%Y"),
            "Entrada" if l.tipo == "entrada" else "Saída",
            l.categoria.nome,
            l.contribuinte.nome if l.contribuinte else "",
            l.descricao or "",
            f"{l.valor:.2f}".replace(".", ","),
        ])

    nome_arquivo = f"lancamentos_{mes:02d}_{ano}.csv"
    # utf-8-sig (BOM) garante acentuação correta ao abrir no Excel em português.
    return Response(
        buffer.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"},
    )
