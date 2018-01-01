from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm, EditForm, CharacterForm
from .models import User, OAuthSignIn, UserTokens
import ast
from .hednpc import create_char
import app.traits as traits


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    user = g.user
    form = CharacterForm()
    return render_template('index.html',
                           title='Home',
                           user=user,
                           form=form)

@app.route('/character', methods=['GET','POST'])
def character():
    if request.method == 'POST':
        values = {'Namn':request.form.get('name', None),
                  'Yrke':request.form.get('job', None),
                  'nivå_min':request.form.get('lvl_min', None),
                  'nivå_max':request.form.get('lvl_max', None),
                  'Ras':request.form.get('race', None),
                  'Kön':request.form.get('gender', None),
                  'Ålder':request.form.get('age', None),
                  'ålder_min':request.form.get('age_min', None),
                  'ålder_max':request.form.get('age_max', None),
                  'Längd':request.form.get('height', None),
                  'längd_min':request.form.get('height_min', None),
                  'längd_max':request.form.get('height_max', None),
                  'Huvudhand':request.form.get('hand', None)}
        char = create_char(values)
        return render_template('character.html',
                               char=char,
                               title=char.start_values['Namn'])

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/<token>', methods=['GET', 'POST'])
@oid.loginhandler
def login(token=None):
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    session['token'] = token
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return redirect(url_for('oauth_authorize',
                                provider = 'facebook'))
    return render_template('login.html',
                           title='Logga in',
                           form=form)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        if session['token']:
            tokensDB = UserTokens.query.all()
            invited = False
            for t in tokensDB:
                if t.token_string == session['token']:
                    invited = True
                    user = User(social_id=social_id, nickname=username, email=email)
                    db.session.add(user)
                    db.session.commit()
                    session.pop('token', None)
            if not invited:
                flash('Din inbjudan verkar vara ogiltig.')
                return redirect(url_for('index'))
            else:
                invited = False
        else:
            flash('Du måste ha en inbjudan för att kunna logga in.')
            return redirect(url_for('index'))
    login_user(user, True)
    flash('Inloggad')
    return redirect(request.args.get('next') or url_for('index'))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    if not nickname == g.user.nickname:
        flash('Du kan bara se din egen profil.')
        return redirect(url_for('index'))
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('Användare %s hittades inte.' % nickname)
        return redirect(url_for('index'))
    chars = [
        {'creator': user, 'Namn': 'Torkel'},
        {'creator': user, 'Namn': 'Torkla'}
        ]
    return render_template('user.html',
                           user=user,
                           chars=chars)

@app.route('/edituser', methods=['GET', 'POST'])
@login_required
def edituser():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        db.session.add(g.user)
        db.session.commit()
        flash('Ditt användarnamn har ändrats')
        return redirect(url_for('edituser'))
    else:
        form.nickname.data = g.user.nickname
    return render_template('edituser.html', form=form)
    
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
