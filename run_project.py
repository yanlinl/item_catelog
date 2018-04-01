# -*- coding: utf-8 -*-
""" This is the main project file.

"""
import os.path

# Stores db name
DB_NAME = "categories.db"

# Start the program.
if os.path.isfile(DB_NAME):
    print "Database alrady exist, start server"
    os.system('python item_categories.py')
else:
    print "Database does not exist, setup database..."
    os.system('python db_setup.py')
    os.system('python populate_db.py')
    print "Database setup successful, start server"
    os.system('python item_categories.py')