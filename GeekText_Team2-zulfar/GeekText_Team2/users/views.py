from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from GeekText_Team2 import db, app, mail, google
from flask_mail import Message
from threading import Thread
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from GeekText_Team2.models import User, Address, Payment_Info
from GeekText_Team2.users.forms import RegistrationForm, LoginForm, UpdateUserForm, UpdateShippingForm, UpdateAddressForm, AddPaymentInfo, ForgotForm, ChangePassword
from GeekText_Team2.users.picture_handler import add_profile_pic
from GeekText_Team2.models import BlogPost
from itsdangerous import URLSafeTimedSerializer
from GeekText_Team2.blog_posts.forms import BlogPostForm
import datetime

users = Blueprint('users', __name__, template_folder='templates/')


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.home'))


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    forgot_form = ForgotForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()
        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        if user is not None:
            if user.check_password(form.password.data) and user is not None:
                # log in the user
                login_user(user)
            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
                next = request.args.get('next')
            # if that next exists we go to it, otherwise we'll go to
            # the welcome page.
                if next == None or not next[0] == '/':
                    next = url_for('books.list')

                return redirect(next)
    return render_template('login.html', form=form, forgot_form=forgot_form)


@users.route('/forgot_password?', methods=['GET', 'POST'])
def forgot_password(form):
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email.lower()).first()
        # if user:

    return render_template("forgot_password.html")


@users.route('/register', methods=['GET', 'POST'])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            user = User(first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        email=form.email.data,
                        username=form.username.data,
                        password=form.password.data)

            db.session.add(user)
            db.session.commit()
            print("HERE")
            send_confirmation_email(user.email)
            flash(
                'Thanks for registering! Please check your email to confirm your email address.', 'success')
            st8 = form.state.data.capitalize()
            u_address = Address(user_id=user.id,
                                address=form.address.data,
                                city=form.city.data,
                                state=st8,
                                postal_code=form.zip_code.data,
                                phone_num=form.phone_num.data)

            db.session.add(u_address)
            db.session.commit()
            flash('Thanks for registering! Now you can login!')
            return redirect(url_for('users.login'))
        except IntegrityError:
            db.session.rollback()
            flash('ERROR! Email ({}) already exists.'.format(
                form.email.data), 'error')
    return render_template('register.html', form=form)

########################## SHIPPING INFO METHODS ############################
@users.route('/shipping_info', methods=['GET', 'POST'])
@login_required
def shipping_info():
    form = UpdateShippingForm()
    addr = 0
    addresses = current_user.address
    if form.validate_on_submit():
        new_address = Address(user_id=current_user.id,
                              address=form.address.data,
                              city=form.city.data,
                              state=form.state.data,
                              postal_code=form.zip_code.data,
                              phone_num=form.phone_num.data)

        #user = User.query.filter_by(address=form.email.data).first()

        print(new_address.address)
        db.session.add(new_address)
        db.session.commit()
        addresses = current_user.address
        redirect(url_for('users.shipping_info', form=form, addresses=addresses))

    return render_template('shipping.html', form=form, addresses=addresses, addr=addr)


