from flask import Flask
from dotenv import load_dotenv
from db import db
from models import User, WeightTracking
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/run_sphere'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = os.getenv('SECRET_KEY')
db.init_app(app)

with app.app_context():
    db.create_all() 

from routes.auth import auth
from routes.profile import profile 

app.register_blueprint(auth)
app.register_blueprint(profile)

if __name__ == '__main__':
    app.run(debug=True)