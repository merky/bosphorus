from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask.ext.login import login_required, current_user
from sqlalchemy import or_

from bosphorus.models import db, orthanc, Person, Study, ResearchID, StudyHistory, ResearchProtocol
from bosphorus.utils  import get_redirect_target, admin_required
from bosphorus.forms  import StudyAssignForm, ResearchProtocolForm
from bosphorus.tasks  import update_studies, match_unassigned, send_study

studies = Blueprint('studies', __name__, url_prefix='/studies')

###############################################
# Generic Study Actions
###############################################

@studies.route('/match')
@login_required
def match():
    match_unassigned.delay()
    return redirect(get_redirect_target() or url_for('main.home'))


@studies.route('/update')
@login_required 
def update():
    """ check orthanc for new studies and
        add them to the db
    """
    update_studies.delay()
    return redirect(get_redirect_target() or url_for('main.home'))




######################
# Study Lists
######################

@studies.route('/')
@login_required 
def index():
    return redirect(url_for('studies.action_required'))


@studies.route('/unsent')
@login_required 
def unsent():
    studies = [s for s in Study.query.all() if s.exists and not s.sent]
    return render_template('studies.list.html', studies=studies, title="Studies Not Sent")


@studies.route('/action-required')
@login_required 
def action_required():
    studies = [s for s in Study.query.filter(or_(Study.history==None,Study.person_id==None)).all() if s.exists]
    return render_template('studies.list.html', studies=studies, title="Studies That Require Action")


@studies.route('/all')
@login_required 
def list():
    studies = [s for s in Study.query.all() if s.exists]
    return render_template('studies.list.html', studies=studies, title="All Studies")


@studies.route('/unassigned')
@login_required 
def unassigned():
    studies = [s for s in Study.query.filter(Study.person_id==None).filter(Study.exists==True).all() if s.exists]
    return render_template('studies.list.html', studies=studies, title="Unassigned Studies")


@studies.route('/assigned')
@login_required 
def assigned():
    studies = Study.query.filter(Study.person_id!=None).filter(Study.exists==True).all()
    return render_template('studies.list.html', studies=studies, title="Assigned Studies")


######################
# Study Actions
######################

@studies.route('/<orthanc_id>/unassign')
@login_required 
def unassign(orthanc_id):
    """ action: unassign from person """
    study = Study.query.filter(Study.orthanc_id==orthanc_id).filter(Study.exists==True).first()
    if study is None:
        flash('No study found with specified ID', 'danger')
        return redirect(request.referrer or url_for('studies.index'))

    study.person_id = None

    # commit changes
    db.session.merge(study)
    db.session.commit()

    # let the user know what's up
    flash('Study unassigned successfully!', 'success')
    return redirect(request.referrer or url_for('studies.index'))


@studies.route('/<orthanc_id>/assign', methods=['POST','GET'])
@login_required 
def assign(orthanc_id):
    """ action: assign to person """
    # get orthanc study
    study = Study.query.filter(Study.orthanc_id==orthanc_id).filter(Study.exists==True).first()
    if study is None:
        flash('No study found with specified ID', 'danger')
        return redirect(request.referrer or url_for('studies.index'))

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
            flash('No person found with specified ID. Study not assigned', 'danger')
            return redirect(request.referrer or url_for('studies.view', orthanc_id=orthanc_id))

        study.person = person

        # commit changes
        db.session.merge(study)
        db.session.commit()

        # let the person know what's up
        flash('Study assigned successfully!', 'success')
        return redirect(url_for('studies.index'))

    elif request.method=='POST':
        # problems with form data
        flash('There were some errors with the form.', 'danger')

    return render_template('studies.assign.html', form=form, orthanc_id=study.orthanc_id)


@studies.route('/<orthanc_id>/send')
@login_required 
def send(orthanc_id,modality="XNAT"):
    """ view details of orthanc study """
    study_id = db.session.query(Study.id).filter(Study.orthanc_id==orthanc_id).first()[0]
    if not study_id:
        flash('Study ID not found', 'danger')
    elif modality not in orthanc.modalities:
        flash('Modality \"{}\" not found.'.format(modality), 'danger')
    else:
        send_study.delay(study_id, modality, current_user.id)
        flash("Study will be sent to {} shortly...".format(modality), 'success')

    return redirect(request.referrer or url_for('studies.index'))


@studies.route('/<orthanc_id>/view')
@login_required 
def view(orthanc_id):
    """ view details of orthanc study """
    study = Study.query.filter(Study.orthanc_id==orthanc_id).filter(Study.exists==True).first()
    if study is None:
        flash('Study ID not found', 'danger')
        redirect(request.referrer or url_for('studies.index'))
    return render_template('studies.view.html',study=study)


@studies.route('/<orthanc_id>/delete')
@login_required 
@admin_required
def delete(orthanc_id):
    """ delete study """
    study = Study.query.filter(Study.orthanc_id==orthanc_id).first()
    if study is None:
        flash('Study ID not found', 'danger')
        redirect(request.referrer)
    
    try:
        study.get().delete()
        db.session.delete(study)
        db.session.commit()
        flash('Successfully deleted study!', 'success')
    except:
        flash('Error deleting study', 'danger')
        db.session.rollback()
        redirect(request.referrer)

    return redirect(url_for('studies.list'))


@studies.route('/<orthanc_id>/assign_to/<research_id>')
@login_required 
def assign_to_person(orthanc_id, research_id):
    """ action: assign orthanc study to person """

    # grab person based on ID
    person = Person.query.filter(Person.research_id==research_id).first()

    # if they don't exist, redirect to person list page
    if person is None:
        flash('Research ID {} not found.', 'warning')
        return redirect(request.referrer or url_for('studies.index'))

    try:
        study = Study(orthanc_id  = orthanc_id,
                      person_id   = person.id)
        db.session.add(study)
        db.session.commit()
    except:
        db.session.rollback()
        flash('Error assigning study to person', 'danger')
    else:
        flash('Study assigned.', 'success')

    # render page
    return redirect(url_for('studies.view', orthanc_id=orthanc_id))


