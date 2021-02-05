import os
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

server = Flask(__name__)
server.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(server)

class Contribution(db.Model):
    contribution = db.Column(db.Integer, primary_key=True)
    mec_id = db.Column(db.String, nullable=False)
    from_committee = db.Column(db.String)
    name = db.Column(db.String)
    zip5 = db.Column(db.String)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    employer = db.Column(db.String)
    occupation = db.Column(db.String)
    date = db.Column(db.Date)
    amount = db.Column(db.Float)
    contribution_type = db.Column(db.String)
    report = db.Column(db.String)
    
class Committee(db.Model):
    mec_id = db.Column(db.String, primary_key=True)
    committee_name = db.Column(db.String, nullable=False)

db.create_all()
db.session.commit()

contributions = Contribution.query.all()
print(contributions)