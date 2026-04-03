from flask import Flask
from .routes import init_routes
from .extensions import db,login_manager
from .forms import LoginForm, RegisterForm

app = Flask(__name__)
init_routes(app)

app.config["SECRET_KEY"] = "ramelamutharasususdha"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

from . import models
login_manager.init_app(app)
login_manager.login_view = "/"
