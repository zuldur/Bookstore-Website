from flask import Blueprint, flash, request, render_template, redirect, url_for
from GeekText_Team2 import db
from GeekText_Team2.models import Wishlist
from GeekText_Team2.Wishlist.forms import wishlistPostForm
from GeekText_Team2.users.views import current_user

wishlist_posts = Blueprint('wishlist_posts', __name__,
                           template_folder='templates/wishlist')


@wishlist_posts.route('/create', methods=['GET', 'POST'])
def create_wish():

    form = wishlistPostForm()

    if form.validate_on_submit():
        title = form.title.data

        wishlist_post = wishlist(title=form.title.data)
        db.session.add(wishlist_post)
        db.session.commit()
        flash('Wishlist created')
        return redirect(url_for('wishlist_posts.viewallw'))
        #redirect(url_for('Wishlist_posts.list', wishlist_post_id= wishlist_post.id))

    return render_template('addWish.html', form=form)


@wishlist_posts.route('/<int:wishlist_post_id>', methods=['GET', 'POST'])
def list(wishlist_post_id):

    Wishlist_post = wishlist.query.get_or_404(wishlist_post_id)
    return render_template('Wishlist.html', title=Wishlist_post.title, post=Wishlist_post)


@wishlist_posts.route('/<int:wishlist_post_id>/update', methods=['GET', 'POST'])
def update(wishlist_post_id):
    wishlist_post = wishlist.query.get_or_404(wishlist_post_id)
    if form.validate_on_submit():

        wishlist_post.title = form.title.data

        db.session.commit()

        flash('Blog post updated')
        return redirect(url_for('wishlist_post.list', wishlist_post_id=wishlist_post.id))


@wishlist_posts.route('/<int:wishlist_post_id>/delete', methods=['GET', 'POST'])
def delete(wishlist_post_id):

    wishlist_post = wishlist.query.get_or_404(wishlist_post_id)
    db.session.delete(wishlist_post)
    db.session.commit()
    flash('Wishlist post Deleted')
    return redirect(url_for('Wishlist_posts.viewallw'))


@wishlist_posts.route('/viewall', methods=['GET', 'POST'])
def viewallw():

    wishlist_post = wishlist.query.all()
    return render_template('wlist.html', wishlist=wishlist_post)
