import os
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

import contrib

load_dotenv()

server = Flask(__name__)
server.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(server)

class Contribution(db.Model):
    __tablename__ = 'contributions'
    contribution_id = db.Column(db.Integer, primary_key=True)
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
    __tablename__ = 'committees'
    mec_id = db.Column(db.String, primary_key=True)
    committee_name = db.Column(db.String, nullable=False)

db.create_all()
db.session.commit()
Contribution.query.delete()

# Right now only doing mayoral race, but update as necessary
mec_ids = ['C201499', 'C201099', 'C201500', 'C211544']
mec_df = contrib.create_contribution_df(mec_ids)

contributions_to_insert = []
for index, row in mec_df.iterrows():
    if row['Company']:
        name = row['Company']
    elif row['Last Name']:
        name = row['First Name']+" "+row['Last Name']
    else:
        name = None

    # if row['Latitude'] and row['Longitude']:
    #     lat = row['Latitude']
    #     lon = row['Longitude']
    # else:
    lat = None 
    lon = None

    this_contribution = Contribution(contribution_id = row['CD1_A ID'], mec_id = row[' MECID'],
        from_committee = row['Committee Name'], name = name, zip5 = row['ZIP5'], 
        lat = lat, lon = lon,
        employer = row['Employer'], occupation = row['Occupation'], date = row['Date'],
        amount = row['Amount'], contribution_type = row['Contribution Type'], report = row['Report'])
    contributions_to_insert.append(this_contribution)
db.session.bulk_save_objects(contributions_to_insert)
db.session.commit()

contributions = Contribution.query.all()