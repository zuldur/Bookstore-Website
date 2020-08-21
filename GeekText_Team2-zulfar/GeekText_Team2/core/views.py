from flask import render_template, request, Blueprint
from flask_login import login_required
from GeekText_Team2.models import Book
from GeekText_Team2.models import User
from GeekText_Team2.models import BlogPost
from GeekText_Team2.blog_posts.forms import BlogPostForm
from GeekText_Team2 import db
from sqlalchemy import func
from GeekText_Team2.models import User

core = Blueprint('core', __name__)

@core.route('/')
def home():
    bestsellers = Book.query.filter(Book.rating <= 4).limit(4).all()
    b1 = bestsellers[0]
    b2 = bestsellers[1]
    b3 = bestsellers[2]
    b4 = bestsellers[3]
    return render_template('home.html', b1=b1, b2=b2, b3=b3, b4=b4)
# @core.route('/')
# def home():
#     bestsellers = Book.query.filter(Book.soldUnits >= 8).limit(4).all()
#     b1 = bestsellers[0]
#     b2 = bestsellers[1]
#     b3 = bestsellers[2]
#     b4 = bestsellers[3]
#     return render_template('home.html', b1=b1, b2=b2, b3=b3, b4=b4)

#@core.route('/')
#def home():
#    bestsellers = Book.query.filter(Book.soldUnits >= 8).limit(4).all()
#    b1 = bestsellers[0]
#    b2 = bestsellers[1]
#    b3 = bestsellers[2]
#    b4 = bestsellers[3]
#    return render_template('home.html', b1=b1, b2=b2, b3=b3, b4=b4)


@core.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html')


@core.route('/info')
def info():
    '''
    Example view of any other "core" page. Such as a info page, about page,
    contact page. Any page that doesn't really sync with one of the models.
    '''
    return render_template('info.html')


@core.route('/index')                            # Main page
def index():
    '''
    This is the home page view. Notice how it uses pagination to show a limited
    number of posts by limiting its query size and then calling paginate.
    '''

    page = request.args.get('page', 1, type=int)
    blog_posts = BlogPost.query.order_by(
        BlogPost.date.desc()).paginate(page=page, per_page=10)
    # Returns an instance of the main page
    # Links to the index template
    return render_template('index.html', blog_posts=blog_posts)
