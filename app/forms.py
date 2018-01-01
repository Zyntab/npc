from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, RadioField
from wtforms import IntegerField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(Form):
    remember_me = BooleanField('remember_me', default=False)

class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])

class CreateUserForm(Form):
    remember_me = BooleanField('remember_me', default=False)

class CharacterForm(Form):
    name = StringField('Namn', default='*slump*')
    job = RadioField('Yrke', choices=[('Vanlig','Vanlig'),
                                      ('Stridis','Stridis'),
                                      ('Tänkare','Tänkare')],
                     default='Vanlig')
    lvl_min = IntegerField(default=1)
    lvl_max = IntegerField(default=3)
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
                     default='Mogen')
    age_min = IntegerField(default=25)
    age_max = IntegerField(default=50)
    height = RadioField('Längd',
                        choices=[('Kort','Kort'),
                                 ('Medel','Medel'),
                                 ('Lång','Lång'),
                                 ('rng','')],
                        default='Medel')
    height_min = IntegerField(default=160)
    height_max = IntegerField(default=180)
    hand = RadioField('Huvudhand',
                      choices=[('slump','*slumpa*'),
                               ('Högerhänt','Högerhänt'),
                               ('Vänsterhänt','Vänsterhänt'),
                               ('Dubbelhänt','Dubbelhänt')],
                      default='slump')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.age.data == 'rng':
            if int(self.age_min.data) > int(self.age_max.data):
                raise ValidationError(message='Max ålder måste vara större än eller lika med Min ålder.')
        if self.height.data == 'rng':
            if int(self.height_min.data) > int(self.height_max.data):
                   raise ValidationError(message='Max längd måste vara större än eller lika med Min längd.')

class SaveCharForm(Form):
    name = StringField('Namn', validators=[DataRequired()])
    notes = TextAreaField('Anteckningar', validators=[DataRequired()])
    campaign = StringField('Kampanj')

class InviteForm(Form):
    invite_email = StringField(validators=[DataRequired(),
                                           Email(message='Det där var fel')])
