from flask import Flask, redirect, url_for, render_template, request, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, current_user
from oauth import OAuthSignIn
from golfparser import get_player_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '##',
        'secret': '##'
    },
}

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    players = db.relationship('Player', backref='user', lazy='dynamic')

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), nullable=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/home')
def home():
    if not current_user.is_authenticated:
        return lm.unauthorized()
    # get all the players currently on the users team
    user = load_user(current_user.get_id())
    players = Player.query.filter_by(user_id = user.id)
    names = [player.name for player in players]  
    print(names)
    return render_template('home.html', active = "home", players = names)
    
def add_player_to_users_team(user, player_name):
    players = Player.query.filter_by(name = player_name)
    for player in players:
        if(player.user_id == None):
            #No one has claimed this player yet
            player.user_id = user.id
            db.session.commit()
            flash("Successfully added player "+ player.name)
        elif(player.user_id == user.id):
            flash(player.name+" is already on your team!")
        else:
            #Player has be claimed, need to create a duplicate player
            duplicate_player = Player()
            duplicate_player.name = player
            duplicate_player.user_id = user.id
            db.session.add(duplicate_player)
            db.session.commit()
            flash("Successfully added player "+ player.name)


@app.route('/add_players', methods=['GET', 'POST'])
def add_players():
    #player selection has occurred
    if not current_user.is_authenticated:
        return lm.unauthorized()
    if request.method == 'POST':
        print(load_user(current_user.get_id()).nickname)
        user = load_user(current_user.get_id())
        for selected_player in request.form:
            #add each selected player to the users db
            if(selected_player != "Submit"):
                add_player_to_users_team(user, selected_player)
    # need to list all the players in the database
    names = [player.name for player in Player.query.all()]        
    return render_template('add_players.html', active = "add_players", players = names)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    print("authorize")
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    print("callback")
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('home'))


def add_all_players():
    player_names = get_player_data()
    print(player_names)
    for i in range(len(player_names)):
        player = Player()
        player.name = player_names[i]
        db.session.add(player)
    db.session.commit()

if __name__ == '__main__':
    #clear_db()
    db.drop_all()
    db.create_all() 
    add_all_players()
    app.run(debug=True)
