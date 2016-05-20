from app import app, db, lm, oid
from flask import render_template, flash, redirect, url_for, session, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import LoginForm, EditForm, PostForm
from .models import User, Post
from datetime import datetime
from .auth import OAuthSignIn

 # Set up
@lm.user_loader
def load_user(id):
    return User.query.get(id)

@app.before_request
def before_request():
    g.user = current_user
    if g.user is not None and g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))


 ## Routes
@app.route('/indextest')
def indextest():
    return render_template('indextest.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = g.user
    return render_template('index.html',
                            title='Home',
                            user=user)

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    # if already logged in
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    # Try authenticate user
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])

    # no login information available
    return render_template('login.html',
                            title='Sign In',
                            form=form,
                            providers=app.config['OPENID_PROVIDERS'])

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/')
@app.route('/user/<nickname>')
@login_required
def user(nickname = None):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Please login')
        return redirected(url_for('index'))
    posts = Post.query.filter_by(user_id=user.id).order_by('timestamp desc').all()
    return render_template('user.html',
                            title='Profile',
                            user=user,
                            posts = posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    user = g.user
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash("Your Profile has been saved.")
        return redirect(url_for('user', nickname=g.user.nickname))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        return render_template('edit.html',
                            title='Profile Edit',
                            user=user,
                            form=form)

@app.route('/clear')
def clear():
    posts = Post.query.all()
    for post in posts:
        db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

## Error Handler
@app.errorhandler(404)
def not_found_error(error):
    # response = jsonify(error.to_dict())
    # response.status_code = error.status_code
    # return response
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


##########################################################
###### Test OAuth ##################
@app.route('/logintest', methods=['GET', 'POST'])
def logintest():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('logintest.html',
                           title='Sign In')

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    # Flask-Login function
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    username, email = oauth.callback()
    if email is None:
        # I need a valid email address for my user identification
        flash('Authentication failed.')
        return redirect(url_for('index'))
    # Look if the user already exists
    user=User.query.filter_by(email=email).first()
    if not user:
        # Create the user. Try and use their name returned by Google,
        # but if it is not set, split the email address at the @.
        nickname = username
        if nickname is None or nickname == "":
            nickname = email.split('@')[0]

        # We can do more work here to ensure a unique nickname, if you
        # require that.
        user=User(nickname=nickname, email=email)
        db.session.add(user)
        db.session.commit()
    # Log in the user, by default remembering them for their next visit
    # unless they log out.
    login_user(user, remember=True)
    return redirect(url_for('index'))
