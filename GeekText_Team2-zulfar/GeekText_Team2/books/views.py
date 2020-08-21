from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from GeekText_Team2 import db
from sqlalchemy import func
from GeekText_Team2.models import Book
from GeekText_Team2.models import BlogPost
from GeekText_Team2.blog_posts.forms import BlogPostForm
from GeekText_Team2.models import User
from GeekText_Team2.models import Cart
from GeekText_Team2.models import Orders
from sqlalchemy import desc

books_blueprint = Blueprint(
    'books', __name__, template_folder='templates/books')


@books_blueprint.route('/books/all')
def list():
    stop_pagination = False
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by')
    descending = request.args.get('desc')

    if descending:
        books = Book.query.order_by(
            desc(sort_by)).paginate(page=page, per_page=12)
    else:
        books = Book.query.order_by(sort_by).paginate(page=page, per_page=12)

    raw_genres = Book.query.with_entities(
        Book.genre).group_by(Book.genre).all()
    genres = []

    for word in raw_genres:
        word = str(word)
        word = (word).replace('(', '').replace(')',
                                               '').replace('\'', '').replace(',', '')
        genres.append(word)

    return render_template('new_browse.html', books=books, genres=genres, stop_pagination=stop_pagination)

    return render_template('new_browse.html', books=books, genres=genres, stop_pagination=stop_pagination)


@books_blueprint.route('/books/genre')
def genre():
    page = request.args.get('page', 1, type=int)
    genre = request.args.get('genre')
    sort_by = request.args.get('sort_by')
    descending = request.args.get('desc')

    if descending:
        books = Book.query.filter_by(genre=genre).order_by(
            desc(sort_by)).paginate(page=page, per_page=12)
    else:
        books = Book.query.filter_by(genre=genre).order_by(
            sort_by).paginate(page=page, per_page=12)

    raw_genres = Book.query.with_entities(
        Book.genre).group_by(Book.genre).all()
    genres = []

    for word in raw_genres:
        word = str(word)
        word = (word).replace('(', '').replace(')',
                                               '').replace('\'', '').replace(',', '')
        genres.append(word)

    return render_template('new_genre.html', genre=genre, books=books, genres=genres)


@books_blueprint.route('/books/best_sellers')
def best_sellers():
    stop_pagination = True
    books = Book.query.order_by(desc('soldUnits')).paginate(per_page=6)
    raw_genres = Book.query.with_entities(
        Book.genre).group_by(Book.genre).all()
    genres = []

    for word in raw_genres:
        word = str(word)
        word = (word).replace('(', '').replace(')',
                                               '').replace('\'', '').replace(',', '')
        genres.append(word)

    return render_template('best_sellers.html', books=books, genres=genres)


@books_blueprint.route('/books/best_rated')
def best_rated():
    stop_pagination = True
    books = Book.query.order_by(desc('rating')).paginate(per_page=6)
    raw_genres = Book.query.with_entities(
        Book.genre).group_by(Book.genre).all()
    genres = []

    for word in raw_genres:
        word = str(word)
        word = (word).replace('(', '').replace(')',
                                               '').replace('\'', '').replace(',', '')
        genres.append(word)

    return render_template('best_rated.html', books=books, genres=genres)


@books_blueprint.route('/books/new_releases')
def new_releases():
    stop_pagination = True
    books = Book.query.order_by(desc('releaseDate')).paginate(per_page=6)
    raw_genres = Book.query.with_entities(
        Book.genre).group_by(Book.genre).all()
    genres = []

    for word in raw_genres:
        word = str(word)
        word = (word).replace('(', '').replace(')',
                                               '').replace('\'', '').replace(',', '')
        genres.append(word)

    return render_template('new_releases.html', books=books, genres=genres)


@books_blueprint.route('/browse/authors')
def author():
    author = request.args.get('author')
    books = Book.query.filter_by(author=author).paginate(per_page=10)
    print(type(books))
    return render_template('new_browse.html', author=author, books=books)


# @books_blueprint.route('/browse/authors/<author>')
# def author(author):
#     #grab list of books based on author from db
#     books = Book.query.filter_by(author=author)
#     return render_template('list.html', author=author, books=books)

@books_blueprint.route('/browse/<ISBN>', methods=['GET', 'POST'])
def browse(ISBN):  # was named details
    # grab book details
    books = Book.query.filter_by(ISBN=ISBN).first()
    user = User.query.filter_by(id=User.id).first_or_404()

    if current_user.is_authenticated:
        orders = Orders.query.filter_by(userId=current_user.id)
        order = Orders.query.filter_by(
            userId=current_user.id, ISBN=ISBN).first()

    else:
        order = None
        orders = None

    form = BlogPostForm()
    page = request.args.get('page', 1, type=int)
    #blog_posts = BlogPost.query.order_by(BlogPost.date.desc()).paginate(page=page, per_page=10)
    blog_posts = BlogPost.query.filter_by(
        book_isbn=ISBN).order_by(BlogPost.date.desc())
    # Returns an instance of the main page

    if form.validate_on_submit():
        rating = request.form.get("rating", None)
        true_private = request.form.get('true_private')
        blog_post = BlogPost(title=form.title.data,  # must add here
                             text=form.text.data,
                             user_id=current_user.id,        # Must use the ID of the currently logged in user
                             rating=form.rating.data,
                             true_private=form.true_private.data,
                             book_isbn=ISBN
                             )
        # db.session.add(blog_post)                           # Add changes to the database by creating a blog post
        # db.session.commit()                                 # Confirming these changes
        flash("Blog Post Created")

        if true_private == 'true_private':
            blog_post = BlogPost(title=form.title.data,  # must add here
                                 text=form.text.data,
                                 user_id=current_user.id,        # Must use the ID of the currently logged in user
                                 rating=form.rating.data,
                                 true_private=form.true_private.data,
                                 book_isbn=ISBN
                                 )
        # Add changes to the database by creating a blog post
        db.session.add(blog_post)
        db.session.commit()

        store_isbn = Book.query.filter_by(ISBN=ISBN)
        #page = request.args.get('page', 1, type=int)
        #blog_posts = BlogPost.query.order_by(BlogPost.date.desc()).paginate(page=page, per_page=10)
        # Returns an instance of the main page

    return render_template('bookentry.html', ISBN=ISBN, books=books, blog_posts=blog_posts, book_isbn=ISBN, form=form, store_isbn=ISBN, order=order, orders=orders, user=user)
