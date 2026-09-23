import os
from datetime import date
from decimal import Decimal

from flask import Flask, render_template
from flask_cors import CORS
from flask_login import login_required
from sqlalchemy import extract

from src.auth import login_manager
from src.models import db
from src.models.contribuinte import Contribuinte
from src.models.lancamento import Lancamento
from src.routes.auth import auth_bp
from src.routes.categoria import categoria_bp
from src.routes.contribuinte import contribuinte_bp
from src.routes.lancamento import lancamento_bp
from src.routes.relatorio import relatorio_bp
from src.seed import seed_categorias_padrao

BASE_DIR = os.path.dirname(__file__)


def create_app(config=None):
    """Application factory. `config` permite sobrepor config padrão (usado nos testes)."""
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "src", "templates"),
        static_folder=os.path.join(BASE_DIR, "src", "static"),
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-troque-em-producao")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'app.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(contribuinte_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(lancamento_bp)
    app.register_blueprint(relatorio_bp)

    with app.app_context():
        db.create_all()
        seed_categorias_padrao()

    @app.route("/")
    @login_required
    def index():
        hoje = date.today()
        lancamentos_mes = Lancamento.query.filter(
            extract("month", Lancamento.data) == hoje.month,
            extract("year", Lancamento.data) == hoje.year,
        ).all()
        total_entradas = sum((l.valor for l in lancamentos_mes if l.tipo == "entrada"), Decimal("0"))
        total_saidas = sum((l.valor for l in lancamentos_mes if l.tipo == "saida"), Decimal("0"))
        contribuintes_ativos = Contribuinte.query.filter_by(ativo=True).count()

        return render_template(
            "index.html",
            mes_atual=hoje.month,
            ano_atual=hoje.year,
            nome_mes_atual=hoje.strftime("%m/%Y"),
            total_entradas=total_entradas,
            total_saidas=total_saidas,
            saldo=total_entradas - total_saidas,
            contribuintes_ativos=contribuintes_ativos,
        )

    @app.route("/ajuda")
    @login_required
    def ajuda():
        return render_template("ajuda.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
