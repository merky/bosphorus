from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask.ext.login import login_required
from sqlalchemy import or_

from bosphorus.models import db, Person, ResearchID, Study, ResearchProtocol
from bosphorus.forms  import PersonForm, PersonSearchForm
from bosphorus.utils  import admin_required

person = Blueprint('person', __name__, url_prefix='/person')

def get_research_id(id):
    return ResearchID.query.filter(ResearchID.research_id==id).first()

########################
# List all persons
########################

@person.route('/')
@login_required 
def list():
    """ show list of all persons """
    form = PersonSearchForm(request.form)
    persons = Person.query.all()
    return render_template('person.list.html',persons=persons, searchform=form)

########################
# Search persons
########################

@person.route('/search', methods=['POST'])
@login_required 
def search():
    form = PersonSearchForm(request.form)
    if not form.validate_on_submit():
        flash('Query not valid','warning')
        return redirect(url_for('person.list'))
    return redirect(url_for('person.search_results', query = form.search.data))

@person.route('/search/<query>', methods=['GET'])
@login_required 
def search_results(query):
    """ search persons """
    form = PersonSearchForm(request.form)
    querystr = '%{}%'.format(query)
    persons = Person.query.filter(or_(
                  Person.research_id.like(querystr),
                  Person.clinical_id.like(querystr),
                  Person.first_name.like(querystr),
                  Person.last_name.like(querystr)
              )).all()
    return render_template('person.list.html', persons=persons, query=query, searchform=form)


########################
# View Person
########################

@person.route('/<research_id>/view')
@login_required 
def index(research_id):
    """ view individual person """
    # grab person based on ID
    person = Person.query.filter(Person.research_id==research_id).first()

    # if they don't exist, redirect to person list page
    if person is None: return redirect(url_for('person.list'))

    # render page
    return render_template('person.index.html',person=person)

########################
# Edit Person
########################

@person.route('/<research_id>/edit', methods=['POST','GET'])
@login_required 
def edit(research_id):
    """ edit individual person """
    # grab person based on ID
    person = Person.query.filter(Person.research_id==research_id).first()

    # if they don't exist, redirect to person list page
    if person is None: return redirect(url_for('person.list'))

    # get all available choices for research ID (include current)
    research_ids = ResearchID.query.filter(ResearchID.used==False).all()
    id_choices = [(x.research_id,x.research_id) for x in research_ids]
    id_choices.insert(0,(person.research_id,person.research_id))

    # get all available choices for research protocol
    protocols = ResearchProtocol.query.all()
    protocol_choices = [(x.id,'{} - {}'.format(x.number, x.title)) for x in protocols]
    
    # apply choices to form
    form = PersonForm(request.form, protocols=[x.id for x in person.protocols])
    form.research_id.choices = id_choices
    form.protocols.choices = protocol_choices

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
        #form.populate_obj(person)
        #person.research_id = form.research_id.data
        person.clinical_id = form.clinical_id.data
        person.first_name  = form.first_name.data
        person.last_name   = form.last_name.data
        person.dob         = form.dob.data
        person.ssn         = form.ssn.data
        person.notes       = form.notes.data

        person.protocols   = [ResearchProtocol.query.get(x) for x in form.protocols.data]

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
    else:
        form.notes.data=person.notes

    # render page
    return render_template('person.edit.html',person=person, form=form)

########################
# New Person
########################

@person.route('/new', methods=['POST','GET'])
@login_required 
def new():
    """ create new person """
    # get all available choices for research ID (include current)
    research_ids = ResearchID.query.filter(ResearchID.used==False).all()
    id_choices = [(x.research_id,x.research_id) for x in research_ids]

    # get all available choices for research protocol
    protocols = ResearchProtocol.query.all()
    protocol_choices = [(x.id,'{} - {}'.format(x.number, x.title)) for x in protocols]
    
    # apply choices to form
    form = PersonForm(request.form)
    form.research_id.choices = id_choices
    form.protocols.choices = protocol_choices

    # on form submission
    if form.validate_on_submit():
        # create new person
        person = Person(research_id = form.research_id.data, clinical_id = form.clinical_id.data)
        # grab ResearchID
        rid = ResearchID.query.filter(ResearchID.research_id==form.research_id.data).first()
        # populate person data from form
        person.clinical_id = form.clinical_id.data
        person.first_name  = form.first_name.data
        person.last_name   = form.last_name.data
        person.dob         = form.dob.data
        person.ssn         = form.ssn.data
        person.notes       = form.notes.data
        person.protocols   = [ResearchProtocol.query.get(x) for x in form.protocols.data]

        # before we add, let's do a quick check
        clinical_id_used = Person.query \
                                 .filter(Person.clinical_id==person.clinical_id) \
                                 .count()
        if clinical_id_used:
            flash('Clinical ID already in use!', 'danger')
        else:
            try:
                # add to session
                db.session.add(person)
                # mark the Research ID as being used
                rid.used = True
                # commit new person
                db.session.commit()
            except:
                flash('Unexpected error while creating person', 'danger')
                db.session.rollback()
            else:
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


@person.route('/<research_id>/delete', methods=['GET'])
@login_required 
@admin_required
def delete(research_id):
    """ edit individual person """
    # grab person based on ID
    person = Person.query.filter(Person.research_id==research_id).first()

    # if they don't exist, redirect to person list page
    if person is not None: 
        rid = get_research_id(person.research_id)
        rid.used = False
        db.session.delete(person)
        db.session.merge(rid)
        db.session.commit()
        flash('Person "{}" removed successfully'.format(person.research_id), 'success')

    return redirect(url_for('person.list'))


