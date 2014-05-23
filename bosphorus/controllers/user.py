from flask import Blueprint, render_template, flash, request

from bosphorus.models import db, User
from bosphorus.forms import LoginForm

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/')
def home():
    return render_template('user.index.html')

@user.route('/list')
def list():
    users = User.query.all()
    return render_template('user.list.html', users=users)

@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('user.login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            flash("The form was successfully submitted", 'success')
        else:
            flash("There was a problem submitting the form!", 'danger')
        return render_template('user.login.html', form=form)
