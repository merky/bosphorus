from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, DateField
from wtforms import validators

strip_filter = lambda x: x.strip() if x else ''

class LoginForm(Form):
    username = TextField(u'username',     validators=[validators.required()])
    password = PasswordField(u'password', validators=[validators.required()])

def ssn_validator():
    return validators.Regexp('(^\d{3}-?\d{2}-?\d{4}$|^XXX-XX-XXXX$)')

class PersonForm(Form):
    research_id = SelectField(u'Research ID',
                               validators=[validators.required()])
    clinical_id = TextField(u'Clinical ID',
                              validators = [validators.required()],
                              filters = [strip_filter])
    first_name  = TextField(u'First Name',filters=[strip_filter])
    last_name   = TextField(u'Last Name',filters=[strip_filter])
    dob         = DateField(u'Date-of-birth', 
                            validators = [validators.Optional()],
                            format='%m/%d/%Y')
    ssn         = TextField(u'SSN',
                             validators = [ssn_validator(), validators.Optional()],
                             filters = [strip_filter])
