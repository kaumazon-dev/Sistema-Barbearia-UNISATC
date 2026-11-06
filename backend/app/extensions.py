from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

migrate = Migrate()
jwt = JWTManager()
cors = CORS()
db = SQLAlchemy()
# Sem default_limits: so as rotas marcadas com @limiter.limit tem limite.
# Armazenamento e liga/desliga vem do app.config (RATELIMIT_*).
limiter = Limiter(key_func=get_remote_address)
