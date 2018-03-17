import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Categories, Base, Items


# Read json file
def readJson(filename):
    data = json.load(open(filename))
    return data


# create new categories
def createCategorie(cat):
    cate = Categories(name=cat["name"])
    return cate


# create new items
def createItem(item):
    cat = session.query(Categories).filter_by(name=item["categories"]).first()
    cate_item = Items(name=item["name"],
                      description=item["description"], categories=cat)
    return cate_item

# connect to database
engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Read json file and commit it into the database
data_categories = readJson("json/categories.json")
cates = data_categories["categories"]
# Extract data from json file.
for cate in cates:
    tempCategories = createCategorie(cate)
    try:
        session.add(tempCategories)
        session.commit()
    except:
        session.rollback()
        print "Unable to insert row", tempCategories.name

# Todo: This code is very similar to previous block
#       This code might be better to put into a function
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
