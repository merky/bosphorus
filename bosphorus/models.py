from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email    = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, username, password, email=None):
        self.username = username
        self.password = password
        self.email    = email

    def __repr__(self):
        return '<User %r>' % self.username


class ResearchID(db.Model):
    """ List of all possible research IDs """
    id = db.Column(db.Integer, primary_key=True)
    research_id = db.Column(db.String(120), unique=True)
    used        = db.Column(db.Boolean)

    def __init__(self, research_id, used=False):
        self.research_id = research_id
        self.used        = used


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    research_id = db.Column(db.String(120), unique=True)
    clinical_id = db.Column(db.String(120), unique=True)
    first_name  = db.Column(db.String(120))
    last_name   = db.Column(db.String(120))
    dob         = db.Column(db.Date)
    ssn         = db.Column(db.String(11))

    def __init__(self, research_id,
                       clinical_id,
                       first_name=None,
                       last_name=None,
                       dob=None,
                       ssn=None):

        if research_id is None and clinical_id is None:
            raise Exception('Unable to create person without research or clinical ID')

        self.research_id = research_id
        self.clinical_id = clinical_id
        self.first_name  = first_name
        self.last_name   = last_name
        self.dob         = dob
        self.ssn         = ssn

