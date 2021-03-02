from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from dotenv import load_dotenv

db = SQLAlchemy()

load_dotenv()


def init_app():
    app = Flask(__name__)
    sslify = SSLify(app)
    app.config.from_object("config")
    db.init_app(app)
    with app.app_context():
        from . import mec_query
        from .dashboard import init_dashboard

        app = init_dashboard(app)

        return app


server = init_app()

db = SQLAlchemy(server)
