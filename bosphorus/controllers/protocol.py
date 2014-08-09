from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask.ext.login import login_required

from bosphorus.models import db, ResearchProtocol
from bosphorus.forms  import ResearchProtocolForm
from bosphorus.utils import admin_required

protocol = Blueprint('protocol', __name__, url_prefix='/protocol')

######################
# Research Protocols
######################

@protocol.route('/add', methods=['GET','POST'])
@login_required 
@admin_required
def add():
    form = ResearchProtocolForm(request.form)

    # on form submission
    if form.validate_on_submit():
        # grab person
        protocol_exists = ResearchProtocol.query. \
                       filter(ResearchProtocol.number==form.number.data).count()
        if protocol_exists:
            flash('Protocol# already exists', 'danger')
            return redirect(request.referrer)

        protocol = ResearchProtocol(number = form.number.data.strip(),
                                    title  = form.title.data.strip(),
                                    description = form.description.data)

        # commit changes
        db.session.add(protocol)
        db.session.commit()

        # let the person know what's up
        flash('Protocol added successfully', 'success')
        return redirect(url_for('protocol.list'))

    elif request.method=='POST':
        # problems with form data
        flash('There were some errors with the form.', 'danger')

    return render_template('protocol.add.html', form=form)


@protocol.route('/all', methods=['GET'])
@login_required 
@admin_required
def list():
    protocols = ResearchProtocol.query.all()
    return render_template('protocol.list.html', protocols=protocols)


@protocol.route('/<protocol_id>/edit', methods=['GET','POST'])
@login_required 
@admin_required
def edit(protocol_id):
    protocol = ResearchProtocol.query.get(protocol_id)
    if not protocol:
        flash('No protocol found.')
        redirect(request.referrer)

    form = ResearchProtocolForm(request.form)

    # on form submission
    if form.validate_on_submit():

	form.populate_obj(protocol)

        # commit changes
        db.session.merge(protocol)
        db.session.commit()

        # let the person know what's up
        flash('Protocol modified successfully', 'success')
        return redirect(url_for('protocol.list'))

    elif request.method=='POST':
        # problems with form data
        flash('There were some errors with the form.', 'danger')

    return render_template('protocol.edit.html', form=form, protocol=protocol)


@protocol.route('/<protocol_id>/delete', methods=['GET'])
@login_required 
@admin_required
def delete(protocol_id):
    protocol = ResearchProtocol.query.get(protocol_id)
    if protocol is not None:
        db.session.delete(protocol)
        db.session.commit()
        flash('Protocol "{}" deleted successfully'.format(protocol.number), 'success')
    return redirect(url_for('protocol.list'))
    

