from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, EmailField, SubmitField, MultipleFileField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from wtforms.widgets import PasswordInput


class RegistrationForm(FlaskForm):
    username = StringField(label=('Username'),
                           validators=[DataRequired(message='*Required'),
                                       Length(min=2, max=64, message='Your username should contain %(min)d - %(max)d characters.')])
    email = StringField(label=('Email'),
                        validators=[DataRequired(message='*Required'),
                                    Email(),
                                    Length(max=120)])
    password = PasswordField(label=('Password'), widget=PasswordInput(hide_value=False),
                             validators=[DataRequired(message='*Required'),
                                         Length(min=8, message='Password should be at least %(min)d characters long.')])
    confirm_password = PasswordField(
        label=('Confirm Password'), widget=PasswordInput(hide_value=False),
        validators=[DataRequired(message='*Required'),
                    EqualTo('password', message='Both password fields must be equal!')])
    profile_pic = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Only jpg and png can be uploaded.')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    next = HiddenField()
    submit = SubmitField('Log In')

class ChangeLoginForm(FlaskForm):
    username = StringField('New Username', validators=[Optional(), Length(min=2, max=64)])
    email = EmailField('New Email', validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    submit = SubmitField('Update')

class AddSpaceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    address = StringField('Address', validators=[Optional(), Length(max=120)])
    description = StringField('Description', validators=[Optional(), Length(min=2, max=300)])
    photos = MultipleFileField('Photos',
                            validators=[FileAllowed(['jpg', 'png'], 'Only jpg and png can be uploaded.')])
    submit = SubmitField('Add Space')

class RatingForm(FlaskForm):
    cleanliness = IntegerField('Cleanliness', validators=[DataRequired(), NumberRange(min=1, max=5)])
    facilities = IntegerField('Facilities', validators=[DataRequired(), NumberRange(min=1, max=5)])
    accessibility = IntegerField('Accessibility', validators=[DataRequired(), NumberRange(min=1, max=5)])
    natural_diversity = IntegerField('Natural Diversity', validators=[DataRequired(), NumberRange(min=1, max=5)])
    eco_friendly_practices = IntegerField('Eco-friendly Practices', validators=[DataRequired(), NumberRange(min=1, max=5)])
    safety_security = IntegerField('Safety and Security', validators=[DataRequired(), NumberRange(min=1, max=5)])
    recreational_opportunities = IntegerField('Recreational Opportunities', validators=[DataRequired(), NumberRange(min=1, max=5)])
    community_engagement = IntegerField('Community Engagement', validators=[DataRequired(), NumberRange(min=1, max=5)])
    educational_value = IntegerField('Educational Value', validators=[DataRequired(), NumberRange(min=1, max=5)])
    scenic_beauty = IntegerField('Scenic Beauty', validators=[DataRequired(), NumberRange(min=1, max=5)])
    text = StringField('Rating Text', validators=[Length(max=300)])
    space_id = HiddenField('Space ID')
    submit = SubmitField('Submit')