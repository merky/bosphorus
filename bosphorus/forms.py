from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, DateField
from wtforms import validators

class LoginForm(Form):
    username = TextField(u'username',     validators=[validators.required()])
    password = PasswordField(u'password', validators=[validators.required()])


def date_validator():
    return validators.Regexp('(^\d{3}-?\d{2}-?\d{4}$|^XXX-XX-XXXX$)')

class PersonForm(Form):
    research_id = SelectField(u'Research ID', validators=[validators.required()])
    clinical_id = TextField(u'Clinical ID', validators=[validators.required()])
    first_name  = TextField(u'First Name')
    last_name   = TextField(u'Last Name')
    dob         = DateField(u'Date-of-birth', 
                            validators = [validators.Optional()],
                            format='%m/%d/%Y')
    ssn         = TextField(u'SSN', validators = [date_validator(),
                                                  validators.Optional()])
