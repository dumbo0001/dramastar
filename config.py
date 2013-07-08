import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + 'app.db'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

hdzoneconfig = { 'username' : 'xxx', 'password' : 'xxx' }