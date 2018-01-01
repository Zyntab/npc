from app import db
import ast
from flask_login import UserMixin
from flask import url_for, current_app, request, redirect, session
from rauth import OAuth2Service
from config import OAUTH_CREDENTIALS
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), unique=True)
    nickname = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    user_type = db.Column(db.String(5), index=True)
    characters = db.relationship('Character', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)

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

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = 'facebook' #provider_name
        credentials = OAUTH_CREDENTIALS[provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name = 'facebook',
            client_id = self.consumer_id,
            client_secret = self.consumer_secret,
            authorize_url = 'https://graph.facebook.com/oauth/authorize',
            access_token_url = 'https://graph.facebook.com/oauth/access_token',
            base_url = 'https://graph.facebook.com'
            )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            info_fields='email, first_name',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data = {'code': request.args['code'],
                    'grant_type': 'authorization_code',
                    'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        me = oauth_session.get('me?fields=id,email,first_name').json()
        return (
            'facebook$' + me['id'],
            me.get('first_name'),
            me.get('email')
        )

class TwitterSignIn(OAuthSignIn):
    pass

