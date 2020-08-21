# __init__ underneath GeekText_Team2 folder
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_dance.contrib.google import make_google_blueprint,google


login_manager = LoginManager()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Confused3@localhost/geektext'
# '''app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'geektext.sqlite')'''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)
mail = Mail(app)

login_manager.init_app(app)

login_manager.login_view = "users.login"

blueprint = make_google_blueprint(client_id="",client_secret='',offline=True, scope=['profile','email'])


###########################
#### BLUEPRINT CONFIGS #######
#########################
from GeekText_Team2.cart.views import cart_blueprint
from GeekText_Team2.Wishlist.views import wishlist_posts
from GeekText_Team2.blog_posts.views import blog_posts
from GeekText_Team2.books.views import books_blueprint
from GeekText_Team2.users.views import users
from GeekText_Team2.core.views import core
from GeekText_Team2 import models

#from GeekText_Team2.blog_posts.views import blog_posts
#from GeekText_Team2.error_pages.handlers import error_pages

# Register the apps
app.register_blueprint(blueprint,url_prefix='/login')
app.register_blueprint(users)
# app.register_blueprint(blog_posts)
app.register_blueprint(core)
# app.register_blueprint(error_pages)

app.register_blueprint(books_blueprint)
app.register_blueprint(blog_posts)
app.register_blueprint(wishlist_posts)
app.register_blueprint(cart_blueprint)
