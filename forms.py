from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField,RadioField,SelectField,SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError,URL
from sqlalchemy import create_engine
engine = create_engine('oracle://dhairya:dhai7735@localhost/orcl')

class RegistrationForm(FlaskForm):
    firstname = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
   

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterAlbum(FlaskForm):
    AlbumName = StringField('Album Name',
                        validators=[DataRequired()])
    YearOfRelease = IntegerField('Year Of Release',
                        validators=[DataRequired()])
    Image = StringField('Image Url',
                        validators=[DataRequired(),URL()])
    submit = SubmitField('Register')

class RegisterArtist(FlaskForm):
    ArtistName = StringField('Artist Name',
                        validators=[DataRequired()])
    Gender = RadioField('Gender', choices = [('M','Male'),('F','Female')])
    Image = StringField('Image Url',
                        validators=[DataRequired(),URL()])
    submit = SubmitField('Register')


class AddSongs(FlaskForm):
    SongName = StringField('Song Name',
                        validators=[DataRequired()])
    Language = StringField('Language',
                        validators=[DataRequired()])
    Duration = IntegerField('Duration',
                        validators=[DataRequired()])
    AlbumName = SelectField('Album Name',
                        choices=[])
    ArtistName = SelectMultipleField('Artist Name',
                        choices=[])
    SongURL = StringField('Song Url',
                        validators=[DataRequired(),URL()])
    submit = SubmitField('Add')


class UpdateForm(FlaskForm):
    firstname = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])  
    oldpassword = PasswordField('Old Password', validators=[DataRequired()])
    newpassword = PasswordField('New Password',
                                     validators=[DataRequired()])
    submit = SubmitField('Save')
