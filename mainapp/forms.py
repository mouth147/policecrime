from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired

class main_search(FlaskForm):
    search = StringField(u"Type in a victims name, a location, etc...", validators=[DataRequired()])
    search_by = SelectField(u'Search in', choices = [('victims', 'Victims'), ('location', 'Location')])

class adv_search(FlaskForm):
    race = SelectField(u'Race', choices = []);
    gender = SelectField(u'Gender', choices = []);
    state = SelectField(u'States', choices = []);
    armed = SelectField(u'Armed', choices = []);
    city = StringField(u'Cities')
    classification = SelectField(u'Classification', choices = []);
    min_age = StringField(u'Range of Ages')
    max_age = StringField(u'Range of Ages')
    submit = SubmitField('Submit')

class race_compare(FlaskForm):
    race = SelectMultipleField(u'Races', choices = [], validators=[DataRequired()]);
    submit = SubmitField('Submit')

class weapon_compare(FlaskForm):
    weapons = SelectMultipleField(u'Weapons', choices = [], validators=[DataRequired()]);
    submit = SubmitField('Submit')

class state_compare(FlaskForm):
    states = SelectMultipleField(u'States', choices = []);
    compare_choices = [('violentcrime', 'Violent Crime'), ('gunmurderrate', 'Gun Murder Rate'),
                       ('murder', 'Murder Rate'), ('assault', 'Assault'), ('count', 'Killing Count')]
    compare = SelectMultipleField(u'Comparison', choices = compare_choices, validators=[DataRequired()])
    sort = SelectField(u'Sort By', choices = compare_choices)
    limit = SelectField(u'Limit Results', choices = [(1, '1'), (5, '5'), (10, '10'), (15, '15'),
                                                     (20, '20'), (30, '30'), (40, '40'), (55, '55')])
    submit = SubmitField('Submit')
