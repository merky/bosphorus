from flask import Blueprint, render_template, flash, request, redirect, url_for

from bosphorus import cache
from bosphorus.models import db, Person, ResearchID, Study
from bosphorus.forms  import PersonForm

person = Blueprint('person', __name__, url_prefix='/person')

def get_research_id(id):
    return ResearchID.query.filter(ResearchID.research_id==id).first()

@person.route('/')
def list():
    """ show list of all persons """
    persons = Person.query.all()
    return render_template('person.list.html',persons=persons)


@person.route('/<research_id>/view')
def index(research_id):
    """ view individual person """
    # grab person based on ID
    person = Person.query.filter(Person.research_id==research_id).first()

    # if they don't exist, redirect to person list page
    if person is None: return redirect(url_for('person.list'))

    # render page
    return render_template('person.index.html',person=person)


@person.route('/<research_id>/edit', methods=['POST','GET'])
def edit(research_id):
    """ edit individual person """
    # grab person based on ID
    person = Person.query.filter(Person.research_id==research_id).first()

    # if they don't exist, redirect to person list page
    if person is None: return redirect(url_for('person.list'))

    # get all available choices for research ID (include current)
    research_ids = ResearchID.query.filter(ResearchID.used==False).all()
    choices = [(x.research_id,x.research_id) for x in research_ids]
    choices.insert(0,(person.research_id,person.research_id))

    # apply choices to form
    form = PersonForm(request.form)
    form.research_id.choices = choices

    # on form submission
    if form.validate_on_submit():
        # grab ResearchID
        rid = get_research_id(form.research_id.data)

        # check if ResearchID was changed
        if rid.research_id != person.research_id:
            # properly mark IDs as used
            # NOTE: this means changes have to occur
            #       within patient DB and XNAT!!!!!!
            #       so, for now, we will not support this.
            flash("Changing of Research ID is currently unsupported", category='danger')
            return render_template('person.edit.html', person=person, form=form)

            # if we were to support this action, we would simply swap
            # the 'used' values of old and new IDs
            old_rid = get_research_id(person.research_id)
            rid.used = True
            old_rid.used = False
            db.session.merge(rid)
            db.session.merge(old_rid)

        # populate person data from form
        form.populate_obj(person)
        # add to session
        db.session.merge(person)
        # commit changes
        db.session.commit()
        # let the person know what's up
        flash('{} modified successfully!'.format(person.research_id), category='success')
        # return to listings
        return redirect(url_for('person.list'))

    elif request.method=='POST':
        # problems with form data
        flash('There were some errors with the form.', category='danger')

    # render page
    return render_template('person.edit.html',person=person, form=form)


@person.route('/new', methods=['POST','GET'])
def new():
    """ create new person """
    # get all available choices for research ID
    research_ids = ResearchID.query.filter(ResearchID.used==False).all()
    id_choices = [(x.research_id,x.research_id) for x in research_ids]

    # apply choices to form
    form = PersonForm(request.form)
    form.research_id.choices = id_choices

    # on form submission
    if form.validate_on_submit():
        # create new person
        person = Person(research_id = form.research_id.data, clinical_id = form.clinical_id.data)
        # grab ResearchID
        rid = ResearchID.query.filter(ResearchID.research_id==form.research_id.data).first()
        # populate person data from form
        form.populate_obj(person)
        # add to session
        db.session.add(person)
        # mark the Research ID as being used
        rid.used = True
        # commit changes
        db.session.merge(rid)
        db.session.commit()
        # let the person know what's up
        flash('Person added successfully!', category='success')
        return redirect(url_for('person.list'))

    elif request.method=='POST':
        # problems with form data
        rid = form.research_id.data
        if rid not in [x.research_id for x in research_ids]:
            flash('The research ID \'{}\' is already in use. Try again.'.format(rid))
        else:
            flash('There were some errors with the form.', category='danger')

    # render page
    return render_template('person.new.html', form=form)


@person.route('/<research_id>/assign/<orthanc_id>')
def assign(research_id, orthanc_id):
    """ assign orthanc study to person """
    # grab person based on ID
    person = Person.query.filter(Person.research_id==research_id).first()

    # if they don't exist, redirect to person list page
    if person is None:
        flash('Research ID {} not found.', category='warning')
        return redirect(url_for('person.list'))

    try:
        study = Study(orthanc_id  = orthanc_id,
                      person_id   = person.id)
        db.session.add(study)
        db.session.commit()
    except:
        db.session.rollback()
        flash('Error assigning study to person')
    else:
        flash('Study assigned.')

    # render page
    return redirect(url_for('person.index',research_id=person.research_id))


