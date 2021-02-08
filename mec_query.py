import os 
import math
import pandas as pd

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

server = Flask(__name__)
server.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(server)

class Candidate(db.Model):
    mec_id = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String)

class Contributor(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    zip5 = db.Column(db.String)

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    mec_id = db.Column(db.String, db.ForeignKey("candidate.mec_id"), nullable=False)
    candidate = db.relationship('Candidate', backref=db.backref("contributions", lazy=True))
    contributor_id = db.Column(db.Integer, db.ForeignKey("contributor.id"), nullable=False)
    contributor = db.relationship('Contributor', backref=db.backref("contributions", lazy=True))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    employer = db.Column(db.String)
    occupation = db.Column(db.String)
    amount = db.Column(db.Float)
    contribution_type = db.Column(db.String)
    report = db.Column(db.String)

def build_mec_df(mec_ids):
    li = []
    for filename in os.listdir('data/mec'):
        df = pd.read_csv('data/mec/' + filename, index_col=None, header=0, parse_dates=['Date'])
        df.loc[:, 'ZIP5'] = df.loc[:, 'Zip'].astype(str).str[:5]
        df.loc[:, 'MECID'] = df.loc[:, ' MECID']
        df = df[df['MECID'].isin(mec_ids)]
        li.append(df)
    frame = pd.concat(li, axis=0, ignore_index=True)
    return frame

def clear_tables():
    db.drop_all()
    db.create_all()
    db.session.commit()

def insert_contributions(mec_df):
    mec_col_name = ' MECID' # this column has a space in front for some reason
    candidate_dict = {}
    contributor_dict = {}
    objects_to_insert = []
    for index, row in mec_df.iterrows():

        if row[mec_col_name] not in candidate_dict:
            this_candidate = Candidate(name=row['Committee Name'], mec_id=row[mec_col_name])
            objects_to_insert.append(this_candidate)
            candidate_dict[row[mec_col_name]] = this_candidate
        else:
            this_candidate = candidate_dict[row[mec_col_name]]

        contributor_name = "no name"
        if isinstance(row['Committee'], str):
            contributor_name = str(row['Committee'])
        elif isinstance(row['Company'], str):
            contributor_name = str(row['Company'])
        elif isinstance(row['Last Name'], str):
            contributor_name = str(row['First Name'])+str(" ")+str(row['Last Name'])

        namezip = contributor_name+" "+row['ZIP5']
        if namezip not in contributor_dict:
            this_contributor = Contributor(name=contributor_name, zip5=row['ZIP5'])
            contributor_dict[namezip] = this_contributor
            objects_to_insert.append(this_contributor)
        else:
            this_contributor = contributor_dict[namezip]
            
            
        # if row['Latitude'] and row['Longitude']:
        #     lat = row['Latitude']
        #     lon = row['Longitude']
        # else:
        lat = None 
        lon = None

        this_contribution = Contribution(candidate=this_candidate, 
            contributor=this_contributor,
            lat = lat, lon = lon,
            employer = row['Employer'], occupation = row['Occupation'], 
            date = row['Date'], amount = row['Amount'], 
            contribution_type = row['Contribution Type'], report = row['Report'])
        db.session.add(this_contribution)

    db.session.commit()

def get_all_contributions():
    return Contribution.query.all()