from flask_login import LoginManager

from src.models import Usuario

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para acessar o sistema."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
