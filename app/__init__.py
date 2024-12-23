from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate #flask migrate tracks the database migration, which are changes to the structure of the database
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail=Mail(app)

from app import routes, models, errors
