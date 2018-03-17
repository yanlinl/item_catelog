from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from db_setup import Categories, Base, Items
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)



CLIENT_ID = json.loads(
    open('json/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categories/')
def categoriesPage():
    categories = session.query(Categories).all()
    latest_10 = session.query(Items).order_by(Items.id.desc()).limit(10)
    return render_template("catelogs.html", categories=categories, latest_10=latest_10)

@app.route('/categories/<int:categories_id>/')
def itemsPage(categories_id):
    categories = session.query(Categories).all()
    items_list = session.query(Items).filter_by(categories_id=categories_id).all()
    categorie = session.query(Categories).filter_by(id=categories_id).first()
    return render_template("itemsPage.html", categories=categories, categorie=categorie, items_list=items_list)


@app.route('/categories/<int:categories_id>/<int:item_id>/')
def itemPage(categories_id, item_id):
    item = session.query(Items).filter_by(categories_id=categories_id).first()
    return render_template("itemPage.html", item=item)

@app.route('/categories/newCategories/', methods=['GET', 'POST'])
def newCategories():
    if request.method == 'POST':
        newCategorie = Categories(name=request.form['name'])
        session.add(newCategorie)
        session.commit()
        return redirect(url_for('categoriesPage'))
    else:
        return render_template('newCatelogs.html')

@app.route('/categories/<int:categories_id>/newItem/', methods=['GET', 'POST'])
def newItem(categories_id):
    if request.method == 'POST':
        newCategorie = Items(name=request.form['name'], description=request.form['description'],categories=session.query(Categories).filter_by(id=categories_id).first())
        session.add(newCategorie)
        session.commit()
        return redirect(url_for('itemsPage', categories_id=categories_id))
    else:
        return render_template('newItem.html', categories_id=categories_id)


@app.route('/categories/<int:categories_id>/edit/', methods=['GET', 'POST'])
def editCategories(categories_id):
    editCategories = session.query(Categories).filter_by(id=categories_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editCategories.name=request.form['name']
            session.add(editCategories)
            session.commit()
            return redirect(url_for('itemsPage', categories_id=editCategories.id))
    else:
        return render_template('editCategories.html', editCategories=editCategories)

@app.route('/categories/<int:categories_id>/<int:items_id>/edit/', methods=['GET', 'POST'])
def editItems(categories_id, items_id):
    editItem = session.query(Items).filter_by(id=items_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editItem.name=request.form['name']
            editItem.description=request.form['description']
            session.add(editItem)
            session.commit()
            return redirect(url_for('itemPage', categories_id=editItem.categories.id, item_id=editItem.id))
    else:
        return render_template('editItem.html', editItem=editItem)

@app.route('/categories/<int:categories_id>/delete/', methods=['GET', 'POST'])
def deleteCategories(categories_id):
    deleteCategorie = session.query(Categories).filter_by(id=categories_id).one()
    if request.method == 'POST':
        deleteItems = session.query(Items).filter_by(categories=deleteCategorie).all()
        for i in deleteItems:
            session.delete(i)
            session.commit()
        session.delete(deleteCategorie)
        session.commit()
        return redirect(url_for('categoriesPage'))
    else:
        return render_template('deleteCategories.html', deleteCategorie=deleteCategorie)


@app.route('/categories/<int:categories_id>/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItems(categories_id, item_id):
    deleteItem = session.query(Items).filter_by(id=item_id).one()
    if request.method == 'POST':
        cat_id = deleteItem.categories.id
        session.delete(deleteItem)
        session.commit()
        print "bere"
        return redirect(url_for('itemsPage', categories_id=cat_id))
    else:
        return render_template('deleteItem.html', deleteItem=deleteItem)

@app.route('/categories/<int:categories_id>/JSON/')
def itemCategoriesJSON(categories_id):
    categories = session.query(Categories).filter_by(id=categories_id).one()
    items = session.query(Items).filter_by(categories=categories).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/categories/<int:categories_id>/<int:items_id>/JSON')
def itemsJSON(categories_id, items_id):
    item = session.query(Items).filter_by(id=items_id).one()
    return jsonify(items=item.serialize)

@app.route('/categories/JSON/')
def categoriesJSON():
    categories = session.query(Categories).all()
    return jsonify(Categories=[i.serialize for i in categories])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port=8000)
