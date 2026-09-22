from datetime import datetime

from src.models import db

TIPOS_LANCAMENTO = ("entrada", "saida")


class Lancamento(db.Model):
    __tablename__ = "lancamentos"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    contribuinte_id = db.Column(db.Integer, db.ForeignKey("contribuintes.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    categoria = db.relationship("Categoria", back_populates="lancamentos")
    contribuinte = db.relationship("Contribuinte", back_populates="lancamentos")
    usuario = db.relationship("Usuario")

    __table_args__ = (
        db.CheckConstraint("tipo IN ('entrada', 'saida')", name="ck_lancamento_tipo"),
        db.CheckConstraint("valor > 0", name="ck_lancamento_valor_positivo"),
    )

    def __repr__(self):
        return f"<Lancamento {self.tipo} {self.valor}>"
