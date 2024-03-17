from flask_sqlalchemy import SQLAlchemy
from front_api import db

class Profile(db.Model()):
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column(db.Integer, nullable = False)
    country = db.Column(db.String(20))
    languages = db.Column(db.String(200))
    birthDate = db.Column(db.Date)
    about = db.Columnn(db.Text)
    pfpId = db.Column(db.Integer)