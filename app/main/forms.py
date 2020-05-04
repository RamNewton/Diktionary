from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError
from wtforms import StringField, SubmitField
import re

class SearchForm(FlaskForm):
    word = StringField('Meaning for :', validators=[DataRequired()])
    submit = SubmitField('Search')

    def validate_word(self, word):
        pat = re.compile("^[a-zA-Z-]+$")
        if pat.match(word.data) is None:
            raise ValidationError('Word can contain alphabets only')
    