# Database setup code
from db_setup import Categories, Base, Items

# Imports from sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# imports from flask
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response

# imports from oauth2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# imports from python library
import random
import string
import httplib2
import json
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('json/client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "item catelogs"

# Connect to the database
engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(function):
    def wrapper():
        if 'username' in login_session:
            function()
        else:
            response = make_response(
                    json.dumps("A user must be logged to add a new item."),
                    401
                )
            return response
    wrapper.func_name = function.func_name
    return wrapper


@app.route('/')
@app.route('/categories/')
def categoriesPage():
    '''
        Display more all categories and most recent added items.
    '''
    categories = session.query(Categories).all()
    latest_10 = session.query(Items).order_by(Items.id.desc()).limit(10)
    return render_template("catelogs.html",
                           categories=categories, latest_10=latest_10)


@app.route('/categories/<int:categories_id>/')
def itemsPage(categories_id):
    '''
        Display all items in acategories.
    '''
    categories = session.query(Categories).all()
    items_list = session.query(Items).filter_by(
        categories_id=categories_id).all()
    categorie = session.query(Categories).filter_by(id=categories_id).first()
    return render_template("itemsPage.html",
                           categories=categories,
                           categorie=categorie,
                           items_list=items_list)


@app.route('/categories/<int:categories_id>/<int:item_id>/')
def itemPage(categories_id, item_id):
    '''
        Display an item
    '''
    item = session.query(Items).filter_by(categories_id=categories_id).first()
    return render_template("itemPage.html", item=item)


@app.route('/categories/newCategories/', methods=['GET', 'POST'])
def newCategories():
    '''
        Create new categories
    '''
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new = Categories(
            name=request.form['name'],
            user_id=login_session['gplus_id']
        )
        session.add(new)
        session.commit()
        return redirect(url_for('categoriesPage'))
    else:
        return render_template('newCatelogs.html')


@app.route('/categories/<int:categories_id>/newItem/', methods=['GET', 'POST'])
def newItem(categories_id):
    '''
        Create new items
    '''
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategorie = Items(
            name=request.form['name'],
            description=request.form['description'],
            categories=session.query(Categories). filter_by(
                id=categories_id).first(), user_id=login_session['gplus_id']
            )
        session.add(newCategorie)
        session.commit()
        return redirect(url_for('itemsPage', categories_id=categories_id))
    else:
        return render_template('newItem.html', categories_id=categories_id)


@app.route('/categories/<int:categories_id>/edit/', methods=['GET', 'POST'])
def editCategories(categories_id):
    '''
        Update a categories name
    '''
    if 'username' not in login_session:
        return redirect('/login')
    editCate = session.query(Categories).filter_by(id=categories_id).one()
    if(editCate.user_id != login_session['gplus_id']):
        script = "<script>function myFunction() {alert('You are not authorized"
        script += "to edit this restaurant. Please create your own restaurant"
        script += "in order to edit.');}</script><body"
        script += "onload='myFunction()'>"
        return script
    if request.method == 'POST':
        if request.form['name']:
            editCate.name = request.form['name']
            session.add(editCate)
            session.commit()
            return redirect(url_for('itemsPage',
                                    categories_id=editCate.id))
    else:
        return render_template('editCategories.html', editCategories=editCate)


@app.route('/categories/<int:categories_id>/<int:items_id>/edit/',
           methods=['GET', 'POST'])
def editItems(categories_id, items_id):
    '''
        update an item
    '''
    if 'username' not in login_session:
        return redirect('/login')
    editItem = session.query(Items).filter_by(id=items_id).one()
    if(editItem.user_id != login_session['gplus_id']):
        script = "<script>function myFunction() {alert('You are not authorized"
        script += "to edit this restaurant. Please create your own restaurant"
        script += "in order to edit.');}</script><body"
        script += "onload='myFunction()'>"
        return script
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
            editItem.description = request.form['description']
            session.add(editItem)
            session.commit()
            return redirect(url_for('itemPage',
                                    categories_id=editItem.categories.id,
                                    item_id=editItem.id))
    else:
        return render_template('editItem.html', editItem=editItem)


@app.route('/categories/<int:categories_id>/delete/', methods=['GET', 'POST'])
def deleteCategories(categories_id):
    '''
        delete a categories
    '''
    if 'username' not in login_session:
        return redirect('/login')
    deleteCategorie = session.query(
        Categories).filter_by(id=categories_id).one()
    if(deleteCategorie.user_id != login_session['gplus_id']):
        script = "<script>function myFunction() {alert('You are not authorized"
        script += "to edit this restaurant. Please create your own restaurant"
        script += "in order to edit.');}</script><body"
        script += "onload='myFunction()'>"
        return script
    if request.method == 'POST':
        deleteItems = session.query(Items).filter_by(
            categories=deleteCategorie).all()
        for i in deleteItems:
            session.delete(i)
            session.commit()
        session.delete(deleteCategorie)
        session.commit()
        return redirect(url_for('categoriesPage'))
    else:
        return render_template('deleteCategories.html',
                               deleteCategorie=deleteCategorie)


@app.route('/categories/<int:categories_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItems(categories_id, item_id):
    '''
        Delete an item
    '''
    if 'username' not in login_session:
        return redirect('/login')
    deleteItem = session.query(Items).filter_by(id=item_id).one()
    if(deleteItem.user_id != login_session['gplus_id']):
        script = "<script>function myFunction() {alert('You are not authorized"
        script += "to edit this restaurant. Please create your own restaurant"
        script += "in order to edit.');}</script><body"
        script += "onload='myFunction()'>"
        return script
    if request.method == 'POST':
        cat_id = deleteItem.categories.id
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('itemsPage', categories_id=cat_id))
    else:
        return render_template('deleteItem.html', deleteItem=deleteItem)


@app.route('/categories/<int:categories_id>/JSON/')
def itemCategoriesJSON(categories_id):
    '''
        Create json view for all items in a categories
    '''
    categories = session.query(Categories).filter_by(id=categories_id).one()
    items = session.query(Items).filter_by(categories=categories).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/categories/<int:categories_id>/<int:items_id>/JSON')
def itemsJSON(categories_id, items_id):
    '''
        Create json view for an item
    '''
    item = session.query(Items).filter_by(id=items_id).one()
    return jsonify(items=item.serialize)


@app.route('/categories/JSON/')
def categoriesJSON():
    '''
        Create json view for all categories
    '''
    categories = session.query(Categories).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/login')
def showLogin():
    '''
        Allow user to login via google
    '''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''
        Gconnect code
    '''
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'json/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' \" style = "width: 300px; '
    output += ' height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;\"> '
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    '''
        disconnect from google login.
    '''
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Main program
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
