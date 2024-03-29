import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = str(os.urandom(20).hex())
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "app.db")}'
db = SQLAlchemy(app)


info = {
    "brand": "test_brand",
    "brand_slogan": "test_brand_slogan",
    "clearance_subheader": "test_subheader_text",
    "base_city": "NYC",
    "contact_link": "https://t.me/itsdust0n"
}


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    picture_link = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    shipping_price = db.Column(db.Integer, nullable=False)

    def __init__(self, name, description, picture_link, price, shipping_price):
        self.name = name
        self.description = description
        self.picture_link = picture_link
        self.price = price
        self.shipping_price = shipping_price

    def __repr__(self):
        return self.name


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.login


@app.route('/')
def index():
    items = Items.query.order_by(Items.id).all()
    return render_template('index.html', items=items, info=info)


@app.route('/admin', methods=['post', 'get'])
def admin():
    if 'isAuthenticated' not in session: session['isAuthenticated'] = 0
    if session['isAuthenticated'] == 1:
        return redirect(url_for('add_item'))
    else:
        if request.method == 'POST':
            login = request.form.get('login')
            pwd = request.form.get('pass')

            if all([login, pwd]) and all([login, pwd]) is not None:
                user = Users.query.filter_by(login=login).first()
                if user is not None and login == user.login and pwd == user.password:
                    try: session['isAuthenticated'] = 1
                    except Exception as e: print(f"Error while adding session data: {e}")
                    return redirect(url_for('add_item'))

    return render_template('admin.html')


@app.route('/admin/add_item', methods=['post', 'get'])
def add_item():
    if 'isAuthenticated' not in session:
        return redirect(url_for('index'))
    else:
        if session['isAuthenticated'] == 1:
            if request.method == 'POST':
                name = request.form.get('name')
                description = request.form.get('description')
                picture_link = request.form.get('picture')
                shipping_price = request.form.get('shipping')
                item_price = request.form.get('price')
                form_data = all([name, description, picture_link, shipping_price, item_price])

                if form_data and form_data is not None:
                    try:
                        db.session.add(Items(name=name, description=description, picture_link=picture_link, shipping_price=shipping_price, price=item_price))
                        db.session.commit()
                        print("Added")
                    except Exception as e:
                        print(f"Error while contact with db: {e}")
            return render_template('add_item.html', info=info, navbar=True, navbar_index=0)
        else:
            return redirect(url_for('index'))


@app.route('/admin/remove_item', methods=['post', 'get'])
def remove_item():
    if 'isAuthenticated' not in session:
        return redirect(url_for('index'))
    else:
        if session['isAuthenticated'] == 1:
            items = Items.query.order_by(Items.id).all()
            if request.method == "POST" and all([request.form.get('item-name'), request.form.get('item-description'), request.form.get('item-picture_link'), request.form.get('item-price')], request.form.get('item-shipping_price')) is not None:
                to_delete = Items.query.filter_by(
                    name=f'{request.form.get("item-name")}',
                    description=f'{request.form.get("item-description")}',
                    picture_link=f'{request.form.get("item-picture_link")}',
                    price=f'{request.form.get("item-price")}',
                    shipping_price=f'{request.form.get("item-shipping_price")}'
                ).first()

                try:
                    db.session.delete(to_delete)
                    db.session.commit()
                    print('Removed')
                except Exception as e:
                    print(f"Error while contact with db: {e}")
            return render_template('remove_item.html', info=info, navbar=True, navbar_index=1, items=items)
        else:
            return redirect(url_for('index'))


@app.route('/admin/add_user', methods=['post', 'get'])
def add_user():
    if 'isAuthenticated' not in session:
        return redirect(url_for('index'))
    else:
        if session['isAuthenticated'] == 1:
            if request.method == "POST":
                login = request.form.get('login')
                pwd = request.form.get('pass')
                if all([login, pwd]):
                    try:
                        db.session.add(Users(login=login, password=pwd))
                        db.session.commit()
                        print('Added')
                    except Exception as e:
                        print(f"Error while contact with db: {e}")
            return render_template('add_user.html', info=info, navbar=True, navbar_index=2)
        else:
            return redirect(url_for('index'))


@app.route('/admin/logout')
def logout():
    if 'isAuthenticated' not in session:
        return redirect(url_for('index'))
    else:
        if session['isAuthenticated'] == 1:
            try: session['isAuthenticated'] = 0
            except Exception as e: print('Error while contact with session data: ', e)
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=8000)