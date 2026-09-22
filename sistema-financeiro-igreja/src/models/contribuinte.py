from datetime import date, datetime

from src.models import db


class Contribuinte(db.Model):
    __tablename__ = "contribuintes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    bairro = db.Column(db.String(120))
    data_primeira_contribuicao = db.Column(db.Date, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    lancamentos = db.relationship("Lancamento", back_populates="contribuinte")

    @property
    def tempo_contribuicao(self):
        """Retorna (anos, meses) entre a primeira contribuição e hoje."""
        hoje = date.today()
        anos = hoje.year - self.data_primeira_contribuicao.year
        meses = hoje.month - self.data_primeira_contribuicao.month
        if meses < 0:
            anos -= 1
            meses += 12
        return anos, meses

    @property
    def tempo_contribuicao_formatado(self):
        anos, meses = self.tempo_contribuicao
        return f"{anos} ano(s) e {meses} mês(es)"

    def __repr__(self):
        return f"<Contribuinte {self.nome}>"
