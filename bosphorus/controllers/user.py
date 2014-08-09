from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import check_password_hash, generate_password_hash

from bosphorus.models import db, User, ROLE_ADMIN
from bosphorus.forms import LoginForm, RegisterForm, EditUserForm
from bosphorus.utils import admin_required
from bosphorus import lm

user = Blueprint('user', __name__, url_prefix='/user')


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@user.route('/profile')
def current_home():
    return redirect(url_for('user.home',username=current_user.username))

@user.route('/<username>/profile')
@login_required 
def home(username):
    if username != current_user.username:
        if not current_user.is_admin():
            return redirect(url_for('main.home'))
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('user.list'))
    return render_template('user.index.html', user=user)


@user.route('/list')
@login_required
@admin_required
def list():
    users = User.query.all()
    return render_template('user.list.html', users=users)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))


@user.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_active():
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful! Welcome, %s." % current_user.name, 'success')
            return redirect(request.args.get('next') or url_for('main.home'))
        else:
            flash('Wrong email or password', 'error')
    return render_template('user.login.html', form=form)

# delete user
@user.route('<username>/delete', methods=['GET'])
@login_required 
@admin_required
def delete(username):
    if username=='admin':
        flash('Cannot remove user \'admin\'', 'warning')
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User \'{}\' removed.'.format(username), 'success')
    else:
        flash('User does not exist', 'warning')
    return redirect(url_for('user.list'))


# add user
@user.route('/add', methods=['GET', 'POST'])
@login_required 
@admin_required
def add():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user_already_exist = User.query.filter_by(username=form.username.data.lower()).first()
        if user_already_exist:
            flash('Username already exists', 'danger')
            return render_template("user.add.html", form=form)

        # create an user instance not yet stored in the database
        user = User(name=form.name.data, 
                    username=form.username.data.lower(),
                    email=form.email.data.lower(),
                    password=generate_password_hash(form.password.data))
        
        if form.role_admin.data:
            user.role = ROLE_ADMIN

        # Insert the record in our database and commit it
        try:
            db.session.add(user)
            db.session.commit()
            flash('User added successfully!')
        except:
            db.session.rollback()
            flash('Unable to add user.', 'danger')

        # redirect user to the 'home' method of the user module.
        return redirect(url_for('user.list'))
    return render_template("user.add.html", form=form)


# edit user
@user.route('/<username>/edit', methods=['GET', 'POST'])
@login_required 
def edit(username):
    if current_user.username != username and not current_user.is_admin():
        return redirect(url_for('user.home', username=username))
    user = User.query.filter_by(username=username).first()
    if not user: 
        return redirect(url_for('user.home',username=username))

    form = EditUserForm(request.form)
    if form.validate_on_submit():
        # create an user instance not yet stored in the database
        if username != form.username.data.lower():
	    user_already_exist = User.query.filter_by(username=form.username.data.lower()).first()
	    if user_already_exist:
	        flash('Username already exists', 'danger')
	        return render_template("user.edit.html", form=form, user=user)

        user.name=form.name.data 
        user.username=form.username.data.lower()
        user.email=form.email.data.lower()
        if len(form.password.data):
            user.password=generate_password_hash(form.password.data)
        if form.role_admin.data:
            user.role = ROLE_ADMIN
        # Insert the record in our database and commit it
        try:
            db.session.add(user)
            db.session.commit()
            flash('User edited successfully!')
        except:
            db.session.rollback()
            flash('Unable to edit user', 'danger')

        # redirect user to the 'home' method of the user module.
        return redirect(url_for('user.home', username=user.username))

    return render_template("user.edit.html", form=form, user=user)

