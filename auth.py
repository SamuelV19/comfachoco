from flask_login import LoginManager
from models import User, db

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def init_login(app):
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None
