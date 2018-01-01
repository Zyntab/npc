from flask import render_template, url_for, flash
from flask_mail import Message
from app import mail, db
import random
from config import ADMINS
from .models import UserTokens

rand_symb = ['a','A','b','B','c','C','d','D','e','E','f','F','g','G',
             'h','H','i','I','j','J','k','K','l','L','m','M','n','N',
             'o','O','p','P','q','Q','r','R','s','S','t','T','u','U',
             'v','V','x','X','y','Y','z','Z','1','2','3','4','5','6',
             '7','8','9','0']

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def invite_user(invite_email, user):
    token_string = ''
    for i in range(20):
        token_string += random.choice(rand_symb)
    usertoken = UserTokens(token_string=token_string)
    db.session.add(usertoken)
    db.session.commit()
    create_url = url_for('login', token=token_string, _external=True)
    index_url = url_for('index', _external=True)
    send_email('%s bjuder in dig till NPC-skaparen!' % user.nickname,
               'npc.zyntabsoft@gmail.com',
               invite_email.split(),
               render_template('invite_email.txt',
                               create_url=create_url,
                               index_url=index_url),
               render_template('invite_email.html',
                               create_url=create_url,
                               index_url=index_url))
