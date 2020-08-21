from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from GeekText_Team2 import db
from GeekText_Team2.models import Cart, User, Book, Orders, SavedItems
import stripe


cart_blueprint = Blueprint('cart', __name__)

public_key = "pk_test_TYooMQauvdEDq54NiTphI7jx"
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"


@cart_blueprint.route('/cart')
@login_required
def cart():
    items = Book.query.join(Cart).add_columns(Cart.userId, Cart.ISBN, Cart.quantity,
                                              Book.price, Book.title, Book.image_url).filter_by(userId=current_user.id)
    totalPrice = 0
    for row in items:
        totalPrice += row.price*row.quantity
    savedItems = Book.query.join(SavedItems).filter_by(userId=current_user.id)
    return render_template('cart.html', totalPrice=totalPrice, items=items, savedItems=savedItems)


@cart_blueprint.route('/addToCart',  methods=['GET', 'POST'])
@login_required
def addToCart():
    bookId = request.args.get('ISBN')
    check = Cart.query.filter_by(userId=current_user.id, ISBN=bookId).first()
    if check is not None:
        return redirect(url_for('cart.cart'))
    item = Cart(userId=current_user.id, ISBN=bookId, quantity=1)
    db.session.add(item)
    db.session.commit()
    flash('Book added to your shopping cart')
    return redirect(url_for('books.list'))


@cart_blueprint.route('/addToSaved',  methods=['GET', 'POST'])
@login_required
def addToSaved():
    bookId = request.args.get('ISBN')
    check = SavedItems.query.filter_by(
        userId=current_user.id, ISBN=bookId).first()
    if check is not None:
        return redirect(url_for('cart.cart'))
    item = SavedItems(userId=current_user.id, ISBN=bookId)
    db.session.add(item)
    db.session.commit()
    flash('Book saved. Look in your cart')
    return redirect(url_for('books.list'))


@cart_blueprint.route('/moveToCart')
@login_required
def moveToCart():
    bookId = request.args.get('ISBN')
    item = Cart(userId=current_user.id, ISBN=bookId, quantity=1)
    savedItem = SavedItems.query.filter_by(
        userId=current_user.id, ISBN=bookId).first()
    db.session.add(item)
    db.session.delete(savedItem)
    db.session.commit()
    flash('Book moved to cart')
    return redirect(url_for('cart.cart'))


@cart_blueprint.route('/moveToSaved')
@login_required
def moveToSaved():
    bookId = request.args.get('ISBN')
    item = SavedItems(userId=current_user.id, ISBN=bookId)
    cartItem = Cart.query.filter_by(
        userId=current_user.id, ISBN=bookId).first()
    db.session.add(item)
    db.session.delete(cartItem)
    db.session.commit()
    flash('Book moved to cart')
    return redirect(url_for('cart.cart'))


@cart_blueprint.route('/removeFromCart')
@login_required
def removeFromCart():
    item = Cart.query.filter_by(
        userId=current_user.id, ISBN=request.args.get('ISBN')).first()
    db.session.delete(item)
    db.session.commit()
    flash('Book removed from your shopping cart')
    return redirect(url_for('cart.cart'))


@cart_blueprint.route('/removeFromSaved')
@login_required
def removeFromSaved():
    item = SavedItems.query.filter_by(
        userId=current_user.id, ISBN=request.args.get('ISBN')).first()
    db.session.delete(item)
    db.session.commit()
    flash('Book removed from your shopping cart')
    return redirect(url_for('cart.cart'))


@cart_blueprint.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = Book.query.join(Cart).filter_by(userId=current_user.id)
    totalPrice = 0
    for row in items:
        item = Cart.query.filter_by(
            userId=current_user.id, ISBN=row.ISBN).first()
        totalPrice += row.price*item.quantity
        order = Orders(userId=current_user.id,
                       ISBN=row.ISBN, quantity=item.quantity)
        db.session.add(order)
        db.session.delete(item)
    db.session.commit()
    return render_template('checkout.html', totalPrice=totalPrice)


@cart_blueprint.route('/addQuantity')
@login_required
def addQuantity():
    bookId = request.args.get('ISBN')
    item = Cart.query.filter_by(userId=current_user.id, ISBN=bookId).first()
    item.quantity += 1
    db.session.commit()
    return redirect(url_for('cart.cart'))


@cart_blueprint.route('/lowerQuantity')
@login_required
def lowerQuantity():
    bookId = request.args.get('ISBN')
    item = Cart.query.filter_by(userId=current_user.id, ISBN=bookId).first()
    item.quantity -= 1
    db.session.commit()
    return redirect(url_for('cart.cart'))


@cart_blueprint.route('/confirmPayment')
@login_required
def confirmPayment():
    items = Book.query.join(Cart).add_columns(Cart.userId, Cart.ISBN, Cart.quantity,
                                              Book.price, Book.title, Book.image_url).filter_by(userId=current_user.id)
    totalPrice = 0
    for row in items:
        item = Cart.query.filter_by(
            userId=current_user.id, ISBN=row.ISBN).first()
        totalPrice += row.price*item.quantity
    return render_template('confirmPayment.html', totalPrice=totalPrice, items=items, public_key=public_key)


@cart_blueprint.route('/payment', methods=['POST'])
@login_required
def charge():
    items = Book.query.join(Cart).filter_by(userId=current_user.id)
    totalPrice = 0
    for row in items:
        item = Cart.query.filter_by(
            userId=current_user.id, ISBN=row.ISBN).first()
        totalPrice += row.price*item.quantity

    amount = int(totalPrice*100)

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'])

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd')

    return redirect(url_for('cart.checkout'))


# @cart_blueprint.route('/clearOrders')
# @login_required
# def orderErase():
#    orders = Orders.query.filter_by(userId=current_user.id)
#    for row in orders:
#        order = Orders.query.filter_by(userId=current_user.id, ISBN=row.ISBN).first()
#        db.session.delete(order)
#    db.session.commit()
#    return redirect(url_for('cart.cart'))
