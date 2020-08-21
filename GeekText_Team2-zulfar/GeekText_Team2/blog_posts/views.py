from flask import render_template,url_for,flash, redirect,request,Blueprint
from flask_login import current_user,login_required
from GeekText_Team2 import db             # Import the database
from GeekText_Team2.models import BlogPost
from GeekText_Team2.blog_posts.forms import BlogPostForm

blog_posts = Blueprint('blog_posts',__name__)           # Creating object instance for a blog post

'''@blog_posts.route('/create',methods=['GET','POST'])
@login_required                                         # User must be logged in
def create_post():
    form = BlogPostForm()                               # Instance of the form

    if form.validate_on_submit():
        rating = request.form.get("rating", None)
        true_private = request.form.get('true_private')
        blog_post = BlogPost(title=form.title.data,# must add here
                             text=form.text.data,
                             user_id=current_user.id,        # Must use the ID of the currently logged in user
                             rating = form.rating.data,
                             true_private = form.true_private.data
                             )
        db.session.add(blog_post)                           # Add changes to the database by creating a blog post
        db.session.commit()                                 # Confirming these changes


        if true_private == 'true_private':
            blog_post = BlogPost(title=form.title.data,# must add here
                                 text=form.text.data,
                                 user_id= 'annonymous',        # Must use the ID of the currently logged in user
                                 rating = form.rating.data,
                                 true_private = form.true_private.data
                                 )
        db.session.add(blog_post)                           # Add changes to the database by creating a blog post
        db.session.commit()


        #db.session.add(blog_post)                           # Add changes to the database by creating a blog post
        #db.session.commit()


        return redirect(url_for('core.index',form=form))

    return render_template('create_post.html',form=form)'''


# int: makes sure that the blog_post_id gets passed as in integer
# instead of a string so we can look it up later.
@blog_posts.route('/<int:blog_post_id>')            # int: forces the post id to be an interger
def blog_post(blog_post_id):
    # grab the requested blog post by id number or return 404
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    return render_template('blog_post.html',title=blog_post.title,
                            date=blog_post.date,post=blog_post
    )


# Update/edit a blog post
@blog_posts.route("/<int:blog_post_id>/update", methods=['GET', 'POST'])
@login_required
def update(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:            # Make sure the post blog is only able to be edited by the user who created it
        # Forbidden, No Access
        abort(403)

    form = BlogPostForm()                           # Instance of that form, that actually interacts with the python code
    if form.validate_on_submit():
        blog_post.title = form.title.data
        blog_post.text = form.text.data
        db.session.commit()

        return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post.id))
    # Pass back the old blog post information so they can start again with
    # the old text and title.
    elif request.method == 'GET':
        form.title.data = blog_post.title
        form.text.data = blog_post.text
    return render_template('create_post.html', title='Update',
                           form=form)

# Delete a blog post
@blog_posts.route("/<int:blog_post_id>/delete", methods=['POST'])
@login_required
def delete_post(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)
    db.session.delete(blog_post)
    db.session.commit()

    return redirect(url_for('core.index'))
