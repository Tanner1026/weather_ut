from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Optional, Email

class EmailForm(FlaskForm):
    name = StringField('What is your name? (You may leave blank to remain anonymous)', validators=[Optional()], id='name')
    email = EmailField('What is your email address', validators=[Email()], id='email')
    message = TextAreaField('Message', validators=[DataRequired()], id='message')
    submit = SubmitField()
