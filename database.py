import os
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from dsadata import init_app


load_dotenv()


db = SQLAlchemy()
engine = create_engine(os.getenv("DATABASE_URL"))


def reset():
    app = init_app()
    db = SQLAlchemy(app)
    db.drop_all()
    db.reset_all()
