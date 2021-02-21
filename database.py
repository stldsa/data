import os
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
engine = create_engine(os.getenv("DB_URL"))
