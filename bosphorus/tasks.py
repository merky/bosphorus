from celery import Celery
from celery.signals   import task_postrun
from flask.globals    import current_app
from flask.ext.login  import current_user
from sqlalchemy import or_

from bosphorus.models import db, orthanc, Study, StudyHistory, Person

###############################################
# Periodic Tasks
###############################################

celery = Celery() 


@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from 
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors 
    # won't propagate across tasks)
    db.session.remove()


@celery.task(name='task.clean_studies')
def clean_studies():
    """ Marks any studies in DB that cannot be found in Orthanc, God forbid  """
    # get all studies
    studies  = Study.query.all()

    for study in studies:
        # sync existence
        study.exists = study.orthanc_exists
        db.session.merge(study)

    try:
        db.session.commit()
    except:
        db.session.rollback()


@celery.task(name='task.match_unassigned')
def match_unassigned():
    """ this matches people with unassigned studies based
        on dicom header info, e.g. patient_id
    """
    # get all studies
    studies  = Study.query.filter(Study.person==None).all()

    for study in studies:
        # check that study exists on orthanc
        if not study.exists: continue

        # get any person matching research ID for this study
        dicom_id = study.get().patient.patient_id.strip()
        person_match = Person.query.filter(Person.clinical_id==dicom_id).first()
        if person_match is not None:
            study.person = person_match
            db.session.merge(study)

    try:
        db.session.commit()
    except:
        db.session.rollback()


@celery.task(name='task.update_studies')
def update_studies():
    studies  = orthanc.get_new.studies()
    for s in studies:
        if s.is_anonymized: continue 

        study_exists = Study.query.filter(
            or_(Study.orthanc_id==s.id, Study.orthanc_anonymized_id==s.id)
        ).count()
        if study_exists == 0:
            study = Study(orthanc_id = s.id,
                          person_id  = None)
            db.session.add(study)
    try:
        db.session.commit()
        orthanc.reset_changes()
        match_unassigned.delay()
    except:
        db.session.rollback()


###############################################
# User Tasks
###############################################

@celery.task(name='task.send_study')
def send_study(study_id, modality, user_id):
    current_app.logger.info("Starting process to send study_id={}".format(study_id))
    # get study
    study = Study.query.filter(Study.id==study_id).first()

    current_app.logger.info("Anonymizing study_id={} ...".format(study_id))
    req = study.get().anonymize(study.person.research_id)
    current_app.logger.info("Anonymization results: {}".format(req))

    if req is not None and "ID" in req:
        anon_id = req["ID"]
        anon_study = orthanc.study(anon_id)
        current_app.logger.info(
            "Sending study_id={} to modality={}...".format(study_id,modality)
        )
        req = anon_study.send_to(modality)

        # TODO: error sending; raise exception
        if req != {}: return None
	try:
            study_history = StudyHistory(study_id = study_id,
                                         user_id  = user_id,
                                         modality = modality,
                                         action   = "sent") 

            db.session.add(study_history)
            study.orthanc_anonymized_id = anon_id
            db.session.merge(study)
            db.session.commit()
        except:
            db.session.rollback()

