from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, DateField, BooleanField, TextAreaField
from wtforms.validators import Regexp, Required, Email, Optional, EqualTo

strip_filter = lambda x: x.strip() if x else ''

def ssn_validator():
    return Regexp('(^\d{3}-?\d{2}-?\d{4}$|^XXX-XX-XXXX$)')

class LoginForm(Form):
    username = TextField(u'username',     validators=[Required()])
    password = PasswordField(u'password', validators=[Required()])

class RegisterForm(Form):
    name = TextField('Name', [Required()])
    email = TextField('Email address', [Required()])
    username = TextField('Username', [Required()])
    password = PasswordField('Password', [Required()])
    role_admin = BooleanField('Administrator', [Optional()])
    confirm = PasswordField('Repeat Password', [
                 Required(),
                 EqualTo('password', message='Passwords must match')
              ])

class EditUserForm(Form):
    name = TextField('Name', [Required()])
    email = TextField('Email address', [Required()])
    username = TextField('Username', [Required()])
    password = PasswordField('Password', [Optional()])
    role_admin = BooleanField('Administrator', [Optional()])
    confirm = PasswordField('Repeat Password', [
                 Optional(),
                 EqualTo('password', message='Passwords must match')
              ])

class StudyAssignForm(Form):
    research_id = SelectField(u'Research ID',
                               validators=[Required()])

class PersonSearchForm(Form):
    search = TextField(u'Search', validators=[Required()])

class PersonForm(Form):
    research_id = SelectField(u'Research ID',
                               validators=[Required()])
    clinical_id = TextField(u'Clinical ID',
                              validators = [Required()],
                              filters = [strip_filter])
    first_name  = TextField(u'First Name',filters=[strip_filter])
    last_name   = TextField(u'Last Name',filters=[strip_filter])
    dob         = DateField(u'Date-of-birth', 
                            validators = [Optional()],
                            format='%m/%d/%Y')
    ssn         = TextField(u'SSN',
                             validators = [ssn_validator(), Optional()],
                             filters = [strip_filter])
    notes       = TextAreaField(u'Notes', 
                             validators = [Optional()],
                             filters = [strip_filter])

