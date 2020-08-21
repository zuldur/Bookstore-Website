from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class wishlistPostForm(FlaskForm):
	title = StringField('title', validators=[DataRequired()])
	submit = SubmitField('Wishlist')


