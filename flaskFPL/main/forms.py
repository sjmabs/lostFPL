from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError
import requests


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

    submit = SubmitField('Post')


class EnterID(FlaskForm):
    league_id = IntegerField('League ID', validators=[DataRequired()])
    scores_scorers_options = ['Scores - This will run until all lowest scores have been found',
                              "Scorers - This will stop once your number of scorers has been found"]

    scores_scorers = SelectField('Would you like bottom scores or scorers?', choices=scores_scorers_options)

    amount_owed = IntegerField('Enter the amount a player owes for finishing last for the week',
                               default=0)
    amount_owed_2 = IntegerField('Enter the amount a player owes for finishing second last for the week',
                               default=0)
    amount_owed_3 = IntegerField('Enter the amount a player owes for finishing third last for the week',
                               default=0)
    options = ["1", "2", "3"]
    select_one = SelectField(u"How many bottom scorers?", choices=options)

    submit = SubmitField('Get league info')

    def validate_league_id(self, league_id):
        response = requests.get('https://fantasy.premierleague.com/api/leagues-classic/' + str(league_id.data) + "/standings/")
        if (
                response.status_code == 204 or response.status_code == 404
        ):
            raise ValidationError('ID not found. Please choose another.')



