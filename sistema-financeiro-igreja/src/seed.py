from src.models import db
from src.models.categoria import Categoria

CATEGORIAS_PADRAO = [
    ("Dízimo", "entrada"),
    ("Oferta", "entrada"),
    ("Doação", "entrada"),
    ("Despesas Fixas", "saida"),
    ("Despesas Variáveis", "saida"),
]


def seed_categorias_padrao():
    if Categoria.query.first() is not None:
        return
    for nome, tipo in CATEGORIAS_PADRAO:
        db.session.add(Categoria(nome=nome, tipo=tipo))
    db.session.commit()
