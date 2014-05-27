from flask import Blueprint, render_template

from bosphorus.models import db, Person
from orthancpy import Orthanc

studies = Blueprint('studies', __name__, url_prefix='/studies')
orthanc = Orthanc('http://localhost:8042')

@studies.route('/')
#@cache.cached(timeout=1000)
def index():
    return render_template('studies.list.html')

@studies.route('/new')
def new():
    studies  = orthanc.get_new.studies()
    clinical_ids = [x[0] for x in db.session.query(Person.clinical_id).all()]
    matches = [x.id for x in studies if x.patient.patient_id in clinical_ids]
    return render_template('studies.new.html',studies=studies, matches=matches)


