from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask import flash
from Controllers.DatabaseController import DatabaseController

class RegistrationForm(FlaskForm):
    
    gebruiker_id = StringField('Gebruiker ID', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    voornaam = StringField('Voornaam', validators=[DataRequired()])
    achternaam = StringField('Achternaam', validators=[DataRequired()])
    rol_id = StringField('Rol ID', validators=[DataRequired()])  # Correcte naamgeving
    password = PasswordField('Wachtwoord', validators=[DataRequired()])
    confirm_password = PasswordField('Bevestig Wachtwoord', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Registreren")

    def validate_gebruiker_id(self, gebruiker_id):  # Correcte validatie
        gebruiker_id = DatabaseController.fetch_by_condition('Gebruiker', gebruiker_id=gebruiker_id)
        if gebruiker_id:
            flash('Gebruiker ID bestaat al', 'danger')
            raise ValidationError('Kies een andere gebruiker ID.')

    def validate_email(self, email):
        email = DatabaseController.fetch_by_condition('Gebruiker', email=Email)
        if email:
            flash('Email bestaat al', 'danger')
            raise ValidationError('Kies een ander emailadres.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Wachtwoord', validators=[DataRequired()])
    remember = BooleanField('Onthoud mij')
    submit = SubmitField("Inloggen")
