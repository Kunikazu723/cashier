import sqlite3
import secrets
# from flask_session import Session
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, session, url_for, g
from helpers import apology, to_reais

app = Flask(__name__)
app.secret_key = secrets.token_hex()

app.jinja_env.filters['to_reais'] = to_reais

DATABASE = 'cashier.db'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route('/')
def index() :
    if 'cart' not in session or not session["cart"] :
        session["cart"] = {}

    if 'user_id' not in session :
        return redirect(url_for('login'))
    
    username = query_db("SELECT username FROM users WHERE id = ?", (session["user_id"],), one=True)

    # select all products where the user_id == session["user_id"] // Render them each with the amountinput
    products = query_db("SELECT * FROM products WHERE user_id = ? AND available > 0 ORDER BY product_name ASC", (session['user_id'],))
    history = query_db("SELECT * FROM history WHERE user_id = ? ORDER BY time DESC LIMIT 10", (session['user_id'],))
    

    return render_template('index.html', username=username, products=products, history=history)

@app.route('/products')
def products() :
    if 'user_id' not in session :
        return redirect(url_for('login'))

    products = query_db("SELECT id, product_name, price, available FROM products WHERE user_id = ? ORDER BY product_name ASC", (session["user_id"],))
    return render_template('products.html', products=products)

@app.route('/add_available', methods=["POST"]) 
def add_available() :
    if 'user_id' not in session :
        return redirect(url_for('login'))
    product_id = request.form.get("id")
    amount = request.form.get("amount")
    db_execute("UPDATE products SET available = available + ? WHERE id = ?", (amount, product_id))

    return redirect(url_for('products'))
    
    



@app.route('/add', methods=["POST"])
def add() :
    if 'user_id' not in session:
        return redirect('/')
    name = request.form.get('product_name')
    price = request.form.get('price')
    available = request.form.get('available')
    if not name or not price or not available :
        return apology("Erro campo inválido")
    try :
        db_execute("INSERT INTO products (user_id, product_name, price, available) VALUES (?, ?, ?, ?) ",\
                (session["user_id"], name.lower(), price, available))
    except sqlite3.IntegrityError :
        return apology("O produto já existe")
    return redirect(url_for('products'))


@app.route('/login', methods=["GET", "POST"])
def login() :
    if request.method == "POST" :
        username = request.form.get("username")
        password = request.form.get("password")
        # print(request.form)
        if not username or not password :
            return apology("Valores inválidos")
        phash = query_db("SELECT hashpass FROM users WHERE username = ?", (username,), one=True) 
        # print(phash)
        if not phash :
            return apology("invalid username or password")
        phash = phash['hashpass']

        if check_password_hash(phash, password) :
            session["user_id"] = query_db("SELECT id FROM users WHERE username = ?", (username,), one=True)['id']
            session["cart"] = []
            return redirect('/')

        return apology("Senha incorreta")
    else :
        return render_template("login.html")

@app.route('/register', methods=["GET","POST"])
def register() :
    if request.method == "POST" :
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        template = 'register.html'
        if not username or not password or not confirm :
            return render_template(template, message="Dados inválidos")
        
        if password != confirm :
            return render_template(template, message="Senha diferente da confirmação")
        
        if len(password) < 8 :
            return render_template(template, message="Min 8 caracteres para a senha")
        try :
            db_execute("INSERT INTO users (username, hashpass) VALUES (?, ?)",(username, generate_password_hash(password)))
        except sqlite3.IntegrityError :
            return render_template(template, message='Nome de usuário já existe')

        session["user_id"] = query_db("SELECT id FROM users WHERE username = ?", (username,), one=True)
        return redirect('/login')
        # return apology("checking your register")
    else :
        return render_template(template)

@app.route('/logout')
def logout() :
    session.clear()
    return redirect('/')

@app.route('/sell', methods=["POST"])
def sell() :
    if 'cart' not in session or not session['cart'] :
        session['cart'] = {}
    items = request.form
    for id , amount in items.items() :
        if amount.isdigit():
            data = query_db("SELECT * FROM products WHERE id = ?", (id,), one=True)
            amount = int(amount)
            if amount > data['available'] :
                return apology(f"Quantia {amount} excede o disponível {data['available']}")
            
            cart_data = {
                                'product_id' : data['id'], 
                                'product_name' : data['product_name'],
                                'price' : data['price'],
                                'amount' : amount,
                                'subtotal' : data['price'] * amount,
                                }
            
            session['cart'][str(data['id'])] = cart_data
            session.modified = True
    return redirect('/')

@app.route('/cart', methods=["GET", "POST"])
def cart() :
    if request.method == "POST" :
        if 'cart' in session and session['cart'] :
            for item in session['cart'].values() :
                db_execute("UPDATE products SET available = available - ? WHERE id = ?",\
                          (item['amount'], int(item['product_id']),))
                
                # Adding each item to history
                db_execute("INSERT INTO history (user_id, amount, product_name, unit_price, total, time)\
                            VALUES (?, ?, ?, ?, ?, ?)", (session['user_id'], item["amount"], item['product_name'],\
                            item['price'], item["subtotal"], datetime.datetime.now(),))
            session['cart'] = {}
            session.modified = True
        return apology("decontando cada item do banco de dados (ainda não)")
    else :
        totals = 0
        if 'cart' in session and session["cart"] :

            for item in session["cart"].values() :
                totals += item['subtotal']
            print(totals)
            return render_template('cart.html', cart=session["cart"].values(), totals=totals)
        else :
            return apology("Não há nada no seu carrinho")

@app.route('/delete_from_cart', methods=["POST"])
def delete_from_cart() :
    product_id = request.form.get('product_id')
    del session['cart'][product_id]
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/edit_product', methods=["GET", "POST"]) 
def edit_product() :
    if request.method == 'POST' :
        id = request.form.get("product_id")
        name = request.form.get("product_name")
        price = request.form.get("price")
        available = request.form.get("available")
        # print(f"{id}\n{name}\n{price}\n{available}")
        template = 'edit_product.html'
        if not id or not name or not price or not available :
            return apology("Dados inválidos")
        if not available.isdigit() :
            return apology("Dados incorretos")
        available = int(available)
        db_execute("UPDATE products SET product_name = ?, price = ?, available = ? WHERE id = ?", (name.lower(), price, available, id,))
        return redirect(url_for('cashier.products'))
        
    else :
        product_data = {
            "product_id" : request.args.get("product_id"),
            "product_name" : request.args.get("product_name"),
            "price" : request.args.get("price"),
            "available" : request.args.get("available"),
        }
        return render_template('edit_product.html', product_data=product_data)

# DATABASE THINGS THAT I DO NOT UNDERSTAND AT ALL
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

    db.row_factory = make_dicts
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def db_execute(query, args=()) :
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    