@users.route('/shipping_info/<int:address_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    address = Address.query.filter_by(id=address_id).first()

    if address.user_id != current_user.id:
        abort(403)

    form = UpdateAddressForm()

    if form.validate_on_submit():
        address.address = form.address.data
        address.city = form.city.data
        address.state = form.state.data
        address.postal_code = form.zip_code.data
        address.phone_num = form.phone_num.data

        db.session.commit()
        flash('Address updated')
        return redirect(url_for('users.shipping_info'))

    return render_template('edit_address.html', form=form, address=address)


@users.route('/shipping_info/<int:address_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_address(address_id):
    address = Address.query.filter_by(id=address_id).first()

    if address.user_id != current_user.id:
        abort(403)

    db.session.delete(address)
    db.session.commit()
    flash('Address deleted')
    return redirect(url_for('users.shipping_info'))
#########################################################################

###################### PAYMENT INFO METHODS ##################################
@users.route('/payment_info', methods=['GET', 'POST'])
@login_required
def payment_info():
    if current_user.payment_info is not None:
        cards = current_user.payment_info

        redirect(url_for('users.payment_info', cards=cards))

    return render_template('payment_info.html', cards=cards)


@users.route('/add_card', methods=['GET', 'POST'])
@login_required
def add_card():
    form = AddPaymentInfo()
    if form.validate_on_submit():
        # m_y = form.exp_date.data
        # date_time = datetime.datetime.strptime(m_y, '%m/%y').date()
        # date = date_time.strftime("%m/%Y")
        # print(m_y)
        # print(date)
        c_card = Payment_Info(credit_number=form.card_num.data,
                              user_id=current_user.id,
                              cardholder=form.name.data,
                              expiration_date=form.exp_date.data,
                              csv=form.csv.data,
                              ZIP=form.zip.data)

        ex_card = Payment_Info.query.filter_by(
            credit_number=form.card_num.data).first()
        if ex_card is not None and ex_card.credit_number == c_card.credit_number and ex_card.user_id == c_card.user_id:
            flash('That card alredy exists')
            return redirect(url_for('users.add_card', form=form))
        else:
            db.session.add(c_card)
            db.session.commit()
            flash('Card Added')
            return redirect(url_for('users.payment_info'))

    return render_template("add_card.html", form=form)


@users.route('/payment_info/delete/<int:card_id>', methods=['GET', 'POST'])
@login_required
def delete_card(card_id):
    card = Payment_Info.query.filter_by(id=card_id).first()
    if card.user_id != current_user.id:
        abort(403)

    db.session.delete(card)
    db.session.commit()
    flash('Crecit card removed')
    return redirect(url_for('users.payment_info'))

##########################################################################


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():

    if not current_user:
        abort(403)

    form = UpdateUserForm()
    c_email = current_user.email
    c_username = current_user.username
    existing_email = None
    existing_username = None
    f_name = current_user.first_name
    l_name = current_user.last_name
    if form.validate_on_submit():
        print(form.picture.data)
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data, username)
            current_user.profile_image = pic
            flash('Picture updated')
            db.session.commit()

        existing_user_name = User.query.filter_by(
            username=form.username.data).first()
        existing_user_email = User.query.filter_by(
            email=form.email.data).first()

        '''current_user.first_name = form.firstname.data
        current_user.last_name = form.lastname.data
        db.session.commit()'''

        if(existing_user_name is not None):
            existing_username = existing_user_name.username

        if(existing_user_email is not None):
            existing_email = existing_user_email.email

        if(len(form.firstname.data) != 0):
            current_user.first_name = form.firstname.data
            db.session.commit()

        if(len(form.lastname.data) != 0):
            current_user.last_name = form.lastname.data
            db.session.commit()

        if existing_email == c_email and existing_username == c_username:
            return redirect(url_for('users.account'))

        if not form.email.data:
            current_user.email = current_user.email
        elif existing_email is None:
            current_user.email = form.email.data
        elif existing_email is not None and existing_email != c_email:
            flash('A user already exists with that email')
            return redirect(url_for('users.account'))

        if not form.username.data:
            current_user.username = current_user.username

        elif existing_username is None:
            current_user.username = form.username.data
        elif existing_username is not None and existing_username != c_username:
            flash('A user already exists with that username')
            return redirect(url_for('users.account'))

        db.session.commit()
        print(existing_email, " | ", c_email)
        print(existing_username, " | ", c_username)
        flash('User Account Updated')
        return redirect(url_for('users.account'))

    profile_image = url_for(
        'static', filename='profile_pics/' + current_user.profile_image)
    return render_template('account.html', profile_image=profile_image, form=form)


@users.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        print("HERERERE")
        new_pass = generate_password_hash(form.new_password.data)
        current_user.password_hash = new_pass
        flash("Password successfully changed")
        db.session.commit()
        return redirect(url_for('users.account'))
    return render_template('change_password.html', form=form)


@users.route("/<username>")
def user_posts(username):
    # Limits the number of post that appears initially
    page = request.args.get('page', 1, type=int)
    # Checks it is the right user
    user = User.query.filter_by(username=username).first_or_404()
    # Returns a list of post, only done by our user
    blog_posts = BlogPost.query.filter_by(author=user).order_by(
        BlogPost.date.desc()).paginate(page=page, per_page=5)
    return render_template('user_blog_posts.html', blog_posts=blog_posts, user=user)


@users.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(
            token, salt='email-confirmation-salt', max_age=3600)
        print(email + "Here!")
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('users.login'))

    user = User.query.filter_by(email=email).first()

    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('Thank you for confirming your email address!', 'success')

    return redirect(url_for('books.list'))


######### HELPER METHODS ###########
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, html_body):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[msg])
    thr.start()


def send_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    confirm_url = url_for(
        'users.confirm_email',
        token=confirm_serializer.dumps(
            user_email, salt='email-confirmation-salt'),
        _external=True)

    html = render_template(
        'email_confirmation.html',
        confirm_url=confirm_url)

    send_email('Confirm Your Email Address', [user_email], html)
