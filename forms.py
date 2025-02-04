from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, TextAreaField, validators
from wtforms.validators import DataRequired, Optional, Email
import email_validator

class EmailForm(FlaskForm):
    name = StringField('What is your name? (You may leave this blank to remain anonymous.)', validators=[Optional()], id='name')
    email = EmailField('What is your email address?', validators=[Email()], id='email')
    message = TextAreaField('Message', validators=[DataRequired()], id='message')
    submit = SubmitField()
