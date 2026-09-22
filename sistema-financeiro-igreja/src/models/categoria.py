from src.models import db

TIPOS_CATEGORIA = ("entrada", "saida")


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)

    lancamentos = db.relationship("Lancamento", back_populates="categoria")

    __table_args__ = (
        db.CheckConstraint("tipo IN ('entrada', 'saida')", name="ck_categoria_tipo"),
    )

    def __repr__(self):
        return f"<Categoria {self.nome} ({self.tipo})>"
