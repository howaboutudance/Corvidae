from corvidae import db
from sqlalchemy import ForeignKey

class Handle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text,  unique=True)
    owner = db.Colummn(owner, ForeignKey('user.id'))