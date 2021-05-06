from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.user import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])

    def validate_email(self, email):
        user = User(email.data)
        if user.exists():
            raise ValidationError('Please use a different email address.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[Email()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
