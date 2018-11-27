from flask import render_template, url_for, flash
from flask_mail import Message
from app import app, mail, db
import jwt
from config import ADMINS
from .models import UserTokens
from threading import Thread
from time import time

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

rand_symb = ['a','A','b','B','c','C','d','D','e','E','f','F','g','G',
             'h','H','i','I','j','J','k','K','l','L','m','M','n','N',
             'o','O','p','P','q','Q','r','R','s','S','t','T','u','U',
             'v','V','x','X','y','Y','z','Z','1','2','3','4','5','6',
             '7','8','9','0']

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def invite_user(invite_email, user, expires_in=(60*60*24*7)):
    token = jwt.encode(
        {'invite_email': invite_email, 'exp': time() + expires_in},
        app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    send_email('%s bjuder in dig till NPC-skaparen!' % user.nickname,
               sender = 'npc.zyntabsoft@gmail.com',
               recipients = [invite_email],
               text_body = render_template('invite_email.txt', token=token),
               html_body = render_template('invite_email.html', token=token))

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[NPC - Hed] Återställ lösenord',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('reset_password_email.txt',
                                         user=user, token=token),
               html_body=render_template('reset_password_email.html',
                                         user=user, token=token))