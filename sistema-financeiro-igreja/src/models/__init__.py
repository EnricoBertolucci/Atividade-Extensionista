from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def _habilitar_foreign_keys_sqlite(dbapi_connection, connection_record):
    """SQLite ignora FKs (e ondelete) por padrão; precisa ser ligado por conexão."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


from src.models.usuario import Usuario  # noqa: E402
from src.models.contribuinte import Contribuinte  # noqa: E402
from src.models.categoria import Categoria  # noqa: E402
from src.models.lancamento import Lancamento  # noqa: E402

__all__ = ["db", "Usuario", "Contribuinte", "Categoria", "Lancamento"]
