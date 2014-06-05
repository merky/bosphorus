from flask import Blueprint, render_template, flash, url_for, redirect, request

from bosphorus.models import db, orthanc, Person, Study, ResearchID
from bosphorus.utils  import get_redirect_target
from bosphorus.forms  import StudyAssignForm

studies = Blueprint('studies', __name__, url_prefix='/studies')


def match_unassigned():
    """ this matches people with unassigned studies based
        on dicom header info, e.g. patient_id
    """
    studies  = Study.query.filter(Study.person==None).all()
    # get any persons matching existing research IDs for those studies
    orthanc_studies = [x.get().patient.patient_id for x in studies]

    for study in studies:
        match = Person.query.filter(Person.clinical_id==study.get().patient.patient_id).first()
        if match is None: continue
        study.match = match

    try:
        db.session.commit()
    except:
        pass


@studies.route('/update')
def update():
    """ check orthanc for new studies and
        add them to the db
    """
    studies  = orthanc.get_new.studies()
    for s in studies:
        study_exists = Study.query.filter(Study.orthanc_id==s.id).count()
        if not study_exists:
            study = Study(orthanc_id = s.id,
                          person_id  = None)
            db.session.add(study)
    try:
        db.session.commit()
    except:
        pass

    match_unassigned()

    loc = get_redirect_target()
    if loc is None:
        return redirect(url_for('main.home'))
    return redirect(loc)

@studies.route('/')
def index():
    return redirect(url_for('studies.list'))

@studies.route('/all')
def list():
    studies = Study.query.all()
    research_ids = [x[0] for x in db.session.query(Person.research_id).all()]
    return render_template('studies.list.html', studies=studies, title="Studies", research_ids=research_ids)

@studies.route('/unassigned')
def unassigned():
    studies = Study.query.filter(Study.person_id==None).all()
    return render_template('studies.list.html', studies=studies, title="Unassigned Studies")

@studies.route('/assigned')
def assigned():
    studies = Study.query.filter(Study.person_id!=None).all()
    return render_template('studies.list.html', studies=studies, title="Assigned Studies")

@studies.route('/<orthanc_id>/unassign')
def unassign(orthanc_id):
    """ action: unassign from person """
    study = Study.query.filter(Study.orthanc_id==orthanc_id).first()
    if study is None:
        flash('No study found with specified ID', category='danger')
        return redirect(url_for('studies.list'))

    study.person_id = None

    # commit changes
    db.session.merge(study)
    db.session.commit()

    # let the person know what's up
    flash('Study unassigned successfully!', category='success')
    return redirect(request.referrer or url_for('studies.list'))


@studies.route('/<orthanc_id>/assign', methods=['POST','GET'])
def assign(orthanc_id):
    """ action: assign to person """
    # get orthanc study
    study = Study.query.filter(Study.orthanc_id==orthanc_id).first()
    if study is None:
        flash('No study found with specified ID', category='danger')
        return redirect(url_for('studies.list'))

    # get all available choices for research ID
    research_ids = ResearchID.query.filter(ResearchID.used==True).all()
    id_choices = [(x.research_id,x.research_id) for x in research_ids]

    # apply choices to form
    form = StudyAssignForm(request.form)
    form.research_id.choices = id_choices

    # on form submission
    if form.validate_on_submit():
        # grab person
        person = Person.query.filter(Person.research_id==form.research_id.data).first()
        if person is None:
            flash('No person found with specified ID. Study not assigned', category='danger')
            return redirect(url_for('studies.list', orthanc_id=orthanc_id))

        study.person = person

        # commit changes
        db.session.merge(study)
        db.session.commit()

        # let the person know what's up
        flash('Study assigned successfully!', category='success')
        return redirect(url_for('studies.list', orthanc_id = orthanc_id))

    elif request.method=='POST':
        # problems with form data
        flash('There were some errors with the form.', category='danger')

    return render_template('studies.assign.html', form=form)


@studies.route('/<orthanc_id>/view')
def view(orthanc_id):
    """ view details of orthanc study """
    study = Study.query.filter(Study.orthanc_id==orthanc_id).first()
    if study is None:
        flash('Study ID not found', category='danger')
        redirect(url_for('studies.list'))
    return render_template('studies.view.html',study=study)


@studies.route('/<orthanc_id>/assign_to/<research_id>')
def assign_to_person(orthanc_id, research_id):
    """ action: assign orthanc study to person """

    # grab person based on ID
    person = Person.query.filter(Person.research_id==research_id).first()

    # if they don't exist, redirect to person list page
    if person is None:
        flash('Research ID {} not found.', category='warning')
        return redirect(url_for('studies.list'))

    try:
        study = Study(orthanc_id  = orthanc_id,
                      person_id   = person.id)
        db.session.add(study)
        db.session.commit()
    except:
        db.session.rollback()
        flash('Error assigning study to person', category='danger')
    else:
        flash('Study assigned.', category='success')

    # render page
    return redirect(url_for('studies.view', orthanc_id=orthanc_id))


