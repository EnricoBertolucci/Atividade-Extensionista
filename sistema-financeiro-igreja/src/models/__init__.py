from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from src.models.usuario import Usuario  # noqa: E402
from src.models.contribuinte import Contribuinte  # noqa: E402
from src.models.categoria import Categoria  # noqa: E402
from src.models.lancamento import Lancamento  # noqa: E402

__all__ = ["db", "Usuario", "Contribuinte", "Categoria", "Lancamento"]
