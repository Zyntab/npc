from flask import render_template, url_for, flash
#from flask_mail import Message
from app import app, mail, db
import jwt
from config import ADMINS
from .models import UserTokens
from threading import Thread
from time import time

from googleapiclient.discovery import build
from googleapiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

def get_credentials():
    SCOPES = 'https://www.googleapis.com/auth/gmail.send'

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/home/viktor/Python/flask/npc/app/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service

def send_message(message, user_id='me'):
    service = get_credentials()
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return message
    except errors.HttpError as error:
        flash('An error occurred: %s' % error)

#def send_async_email(app, msg):
#    with app.app_context():
#        mail.send(msg)

#def send_email(subject, sender, recipients, text_body, html_body):
#    msg = Message(subject, sender=sender, recipients=recipients)
#    msg.body = text_body
#    msg.html = html_body
#    Thread(target=send_async_email, args=(app, msg)).start()

def invite_user(invite_email, user, expires_in=(60*60*24*7)):
    token = jwt.encode(
        {'invite_email': invite_email, 'exp': time() + expires_in},
        app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    message = MIMEMultipart('alternative')
    message['to'] = invite_email
    message['from'] = app.config['ADMINS'][0]
    message['subject'] = '{} bjuder in dig till NPC-skaparen'.format(user.nickname)
    body_mime = MIMEText(render_template('invite_email.txt', token=token), 'plain')
    message.attach(body_mime)
    html_mime = MIMEText(render_template('invite_email.html', token=token), 'html')
    message.attach(html_mime)
    raw = {'raw': base64.urlsafe_b64encode(bytes(
                message.as_string(), 'utf-8')).decode('utf-8')}
    send_message(raw)


def send_password_reset_email(user):
    token = user.get_reset_password_token()

    message = MIMEMultipart('alternative')
    message['to'] = user.email
    message['from'] = app.config['ADMINS'][0]
    message['subject'] = '[NPC-skaparen] Återställ lösenord'
    body_mime = MIMEText(render_template('reset_password_email.txt',
                                         user=user, token=token))
    message.attach(body_mime)
    html_mime = MIMEText(render_template('reset_password_email.html',
                                         user=user, token=token))
    raw = {'raw': base64.urlsafe_b64encode(bytes(
            message.as_string(), 'utf-8')).decode('utf-8')}
    send_message(raw)
