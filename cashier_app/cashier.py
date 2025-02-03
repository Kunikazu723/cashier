from flask import (
    Blueprint, request, render_template, session, g, url_for, flash, redirect
)

from sqlite3 import IntegrityError
import requests
import datetime

from cashier_app.auth import login_required
from cashier_app.db import get_db
bp = Blueprint('cashier', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    if 'cart' not in session or not session["cart"] :
        session["cart"] = {}
    
    products = db.execute("SELECT * FROM products WHERE user_id = ? AND available > 0 ORDER BY product_name ASC", (session['user_id'],)).fetchall()
    history = db.execute("SELECT * FROM history WHERE user_id = ? ORDER BY time DESC LIMIT 10", (session['user_id'],)).fetchall()
    
    message = requests.get('https://meowfacts.herokuapp.com/?lang=por-br').json()['data'][0]
    return render_template('cashier/index.html', products=products, history=history, message=message)

@bp.route('/products')
@login_required
def products():
    products = get_db().execute(
        'SELECT * FROM products WHERE user_id = ? ORDER BY product_name ASC',
        (session['user_id'],)
    ).fetchall()
    if not products:
        flash('Você ainda não possui nenhum produto.')
    return render_template('cashier/products.html', products=products)

# Adicionar produtos
@bp.route('/add_product', methods=["POST"])
@login_required
def add_product() :
    name = request.form.get('product_name')
    price = request.form.get('price')
    available = request.form.get('available')
    error = None
    if not name or not price or not available :
        error = 'Dados para produto inválidos.'
    try :
        db = get_db()
        db.execute("INSERT INTO products (user_id, product_name, price, available) VALUES (?, ?, ?, ?) ",\
                (session["user_id"], name.lower(), price, available))
        db.commit()
    except IntegrityError :
        error = f'Produto {name} já existe'
    if error:
        flash(error)
    return redirect(url_for('cashier.products'))


@bp.route('/add_to_cart', methods=["POST"])
def add_to_cart() :
    if 'cart' not in session or not session['cart'] :
        session['cart'] = {}
    items = request.form
    error = None
    for id , amount in items.items() :
        if amount.isdigit():
            data = get_db().execute("SELECT * FROM products WHERE id = ?", (id,),).fetchone()
            amount = int(amount)
            if amount > data['available'] :
                error = f"Quantia {amount} maior que o disponível: {data['available']}"
            
            if not error:
                cart_data = {
                            'product_id' : data['id'], 
                            'product_name' : data['product_name'],
                            'price' : data['price'],
                            'amount' : amount,
                            'subtotal' : data['price'] * amount,
                            }
                
                session['cart'][str(data['id'])] = cart_data
                session.modified = True
    if error:
        flash(error)
    return redirect(url_for('cashier.index'))


@bp.route('/cart', methods=["GET", "POST"])
def cart() :
    error = None
    cart_exist = 'cart' in session and session["cart"]
    error = "carrinho vazio" if not cart_exist else ""
    if request.method == "POST" :
        if cart_exist :
            db = get_db()
            for item in session['cart'].values() :
                db.execute("UPDATE products SET available = available - ? WHERE id = ?",\
                          (item['amount'], int(item['product_id']),))
                
                # Adding each item to history
                db.execute("INSERT INTO history (user_id, amount, product_name, unit_price, total, time)\
                            VALUES (?, ?, ?, ?, ?, ?)", (session['user_id'], item["amount"], item['product_name'],\
                            item['price'], item["subtotal"], datetime.datetime.now(),))
            db.commit()
            session['cart'] = {}
            session.modified = True
            return redirect(url_for('cashier.index'))
        else:
            flash(error)
            return render_template('cashier/cart.html', cart=session["cart"].values(), totals=0)

    else :
        totals = 0
        if cart_exist :

            for item in session["cart"].values() :
                totals += item['subtotal']
            print(totals)
        
        if error:
            flash(error)
        return render_template('cashier/cart.html', cart=session["cart"].values(), totals=totals)
    
@bp.route('/delete_from_cart', methods=["POST"])
def delete_from_cart() :
    product_id = request.form.get('product_id')
    del session['cart'][product_id]
    session.modified = True
    return redirect(url_for('cashier.cart'))


@bp.route('/edit_product', methods=["GET", "POST"]) 
def edit_product() :
    if request.method == 'POST' :
        db = get_db()
        id = request.form.get("product_id")
        name = request.form.get("product_name")
        price = request.form.get("price")
        available = request.form.get("available")
        error = None
        # print(f"{id}\n{name}\n{price}\n{available}")
        if not id or not name or not price or not available :
            error = 'Dados inválidos'
        if not available.isdigit() :
            error = 'Digite um número para a quantidade'
        if error is None:
            available = int(available)
            db.execute("UPDATE products SET product_name = ?, price = ?, available = ? WHERE id = ?", (name.lower(), price, available, id,))
            db.commit()
        else:
            flash(error)
        return redirect(url_for('cashier.products'))
        
    else :
        product_data = {
            "product_id" : request.args.get("product_id"),
            "product_name" : request.args.get("product_name"),
            "price" : request.args.get("price"),
            "available" : request.args.get("available"),
        }
        return render_template('cashier/edit_product.html', product_data=product_data)
    
@bp.route('/about')
def about():
    date = datetime.date.today().strftime(r"%m/%d/%Y")
    return render_template('cashier/about.html', date=date)