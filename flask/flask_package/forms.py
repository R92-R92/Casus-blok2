from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, length, Email, EqualTo, ValidationError
from flask import flash
from flask_package.models import User

class RegistrationForm(FlaskForm):
	Gebruiker_id = StringField('Gebruiker id', validators=[DataRequired(), length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	voornaam = StringField('Voornaam', validators=[DataRequired()])
	achternaam = StringField('Achternaam', validators=[DataRequired()])
	password = PasswordField('Password', validators = [DataRequired()])
	roll_id = StringField('Roll id', validators=[DataRequired()])
	confirm_password = PasswordField('confirm_password',
		validators = [DataRequired(), EqualTo('password')])

	submit = SubmitField("Sign up")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			flash('Username already exists')
			raise ValidationError()

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			flash('Email already exists')
			raise ValidationError()


class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('remember Me')
	submit = SubmitField("Log In")
