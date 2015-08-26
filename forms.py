from wtforms import Form, BooleanField, StringField, validators
from wtforms import SelectMultipleField

class ProjectForm(Form):
    name = StringField('Name', [validators.Length(max=30, min=4), validators.InputRequired()])
    repositories = SelectMultipleField('Repos', [validators.InputRequired()])

class ProjectLabelsForm(Form):
    labels = SelectMultipleField('Labels', [validators.InputRequired()])
