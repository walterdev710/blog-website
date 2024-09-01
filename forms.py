from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired(), Email(message="Please enter a valid email address with @", granular_message=True)])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=8, message="Password consists of minium 8 characters")])
    submit = SubmitField(label="Sign Me Up")

class LoginForm(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired(), Email(message="Please enter a valid email address with @", granular_message=True)])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Let me in")