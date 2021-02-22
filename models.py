from database import db
from sqlalchemy import Column, String


class Candidate(db.Model):
    __tablename__ = "candidates"

    name = Column(String, primary_key=True)
