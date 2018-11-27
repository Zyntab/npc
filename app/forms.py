from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, RadioField, PasswordField
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, \
    NumberRange, ValidationError, EqualTo
import jwt
from app import app

def checkMaxLvl(form, field):
    try:
        if field.data < form.lvl_min.data:
            raise ValidationError('Max får inte vara mindre än min')
    except:
        pass

def checkAge(form, field):
    if field.data == 'rng':
        if form.age_min.data > form.age_max.data:
            raise ValidationError('Max får inte vara mindre än min')

def checkHeight(form, field):
    if field.data == 'rng':
        if form.height_min.data > form.height_max.data:
            raise ValidationError('Max får inte vara mindre än min')

def checkPositive(form, field):
    if field.data < 2:
        raise ValidationError('Får inte vara mindre än 2')

class RegistrationForm(FlaskForm):
    nickname = StringField('Användarnamn', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Lösenord', validators=[DataRequired()])
    password2 = PasswordField('Lösenord igen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrera')

#    def validate_email(self, token):
#        invite_email = jwt.decode(token, app.config['SECRET_KEY'],
#                                  algorithms=['HS256'])['invite_email']
#        if invite_email != self.email.data:
#            raise ValidationError('Du måste använda samma email som inbjudan skickades till.')


class LoginForm(FlaskForm):
    nickname = StringField('Användarnamn', 
                           validators=[DataRequired(message='Får inte vara tomt')])
    password = PasswordField('Lösenord', 
                             validators=[DataRequired(message='Får inte vara tomt')])
    remember_me = BooleanField('Kom ihåg mig', default=False)
    submit = SubmitField('Logga in')

class EditForm(FlaskForm):
    nickname = StringField('nickname',
                           validators=[DataRequired(message='Får inte vara tomt')])
    submit = SubmitField('Spara')

class CreateUserForm(FlaskForm):
    remember_me = BooleanField('remember_me', default=False)

class CharacterForm(FlaskForm):
    name = StringField('Namn',
                       default='*slump*',
                       validators=[DataRequired(message='Får inte vara tomt')])
    job = RadioField('Yrke', choices=[('Vanlig','Vanlig'),
                                      ('Stridis','Stridis'),
                                      ('Tänkare','Tänkare')],
                     default='Vanlig')
    lvl_min = IntegerField(default=1,
                           validators=[NumberRange(min=1,
                                                   message='Min måste vara minst 1')])
    lvl_max = IntegerField(default=3,
                           validators=[NumberRange(min=1,
                                                   message='Max måste vara minst 1'),
                                       checkMaxLvl])
    race = RadioField('Ras',
                      choices=[('Människa','Människa'),
                               ('Gôr','Gôr')],
                      default='Människa')
    gender = RadioField('Kön',
                        choices=[('slump','*slumpa*'),
                                 ('Man','Man'),
                                 ('Kvinna','Kvinna')],
                        default='slump')
    age = RadioField('Ålder',
                     choices=[('Ung','Ung'),
                              ('Mogen','Mogen'),
                              ('Medel','Medel'),
                              ('Gammal','Gammal'),
                              ('Åldring','Åldring'),
                              ('rng','')],
                     default='Mogen',
                     validators=[checkAge])
    age_min = IntegerField(default=25, validators=[NumberRange(min=1,
                                                               message='Måste vara minst 1')])
    age_max = IntegerField(default=50, validators=[NumberRange(min=1,
                                                               message='Måste vara minst 1')])
    height = RadioField('Längd',
                        choices=[('Kort','Kort'),
                                 ('Medel','Medel'),
                                 ('Lång','Lång'),
                                 ('rng','')],
                        default='Medel',
                        validators=[checkHeight])
    height_min = IntegerField(default=160, validators=[NumberRange(min=1,
                                                                   message='Måste vara minst 1')])
    height_max = IntegerField(default=180, validators=[NumberRange(min=1,
                                                                   message='Måste vara minst 1')])
    hand = RadioField('Huvudhand',
                      choices=[('slump','*slumpa*'),
                               ('Högerhänt','Högerhänt'),
                               ('Vänsterhänt','Vänsterhänt'),
                               ('Dubbelhänt','Dubbelhänt')],
                      default='slump')
    submit = SubmitField('Skapa karaktär')

class SaveCharForm(FlaskForm):
    name = StringField('Namn',
                       validators=[DataRequired(message='Får inte vara tomt')])
    notes = TextAreaField('Anteckningar')
    campaign = StringField('Kampanj')
    submit = SubmitField('Spara')

class InviteForm(FlaskForm):
    invite_email = StringField(validators=[DataRequired(message='Du måste skriva in en adress'),
                                           Email(message='Det verkar inte vara en mailaddress')])

class lvlupForm(FlaskForm):
    levels = IntegerField(default=0,
                          validators=[NumberRange(min=0,
                                                  message='Får inte vara mindre än 0')])
    years = IntegerField(default=0,
                         validators=[NumberRange(min=0,
                                                 message='Får inte vara mindre än 0')])

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Skicka')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Lösenord', validators=[DataRequired()])
    password2 = PasswordField('Lösenord igen', validators=[DataRequired(),
                                                           EqualTo('password')])
    submit = SubmitField('Ändra lösenordet')