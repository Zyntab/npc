from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, EditForm, CharacterForm, InviteForm, \
    SaveCharForm, lvlupForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from .models import User, UserTokens
import ast
from .hednpc import create_char, load_char, save_char, unique_charname
import app.traits as traits
from .emails import invite_user, send_password_reset_email
from config import ADMINS
from werkzeug.urls import url_parse
import jwt


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    user = g.user
    form = CharacterForm()
    if form.validate_on_submit():
        session['create_values'] = request.form
        return redirect(url_for('character'))
    else:
        return render_template('index.html',
                               title='Hem',
                               user=user,
                               form=form)

@app.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    try:
        invite_email = jwt.decode(token, app.config['SECRET_KEY'],
                        algorithm='HS256')['invite_email']
    except:
        flash('Ogiltig länk. Har det gått mer än en vecka sedan du fick inbjudan?')
        return redirect(url_for('index'))
    form = RegistrationForm()
    form.email.data = invite_email
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Grattis! Du är nu registrerad som användare.')
        return redirect(url_for('login'))
    return render_template('register.html',
                           title='Skapa konto',
                           form=form)

@app.route('/character', methods=['GET','POST'])
@app.route('/character/<charname>', methods=['GET','POST'])
def character(charname=None):
    form = SaveCharForm()
    if not charname:
        if session['create_values']:
            values = {'Namn':session['create_values']['name'],
                      'Yrke':session['create_values']['job'],
                      'nivå_min':session['create_values']['lvl_min'],
                      'nivå_max':session['create_values']['lvl_max'],
                      'Ras':session['create_values']['race'],
                      'Kön':session['create_values']['gender'],
                      'Ålder':session['create_values']['age'],
                      'ålder_min':session['create_values']['age_min'],
                      'ålder_max':session['create_values']['age_max'],
                      'Längd':session['create_values']['height'],
                      'längd_min':session['create_values']['height_min'],
                      'längd_max':session['create_values']['height_max'],
                      'Huvudhand':session['create_values']['hand']}
            char = create_char(values)
            session['char'] = char.toDict()
            form.notes.data = session['char']['notes']
            if form.validate_on_submit():
                session['char']['start_values']['Namn'] = request.form.get('name',None)
                session['char']['campaign'] = request.form.get('campaign',None)
                session['char']['notes'] = request.form.get('notes',None)
                return redirect(url_for('savecharacter'))
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
                if form.validate_on_submit():
                    session['char']['new_name'] = request.form.get('name',None)
                    session['char']['campaign'] = request.form.get('campaign',None)
                    session['char']['notes'] = request.form.get('notes',None)
                    return redirect(url_for('savecharacter'))
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
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Felaktigt användarnamn eller lösenord.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',
                           title='Logga in',
                           form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Kolla din mail för instruktioner om hur du återställer ditt lösenord.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Återställ lösenord',
                           form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Ogiltig länk. Har det gått mer än 10 minuter? ')
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ditt lösenord har ändrats.')
        return redirect(url_for('login'))
    return render_template('reset_password.html',
                           title='Återställ lösenord',
                           form=form)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

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
    if user.email in app.config['ADMINS']:
        is_admin = True
    return render_template('user.html',
                           title = 'Profil',
                           user=user,
                           chars=chars,
                           lit_eval=ast.literal_eval,
                           is_admin=is_admin)

@app.route('/edituser', methods=['GET', 'POST'])
@login_required
def edituser():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        db.session.add(g.user)
        db.session.commit()
        flash('Ditt användarnamn har ändrats')
        return redirect(url_for('user', nickname=g.user.nickname))
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
        char = save_char(session['char'], g.user)
        flash('Karaktären har sparats som "%s".' % char.name)
        return redirect(url_for('character', charname=char.name))
    else:  # tidigare sparad
        c = g.user.characters.filter_by(name=session['char']['name']).first()
        if session['char']['new_name'] != session['char']['start_values']['Namn']:
            start_values = ast.literal_eval(c.start_values)
            start_values['Namn'] = session['char']['new_name']
            c.start_values = str(start_values)
            c.name = unique_charname(start_values['Namn'].split()[0], g.user)
        c.campaign = session['char']['campaign']
        c.notes = session['char']['notes']
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
    if form.validate_on_submit():
        levels = request.form.get('levels',None)
        years = request.form.get('years',None)
        token = '%s-%s-%s' % (charname, levels, years)
        return redirect(url_for('ding', dingtoken=token))
    return render_template('lvlup.html',
                           title='Dinga %s' % (char.start_values['Namn']),
                           user=user,
                           char=char,
                           form=form)

@app.route('/ding/<dingtoken>', methods=['GET','POST'])
@login_required
def ding(dingtoken):
    charname, levels, years = dingtoken.split('-')
    char = load_char(charname, g.user)
    char.ding(levels, years)
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
