from flask import Blueprint, render_template, flash, request, redirect, url_for

from bosphorus import cache
from bosphorus.models import db, ResearchID
from orthancpy import Orthanc

main = Blueprint('main', __name__)
orthanc = Orthanc('http://localhost:8042')

@main.route('/')
#@cache.cached(timeout=1000)
def home():
    return redirect(url_for('person.list'))

@main.route('/ids')
def ids():
    ids = ResearchID.query.all()
    return render_template('ids.html', ids=ids)

@main.route('/studies/new')
def studies_new():
    studies  = orthanc.get_new.studies()
    return render_template('studies.html',studies=studies)


