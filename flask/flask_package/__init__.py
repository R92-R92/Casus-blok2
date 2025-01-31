from flask import Flask
from datetime import datetime
from logging import DEBUG
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = b'\xd9\x88\xa0\x7f5`\xb3\xe0'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.logger.setLevel(DEBUG)
app.app_context().push()

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)



from flask_package import routes