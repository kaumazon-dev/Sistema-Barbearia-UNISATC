from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

migrate = Migrate()
jwt = JWTManager()
cors = CORS()
db = SQLAlchemy()
