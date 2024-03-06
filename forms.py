from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, EmailField, SubmitField, MultipleFileField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from wtforms.widgets import PasswordInput


class RegistrationForm(FlaskForm):
    username = StringField(label=('Benutzername'),
                           validators=[DataRequired(message='*Erforderlich'),
                                       Length(min=2, max=64, message='Der Benutzername sollte %(min)d - %(max)d Zeichen enthalten.')])
    email = StringField(label=('E-Mail'),
                        validators=[DataRequired(message='*Erforderlich'),
                                    Email(),
                                    Length(max=120)])
    password = PasswordField(label=('Passwort'), widget=PasswordInput(hide_value=False),
                             validators=[DataRequired(message='*Erforderlich'),
                                         Length(min=8, message='Das Passwort sollte mindestens %(min)d Zeichen lang sein.')])
    confirm_password = PasswordField(
        label=('Passwort bestätigen'), widget=PasswordInput(hide_value=False),
        validators=[DataRequired(message='*Erforderlich'),
                    EqualTo('password', message='Beide Passwortfelder müssen gleich sein!')])
    profile_pic = FileField('Profilbild', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Nur jpg, jpeg und png können hochgeladen werden.')])
    submit = SubmitField('Registrieren')

class LoginForm(FlaskForm):
    email = EmailField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    next = HiddenField()
    submit = SubmitField('Anmelden')

class ChangeLoginForm(FlaskForm):
    username = StringField('Neuer Benutzername', validators=[Optional(), Length(min=2, max=64)])
    email = EmailField('Neue E-Mail', validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField('Neues Passwort', validators=[Optional(), Length(min=8)])
    submit = SubmitField('Aktualisieren')

class AddSpaceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    address = StringField('Adresse', validators=[Optional(), Length(max=120)])
    description = StringField('Beschreibung', validators=[Optional(), Length(min=2, max=300)])
    photos = MultipleFileField('Fotos',
                            validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Nur jpg, jpeg und png können hochgeladen werden.')])
    submit = SubmitField('Grünanlage hinzufügen')

class RatingForm(FlaskForm):
    cleanliness = IntegerField('Sauberkeit', validators=[DataRequired(), NumberRange(min=1, max=5)])
    facilities = IntegerField('Ausstattung', validators=[DataRequired(), NumberRange(min=1, max=5)])
    accessibility = IntegerField('Zugänglichkeit', validators=[DataRequired(), NumberRange(min=1, max=5)])
    natural_diversity = IntegerField('Natürliche Vielfalt', validators=[DataRequired(), NumberRange(min=1, max=5)])
    eco_friendly_practices = IntegerField('Umweltfreundlichkeit', validators=[DataRequired(), NumberRange(min=1, max=5)])
    safety_security = IntegerField('Sicherheit', validators=[DataRequired(), NumberRange(min=1, max=5)])
    recreational_opportunities = IntegerField('Freizeitmöglichkeiten', validators=[DataRequired(), NumberRange(min=1, max=5)])
    community_engagement = IntegerField('Gemeinschaftsengagement', validators=[DataRequired(), NumberRange(min=1, max=5)])
    educational_value = IntegerField('Bildungswert', validators=[DataRequired(), NumberRange(min=1, max=5)])
    scenic_beauty = IntegerField('Landschaftliche Schönheit', validators=[DataRequired(), NumberRange(min=1, max=5)])
    text = StringField('Bewertungstext', validators=[Length(max=1500)])
    space_id = HiddenField('Space ID')
    submit = SubmitField('Grünanlage hinzufügen')
