from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import Categoria, Lancamento, db


def _criar_categoria(tipo, nome):
    categoria = Categoria(nome=nome, tipo=tipo)
    db.session.add(categoria)
    db.session.commit()
    return categoria


def test_saldo_apenas_entradas(app):
    with app.app_context():
        categoria = _criar_categoria("entrada", "Dízimo Teste")
        db.session.add(Lancamento(tipo="entrada", valor=Decimal("100.00"), data=date.today(), categoria_id=categoria.id))
        db.session.add(Lancamento(tipo="entrada", valor=Decimal("50.00"), data=date.today(), categoria_id=categoria.id))
        db.session.commit()

        lancamentos = Lancamento.query.all()
        entradas = sum((l.valor for l in lancamentos if l.tipo == "entrada"), Decimal("0"))
        saidas = sum((l.valor for l in lancamentos if l.tipo == "saida"), Decimal("0"))

        assert entradas - saidas == Decimal("150.00")


def test_saldo_entradas_e_saidas(app):
    with app.app_context():
        cat_entrada = _criar_categoria("entrada", "Oferta Teste")
        cat_saida = _criar_categoria("saida", "Despesa Teste")

        db.session.add(Lancamento(tipo="entrada", valor=Decimal("300.00"), data=date.today(), categoria_id=cat_entrada.id))
        db.session.add(Lancamento(tipo="saida", valor=Decimal("120.50"), data=date.today(), categoria_id=cat_saida.id))
        db.session.commit()

        lancamentos = Lancamento.query.all()
        entradas = sum((l.valor for l in lancamentos if l.tipo == "entrada"), Decimal("0"))
        saidas = sum((l.valor for l in lancamentos if l.tipo == "saida"), Decimal("0"))

        assert entradas - saidas == Decimal("179.50")


def test_saldo_sem_lancamentos_e_zero(app):
    with app.app_context():
        lancamentos = Lancamento.query.all()
        entradas = sum((l.valor for l in lancamentos if l.tipo == "entrada"), Decimal("0"))
        saidas = sum((l.valor for l in lancamentos if l.tipo == "saida"), Decimal("0"))

        assert entradas - saidas == Decimal("0")


def test_lancamento_com_valor_negativo_viola_constraint(app):
    with app.app_context():
        categoria = _criar_categoria("entrada", "Dízimo Constraint")
        db.session.add(Lancamento(tipo="entrada", valor=Decimal("-10.00"), data=date.today(), categoria_id=categoria.id))

        with pytest.raises(IntegrityError):
            db.session.commit()
