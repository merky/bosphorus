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
    # new studies received by orthanc
    studies  = orthanc.get_new.studies()
    # get any persons matching existing research IDs for those studies
    dicom_patient_ids = [x.patient.patient_id for x in studies]
    matches = {study.id: Person.query.filter(Person.clinical_id==study.patient.patient_id).first()
                         for study in studies}
    # render listing
    return render_template('studies.new.html',studies=studies, matches=matches)


