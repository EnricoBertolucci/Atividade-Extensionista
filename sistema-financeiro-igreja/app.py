import os

from flask import Flask, render_template
from flask_cors import CORS
from flask_login import login_required

from src.auth import login_manager
from src.models import db
from src.routes.auth import auth_bp
from src.seed import seed_categorias_padrao

BASE_DIR = os.path.dirname(__file__)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "src", "templates"),
    static_folder=os.path.join(BASE_DIR, "src", "static"),
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-troque-em-producao")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'app.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()
    seed_categorias_padrao()


@app.route("/")
@login_required
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
