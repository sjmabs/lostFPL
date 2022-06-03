from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import requests


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

    submit = SubmitField('Post')


class EnterID(FlaskForm):
    league_id = IntegerField('League ID', validators=[DataRequired()])
    amount_owed = IntegerField('Enter the amount a player owes for finishing last for the week',
                               validators=[DataRequired()])
    submit = SubmitField('Get league info')

    def validate_league_id(self, league_id):
        response = requests.get('https://fantasy.premierleague.com/api/leagues-classic/' + str(league_id.data) + "/standings/")
        if (
                response.status_code == 204 or response.status_code == 404
        ):
            raise ValidationError('ID not found. Please choose another.')



