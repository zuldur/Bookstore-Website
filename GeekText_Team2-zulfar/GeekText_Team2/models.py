# models.py under GeekText_Team2 folder
# IMPORT THE DATABASE
from GeekText_Team2 import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
##################################
from numpy import genfromtxt
from time import time
from datetime import datetime, date
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

#############################################
############ DATABASE MODELS ################
#############################################


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(user_id)

############### USER MODEL #############################


class User(db.Model, UserMixin):

    __tablename__ = 'users'  # override tablename
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    profile_image = db.Column(
        db.String(25), nullable=False, default='level_one_geeker.png')
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    address = db.relationship('Address', backref='users')
    payment_info = db.relationship('Payment_Info', backref='users')
    wishlists = db.relationship('Wishlist', backref='users')
    posts = db.relationship('BlogPost', backref='author', lazy=True)
    join_date = db.Column(db.String(20), nullable=False,
                          default=date.today().strftime("%B %d, %Y"))
    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, first_name, last_name, email, username, password, email_confirmation_sent_on=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email_confirmation_sent_on = email_confirmation_sent_on
        self.email_confirmed = False
        self.email_confirmed_on = None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"This is {self.first_name} {self.last_name} with email -> {self.email}"

    def report_address(self):
        print("Addresses for user:")
        for a in self.addresses:
            print(a.address)

########################################################

################## PAYMENT_INFO MODEL ######################


class Payment_Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credit_number = db.Column(db.String(16), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    cardholder = db.Column(db.String(30), nullable=False)
    expiration_date = db.Column(db.String(5), nullable=False)
    csv = db.Column(db.Integer, nullable=False)
    ZIP = db.Column(db.Integer, nullable=False)

    def __init__(self, credit_number, user_id, cardholder, expiration_date, csv, ZIP):
        self.credit_number = credit_number
        self.user_id = user_id
        self.cardholder = cardholder
        self.expiration_date = expiration_date
        self.csv = csv
        self.ZIP = ZIP

########################################################

################## WISHLIST MODEL ######################


class Wishlist(db.Model):

    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    books = db.Column(db.String(13), ForeignKey('books.ISBN'), nullable=True)

    def __init__(self, title, user_id, books):
        self.title = title
        self.user_id = user_id
        self.title = title
        self.books = books

########################################################

############### ADDRESS MODEL #############################


class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    postal_code = db.Column(db.Integer, nullable=False)
    phone_num = db.Column(db.Text, nullable=False)

    def __init__(self, user_id, address, city, state, postal_code, phone_num):
        self.user_id = user_id
        self.address = address
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.phone_num = phone_num

############### BOOK MODEL #############################


class Book(db.Model):

    __tablename__ = 'books'
    author = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.Text, nullable=False)
    ISBN = db.Column(db.String(13), primary_key=True,
                     unique=True, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    publisher = db.Column(db.Text)
    rating = db.Column(db.Numeric(5, 2))
    releaseDate = db.Column(db.Text)
    soldUnits = db.Column(db.Integer)
    title = db.Column(db.Text, nullable=False)

    def __init__(self, author, description, genre, ISBN, releaseDate, price,  rating, image_url, soldUnits, title, publisher):
        self.title = title
        self.author = author
        self.genre = genre
        self.releaseDate = releaseDate
        self.price = price
        self.description = description
        self.rating = rating
        self.image_url = image_url
        self.soldUnits = soldUnits
        self.publisher = publisher


class BlogPost(db.Model):
    # Setup the relationship to the User table
    # Notice the same .relationship was used in the users table.
    users = db.relationship(User)
###################################################################
# [DATABASE(index), user_id(shared with user), date, title, text]
##################################################################
    # Model for the Blog Posts on Website
    # Individual ID for each post
    id = db.Column(db.Integer, primary_key=True)
    # Notice how we connect the BlogPost to a particular author
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False)      # ID of the user'users.id'
    # Date of the post, uses Date API
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Title of the post
    title = db.Column(db.String(140), nullable=False)
    # Text of the post
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.String(140))
    true_private = db.Column(db.String(140))
    book_isbn = db.Column(db.String(140))
# Creating an instance of a blog post

    def __init__(self, title, text, user_id, rating, true_private, book_isbn):
        self.title = title                          # Always done in python
        self.text = text
        self.user_id = user_id
        self.rating = rating
        self.true_private = true_private
        self.book_isbn = book_isbn

    def __repr__(self):                             # representation of each blog post
        return f"Post Id: {self.id} --- Date: {self.date} --- Title: {self.title} --- Rating: {self.rating}"


############### CART MODEL ##################################
class Cart(db.Model):

    __tablename__ = 'cart'
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    ISBN = db.Column(db.String(13), db.ForeignKey('books.ISBN'), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)

################## ORDERS MODEL ################################


class Orders(db.Model):

    __tablename__ = 'orders'
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    ISBN = db.Column(db.String(13), db.ForeignKey('books.ISBN'), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)

############### SAVEDITEMS MODEL ##################################


class SavedItems(db.Model):

    __tablename__ = 'saved_items'
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    ISBN = db.Column(db.String(13), db.ForeignKey('books.ISBN'), nullable=True)
    id = db.Column(db.Integer, primary_key=True)

############### PUBLISHER MODEL #############################
# class Publisher(db.Model):
#
#     __tablename__ = 'publisher'
#
#     publisher_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Text, nullable=False)
#     address = db.Column(db.Text)
#     books = db.relationship('Book', backref='publisher', lazy=True)
#
#     def __init__(self, name, address):
#         self.name = name
#         self.address = address

############################################################


############### AUTHOR MODEL #############################
# class Author(db.Model):

 #   __tablename__ = 'author'

  #  author_id = db.Column(db.Integer, primary_key=True)
   # name = db.Column(db.Text, nullable=False)
    #books = db.relationship('Book', backref='author', lazy=True)

    # def __init__(self, name):
    #   self.name = name
############################################################
