from flask import Flask, render_template, redirect, flash, request, url_for
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_login import login_user, logout_user, login_required, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_bootstrap import Bootstrap


app = Flask(__name__)
bootstrap = Bootstrap(app)

DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_SERVER = os.environ.get('DATABASE_SERVER') or 'localhost'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://' + DATABASE_USER + ':' + \
    DATABASE_PASSWORD + '@' + DATABASE_SERVER + '/mapping_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Mapping(db.Model):
    __tablename__ = 'codemapping'
    legacy = db.Column(db.String(10), nullable=False, primary_key=True)
    new = db.Column(db.String(10), nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AddNewMappingForm(FlaskForm):
    legacy = StringField('Legacy Code', validators=[DataRequired(), Length(1, 10)])
    new = StringField('New Code', validators=[DataRequired(), Length(1, 10)])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me signed in')
    submit = SubmitField('Sign In')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Mapping=Mapping, User=User)

def add_mapping_to_db(legacy, new):
    db.session.add(Mapping(legacy=legacy, new=new))
    db.session.commit()

def load_mappings():
    codes = Mapping.query.all()
    return [[code.legacy, code.new] for code in codes]

def code_exists(legacy):
    code = Mapping.query.filter_by(legacy=legacy).first()
    return bool(code)

@app.route('/')
def index():
    mapping_list = load_mappings()
    MAX_NUM_RESULTS = 20
    return render_template('index.html', 
            mapping_list=mapping_list, max_num_results=MAX_NUM_RESULTS)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/new_mapping', methods=['GET', 'POST'])
@login_required
def new_mapping():
    form = AddNewMappingForm()
    if form.validate_on_submit():
        legacy = form.legacy.data
        new = form.new.data
        if code_exists(legacy):
            flash(f'Legacy code {legacy} already exists.'.format(legacy))
        else:
            add_mapping_to_db(legacy, new)
            msg = f'Added new mapping {legacy}-{new}'.format(legacy, new)
            flash(msg)
            form.legacy.data = ''
            form.new.data = ''
    return render_template('new_mapping.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()
