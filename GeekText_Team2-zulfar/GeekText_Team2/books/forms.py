from flask_wtf import FlaskForm                         # Imports the forms API
from wtforms import StringField, SubmitField, TextAreaField     # Specific forms that are needed
from wtforms.validators import DataRequired                     # validators for these forms


class BlogPostForm(FlaskForm):
    # no empty titles or text possible
    # we'll grab the date automatically from the Model later
    title = StringField('Title', validators=[DataRequired()])                   # Title of post
    text = TextAreaField('Text', validators=[DataRequired()])                   # Tesxt of post
    rating = StringField('rating', validators=[DataRequired()])
    true_private = StringField('true_private')
    book_isbn = StringField()
    submit = SubmitField('Submit')                                            # Button to submit
