from app import db, app
import ast
from flask_login import UserMixin
from flask import url_for, current_app, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    user_type = db.Column(db.String(5), index=True)
    password_hash = db.Column(db.String(128))
    characters = db.relationship('Character', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithm='HS256')['reset_password']
        except:
            return
        return User.query.get(id)

class UserTokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token_string = db.Column(db.String(20), unique=True, index=True)

    def __repr__(self):
         return '<Token_string %r>' % (self.token_string)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_users = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime)
    trace_buys = db.Column(db.String())
    name = db.Column(db.String(), index=True)
    start_values = db.Column(db.String(200))
    weights = db.Column(db.String(300))
    traits = db.Column(db.String(420))
    points_left = db.Column(db.Integer)
    skills = db.Column(db.String(700))
    hitpoints = db.Column(db.String(350))
    move_carry = db.Column(db.String(400))
    campaign = db.Column(db.String())
    notes = db.Column(db.String())

    def __repr__(self):
        return '<Character %r>' % self.name

    def make_unique_charname(self, charname, user):
        chars = user.characters.all()
        if charname not in chars:
            return charname
        version = 2
        while True:
            new_charname = charname + str(version)
            if new_charname not in chars:
                break
            version += 1
        return new_charname

