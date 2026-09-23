from werkzeug.datastructures import MultiDict

from src.routes.contribuinte import _parse_form as parse_contribuinte
from src.routes.lancamento import _parse_form as parse_lancamento
from src.routes.lancamento import _parse_valor


def test_contribuinte_data_invalida_retorna_erro():
    form = MultiDict({"nome": "Fulano", "bairro": "Centro", "data_primeira_contribuicao": "31/02/2026"})
    dados, erro = parse_contribuinte(form)

    assert dados is None
    assert erro == "Data inválida. Use o formato DD/MM/AAAA."


def test_contribuinte_nome_vazio_retorna_erro():
    form = MultiDict({"nome": "  ", "data_primeira_contribuicao": "01/01/2026"})
    dados, erro = parse_contribuinte(form)

    assert dados is None
    assert erro == "O nome é obrigatório."


def test_contribuinte_dados_validos():
    form = MultiDict({"nome": "Fulano", "bairro": "", "data_primeira_contribuicao": "05/03/2026"})
    dados, erro = parse_contribuinte(form)

    assert erro is None
    assert dados["nome"] == "Fulano"
    assert dados["bairro"] is None


def test_parse_valor_negativo_e_invalido():
    assert _parse_valor("-10,00") is None


def test_parse_valor_zero_e_invalido():
    assert _parse_valor("0") is None


def test_parse_valor_com_virgula_decimal():
    from decimal import Decimal

    assert _parse_valor("1.234,56") == Decimal("1234.56")


def test_lancamento_categoria_invalida_retorna_erro(app):
    with app.app_context():
        form = MultiDict(
            {
                "categoria_id": "9999",
                "valor": "100,00",
                "data": "10/03/2026",
                "descricao": "",
                "contribuinte_id": "",
            }
        )
        dados, erro = parse_lancamento(form)

        assert dados is None
        assert erro == "Selecione uma categoria válida."


def test_lancamento_data_invalida_retorna_erro(app):
    from src.models import Categoria, db

    with app.app_context():
        categoria = Categoria(nome="Dízimo Form", tipo="entrada")
        db.session.add(categoria)
        db.session.commit()

        form = MultiDict(
            {
                "categoria_id": str(categoria.id),
                "valor": "100,00",
                "data": "32/13/2026",
                "descricao": "",
                "contribuinte_id": "",
            }
        )
        dados, erro = parse_lancamento(form)

        assert dados is None
        assert erro == "Data inválida. Use o formato DD/MM/AAAA."
