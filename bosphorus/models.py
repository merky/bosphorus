
# bosphorus database
from flask.ext.sqlalchemy import SQLAlchemy
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


class Study(db.Model):
    """ imaging study (e.g. MRI session) """
    id = db.Column(db.Integer, primary_key=True)

    # orthanc_id corresponds to study uid within orthanc
    orthanc_id = db.Column(db.String, unique=True)

    # relationship to person (confirmed)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person    = db.relationship("Person",
                                backref = "studies",
                                primaryjoin = "Study.person_id==Person.id")

    # potential person match
    match_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    match    = db.relationship("Person",
                                backref = "matches",
                                primaryjoin = "Study.match_id==Person.id")

    #@cache.memoize(50)
    def get(self):
        """ return orthanc object of study """
        return orthanc.study(self.orthanc_id)

    def __repr__(self):
        return '<Study %r>' % self.orthanc_id


class ResearchID(db.Model):
    """ List of all possible research IDs """
    id = db.Column(db.Integer, primary_key=True)
    research_id = db.Column(db.String(120), unique=True)
    used        = db.Column(db.Boolean)

    def __repr__(self):
        return '<ResearchID %r>' % self.research_id


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    research_id = db.Column(db.String(120), unique=True)
    clinical_id = db.Column(db.String(120), unique=True)
    first_name  = db.Column(db.String(120))
    last_name   = db.Column(db.String(120))
    dob         = db.Column(db.Date)
    ssn         = db.Column(db.String(11))

    @property
    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def orthanc_studies(self):
        """ return orthanc objects of studies """
        return [orthanc.study(x.orthanc_id) for x in self.studies]

    def __repr__(self):
        return '<Person %r>' % self.research_id

