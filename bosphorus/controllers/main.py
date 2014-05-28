from flask import Blueprint, render_template, request, redirect, url_for

from bosphorus import cache
from bosphorus.models import ResearchID

main = Blueprint('main', __name__)

@main.route('/')
#@cache.cached(timeout=1000)
def home():
    return redirect(url_for('person.list'))

@main.route('/ids')
def ids():
    ids = ResearchID.query.all()
    return render_template('ids.html', ids=ids)


