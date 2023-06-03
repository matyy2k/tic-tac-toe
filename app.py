from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from apps.tictactoe.models import *
from apps.tictactoe.views import app as app_tic
from db import Base, engine
from flask_session import Session

db = SQLAlchemy()


def init_db():
    Base.metadata.create_all(bind=engine)


def create_app():
    app = Flask(__name__)
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    app.config.from_object("config.DevelopmentConfig")
    db.init_app(app)
    init_db()

    app.register_blueprint(app_tic)

    return app


if __name__ == "__main__":
    create_app().run()
