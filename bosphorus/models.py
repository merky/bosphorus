
from datetime import datetime

# bosphorus database
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Table
db = SQLAlchemy()

# include orthanc here; basically 2nd set of models
from orthancpy import Orthanc
orthanc = Orthanc()

from bosphorus.utils import cache

ROLE_USER =1
ROLE_ADMIN=2

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email    = db.Column(db.String(120), unique=True)
    name     = db.Column(db.String(120))
    role     = db.Column(db.SmallInteger, default = ROLE_USER)
    password = db.Column(db.String(120))

    def is_admin(self):
        return self.role==ROLE_ADMIN

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return unicode(self.id)

    def get_password(self):
        return self.password

    def __repr__(self):
        return '<User %r>' % self.username


class StudyHistory(db.Model):
    """ history of actions on study """
    id = db.Column(db.Integer, primary_key=True)

    # relationship to study
    study_id = db.Column(db.Integer, db.ForeignKey('study.id'))

    # relationship to user who performed action
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'))
    user     = db.relationship("User",
                                backref = "transfers",
                                primaryjoin = "StudyHistory.user_id==User.id")

    modality = db.Column(db.String(120))
    action   = db.Column(db.String(120))
    datetime = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<StudyTransfer %r>' % self.id



class Study(db.Model):
    """ imaging study (e.g. MRI session) """
    id = db.Column(db.Integer, primary_key=True)

    # orthanc_id corresponds to study uid within orthanc
    orthanc_id = db.Column(db.String(120), unique=True)
    orthanc_anonymized_id = db.Column(db.String(120), unique=True)
    exists     = db.Column(db.Boolean, default=True)

    # relationship to person (confirmed)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person    = db.relationship("Person",
                                backref = "studies",
                                primaryjoin = "Study.person_id==Person.id")
    # relationship with history
    history   = db.relationship("StudyHistory", backref="study")

    def get(self):
        """ return orthanc object of study """
        return orthanc.study(self.orthanc_id)

    @property
    def sent(self):
        return True if self.history else False

    @property
    def orthanc_exists(self):
        return self.get().exists

    def __repr__(self):
        return '<Study %r>' % self.orthanc_id


person_protocol_association = db.Table('research_protocols',
    db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
    db.Column('protocol_id', db.Integer, db.ForeignKey('research_protocol.id'))
)
   

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    research_id = db.Column(db.String(120), unique=True)
    clinical_id = db.Column(db.String(120), unique=True)
    first_name  = db.Column(db.String(120))
    last_name   = db.Column(db.String(120))
    dob         = db.Column(db.Date)
    ssn         = db.Column(db.String(11))
    notes       = db.Column(db.String(1024))

    protocols    = db.relationship("ResearchProtocol",
                                   secondary = person_protocol_association,
                                   backref = db.backref('persons', 
                                                lazy='dynamic'))

    @property
    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def orthanc_studies(self):
        """ return orthanc objects of studies """
        return [orthanc.study(x.orthanc_id) for x in self.studies]

    def __repr__(self):
        return '<Person %r>' % self.research_id


class ResearchID(db.Model):
    """ List of all possible research IDs """
    id = db.Column(db.Integer, primary_key=True)
    research_id = db.Column(db.String(120), unique=True)
    used        = db.Column(db.Boolean)

    def __repr__(self):
        return '<ResearchID %r>' % self.research_id



class ResearchProtocol(db.Model):
    """ List of all protocol numbers """
    id = db.Column(db.Integer, primary_key=True)
    number      = db.Column(db.String(120), unique=True)
    title       = db.Column(db.String(120))
    description = db.Column(db.String(120))

    def __repr__(self):
        return '<ResearchProtocol %r>' % self.number


