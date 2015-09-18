from wtforms import Form, BooleanField, StringField, validators
from wtforms import SelectMultipleField, SelectField, Label

class ProjectForm(Form):
    name = StringField('Name', [validators.Length(max=30, min=4), validators.InputRequired()])
    repositories = SelectMultipleField('Repos', [validators.InputRequired()])


class ProjectLabelsForm(Form):
    labels = SelectMultipleField('Labels', [validators.InputRequired()])


class ProjectIssueForm(Form):
    title = StringField('Title', [validators.Length(max=30, min=4), validators.InputRequired()])
    body = StringField('Description', [validators.Length(max=1000, min=4), validators.InputRequired()])
    label = StringField('Label')
    repository = SelectField('Repository', [validators.InputRequired()])


class ProjectMemberForm(Form):
    members = SelectMultipleField('Members', [validators.InputRequired()])
