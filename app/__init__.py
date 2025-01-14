from flask import Flask
from .routes import routes
from .models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri_here'
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    db.init_app(app)

    app.register_blueprint(routes)

    return app