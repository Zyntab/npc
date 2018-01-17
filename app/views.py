from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm, EditForm, CharacterForm, InviteForm, SaveCharForm, lvlupForm
from .models import User, OAuthSignIn, UserTokens
import ast
from .hednpc import create_char, load_char, save_char, unique_charname
import app.traits as traits
from .emails import invite_user
from config import ADMINS


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    user = g.user
    form = CharacterForm()
    return render_template('index.html',
                           title='Hem',
                           user=user,
                           form=form)

@app.route('/character', methods=['GET','POST'])
@app.route('/character/<charname>', methods=['GET','POST'])
def character(charname=None):
    form = SaveCharForm()
    if not charname:
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
            session['char'] = char.toDict()
            form.notes.data = session['char']['notes']
            return render_template('character.html',
                                   char=char,
                                   title=char.start_values['Namn'],
                                   form=form)
        else:
            if g.user.is_authenticated:
                flash('Du måste skapa en karaktär eller ladda en sparad.')
            else:
                flash('Du måste skapa en karaktär först.')
            return redirect(url_for('index'))
    else:
        ### kod för att visa sparad karaktär ###
        if g.user.is_authenticated:
            try:
                char = load_char(charname, g.user)
                session['char'] = char.toDict()
                form.notes.data = session['char']['notes']
                return render_template('character.html',
                                       char=char,
                                       title=char.start_values['Namn'],
                                       form=form,
                                       charname=charname)
            except:
                flash('Du verkar inte ha någon karaktär med det namnet')
                return redirect(url_for('index'))
        else:
            ### icke inloggad användare ###
            flash('Du måste skapa en karaktär först')
            return redirect(url_for('index'))

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
                    db.session.delete(t)
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
    chars = user.characters.order_by('timestamp').all()
    return render_template('user.html',
                           title = 'Profil',
                           user=user,
                           chars=chars,
                           lit_eval=ast.literal_eval)

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
    return render_template('edituser.html',
                           title='Ändra namn',
                           form=form)

@app.route('/invite', methods=['GET','POST'])
@login_required
def invite():
    if g.user.is_authenticated and g.user.email in ADMINS:
        form = InviteForm()
        if form.validate_on_submit():
            invite_user(form.invite_email.data, g.user)
            return redirect(url_for('user', nickname=g.user.nickname))
        return render_template('invite.html',
                               title='Bjud in',
                               form=form)
    else:
        flash('Du är inte administratör.')
        return redirect(url_for('index'))

@app.route('/savecharacter', methods=['GET','POST'])
@login_required
def savecharacter():
    ### skillnad om karaktären redan är sparad eller om den är ny ###
    if session['char']['name'] == '':  # inte tidigare sparad
        session['char']['start_values']['Namn'] = request.form.get('name', None)
        session['char']['campaign'] = request.form.get('campaign', None)
        session['char']['notes'] = request.form.get('notes', None)
        char = save_char(session['char'], g.user)
        flash('Karaktären har sparats som "%s".' % char.name)
        return redirect(url_for('character', charname=char.name))
    else:  # tidigare sparad
        c = g.user.characters.filter_by(name=session['char']['name']).first()
        if request.form.get('name', None) != session['char']['start_values']['Namn']:
            start_values = ast.literal_eval(c.start_values)
            start_values['Namn'] = request.form.get('name', None)
            c.start_values = str(start_values)
            c.name = unique_charname(start_values['Namn'].split()[0], g.user)
        if request.form.get('campaign', None) != session['char']['campaign']:
            c.campaign = request.form.get('campaign', None)
        if request.form.get('notes', None) != session['char']['notes']:
            c.notes = request.form.get('notes', None)
        db.session.commit()
        flash('Karaktären har sparats som "%s".' % c.name)
        return redirect(url_for('character', charname=c.name))

@app.route('/confirm_delete/<charname>')
@login_required
def confirm_delete(charname):
    return render_template('confirm_delete.html',
                           title='Bekräfta',
                           charname=charname,
                           session=session)

@app.route('/deletecharacter/<charname>', methods=['GET','POST'])
@login_required
def deletecharacter(charname):
    c = g.user.characters.filter_by(name=charname).first()
    db.session.delete(c)
    db.session.commit()
    flash('Karaktären har raderats.')
    return redirect(url_for('user', nickname=g.user.nickname))

@app.route('/lvlup/<charname>', methods=['GET','POST'])
@login_required
def lvlup(charname):
    user = g.user
    char = load_char(charname, user)
    form = lvlupForm()
    return render_template('lvlup.html',
                           title='Dinga %s' % (char.start_values['Namn']),
                           user=user,
                           char=char,
                           form=form)

@app.route('/ding/<charname>', methods=['GET','POST'])
@login_required
def ding(charname):
    if request.method == 'POST':
        char = load_char(charname, g.user)
        char.ding(request.form.get('levels', None),
                  request.form.get('years', None))
        c = g.user.characters.filter_by(name=charname).first()
        c.start_values = str(char.start_values)
        c.trace_buys = str(char.trace_buys)
        c.points_left = char.points_left
        c.traits = str(char.traits)
        c.skills = str(char.skills)
        c.hitpoints = str(char.hitpoints)
        c.move_carry = str(char.move_carry)
        db.session.commit()
        flash('%s har dingat.' % char.start_values['Namn'])
        return redirect(url_for('character', charname=char.name))
    else:
        flash('Get')
        return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html',
                           title='Om')

@app.route('/aboutHed')
def aboutHed():
    return render_template('aboutHed.html',
                           title='Om Hed')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html',
                           title='Integritetspolicy')

@app.route('/todo')
def todo():
    return render_template('todo.html',
                           title='Kommande')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html',title='Filen hittades inte'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html',title='Oväntat fel'), 500
