import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Categories, Base, Items


def readJson(filename):
    data = json.load(open(filename))
    return data

def createCategorie(cat):
    cate = Categories(name=cat["name"])
    return cate

def createItem(item):
    cat = session.query(Categories).filter_by(name=item["categories"]).first()
    cate_item = Items(name=item["name"], description=item["description"], categories=cat)
    return cate_item

# connect to database
engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

data_categories = readJson("json/categories.json")
cates = data_categories["categories"]
for cate in cates:
    tempCategories = createCategorie(cate)
    try:
        session.add(tempCategories)
        session.commit()
    except:
        session.rollback()
        print "Unable to insert row", tempCategories.name

data_items = readJson("json/items.json")
cat_items = data_items["items"]
for cate_item in cat_items:
    temp_item = createItem(cate_item)
    try:
        session.add(temp_item)
        session.commit()
    except:
        session.rollback()
        print "Unable to insert row", temp_item.name
