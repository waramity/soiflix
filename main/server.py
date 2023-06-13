from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import csv
from datetime import datetime
from alembic import op
from flask_mobility import Mobility


# init SQLAlchemy so we can use it later in our models

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
Mobility(app)

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)


@migrate.configure
def configure_alembic(config):
    # modify config object
    return config
