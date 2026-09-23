from datetime import date

import src.models.contribuinte as contribuinte_module
from src.models.contribuinte import Contribuinte


class _DataFixa(date):
    """Subclasse de date com `today()` fixo, para tornar os testes determinísticos."""

    FIXA = date(2026, 3, 15)

    @classmethod
    def today(cls):
        return cls.FIXA


def _com_hoje_fixo(monkeypatch, hoje):
    _DataFixa.FIXA = hoje
    monkeypatch.setattr(contribuinte_module, "date", _DataFixa)


def test_tempo_contribuicao_mesmo_mes(monkeypatch):
    _com_hoje_fixo(monkeypatch, date(2026, 3, 15))
    contribuinte = Contribuinte(nome="Fulano", data_primeira_contribuicao=date(2026, 3, 1))

    assert contribuinte.tempo_contribuicao == (0, 0)


def test_tempo_contribuicao_virada_de_ano(monkeypatch):
    _com_hoje_fixo(monkeypatch, date(2026, 1, 10))
    contribuinte = Contribuinte(nome="Fulano", data_primeira_contribuicao=date(2025, 11, 1))

    assert contribuinte.tempo_contribuicao == (0, 2)


def test_tempo_contribuicao_data_futura(monkeypatch):
    """Não há validação de data futura no modelo; o cálculo resulta em diferença negativa."""
    _com_hoje_fixo(monkeypatch, date(2026, 3, 15))
    contribuinte = Contribuinte(nome="Fulano", data_primeira_contribuicao=date(2026, 6, 1))

    anos, meses = contribuinte.tempo_contribuicao
    assert (anos, meses) == (-1, 9)


def test_tempo_contribuicao_formatado(monkeypatch):
    _com_hoje_fixo(monkeypatch, date(2026, 3, 15))
    contribuinte = Contribuinte(nome="Fulano", data_primeira_contribuicao=date(2024, 1, 1))

    assert contribuinte.tempo_contribuicao_formatado == "2 ano(s) e 2 mês(es)"
