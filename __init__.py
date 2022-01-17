from flask import Flask, render_template, request, session, redirect, url_for, redirect

import DBscript

import loginScript

app = Flask(__name__)

error = None


@app.route("/")
def loginl():
    return redirect(url_for("loginpage"))


@app.route("/voorwaarden")
def loginl():
    naam = session['naam'] if 'naam' in session else 'Gast'
    return render_template("voorwaarden", naam=naam)


@app.route("/webshop")
def webshop():
    naam = session['naam'] if 'naam' in session else 'Gast'
    return render_template("webshop.html", naam=naam)


@app.route("/media")
def media():
    naam = session['naam'] if 'naam' in session else 'Gast'
    return render_template("media.html", naam=naam)


@app.route("/contact")
def contact():
    naam = session['naam'] if "naam" in session else "gast"
    return render_template("contact.html", naam=naam)


@app.route("/css")
def css():
    return redirect(url_for("static", filename="main.css"))


@app.route("/index")
def loginpage():
    naam = session['naam'] if "naam" in session else "gast"
    return render_template("index.html", naam=naam)


@app.route("/home")
def home():
    naam = session['naam'] if "naam" in session else "gast"
    return render_template("home.html", naam=naam)


@app.route("/login", methods=["POST"])
def inloggen():
    if request.method == "POST":
        if loginScript.CheckLogin(request.form['naam'], request.form['ticket']):
            session['naam'] = request.form['naam']
        else:
            error_fout = 'Foute naam of ticketnummer'
            return redirect(url_for("loginpage", error=error_fout))
    return redirect(url_for("home"))


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    cursor = None
    try:
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        if _quantity and _code and request.method == 'POST':
            conn = DBscript.connect()
            cursor = conn.cursor(DBscript.cursors.DictCursor)
            cursor.execute("SELECT * FROM product WHERE code=%s", _code)
            row = cursor.fetchone()

            itemArray = {
                row['code']: {'name': row['name'], 'code': row['code'], 'quantity': _quantity, 'price': row['price'],
                              'image': row['image'], 'total_price': _quantity * row['price']}}

            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:
                if row['code'] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if row['code'] == key:
                            old_quantity = session['cart_item'][key]['quantity']
                            total_quantity = old_quantity + _quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * row['price']
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                all_total_price = all_total_price + _quantity * row['price']

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            return redirect(url_for('.products'))
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/')
def products():
    try:
        conn = DBscript.connect()
        cursor = conn.cursor(DBscript.cursors.DictCursor)
        cursor.execute("SELECT * FROM product")
        rows = cursor.fetchall()
        return render_template('products.html', products=rows)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        # return redirect('/')
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


if __name__ == "__main__":
    app.run(ssl_context='adhoc')
