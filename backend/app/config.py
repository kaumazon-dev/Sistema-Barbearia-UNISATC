import os

def normalizar_url_banco(url):
    if url is None:
        return 
    busca = "postgres://"
    if url.startswith(busca):
        return "postgresql://" + url[len(busca):]
    else:
        return url

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(os.environ.get("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(os.environ.get("DATABASE_URL_TEST"))

class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    def __init__(self):
        super().__init__()

        if not self.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError("Variavel SQLALCHEMY_DATABASE_URI com valor nulo")
        if not self.SECRET_KEY:
            raise RuntimeError("Variavel SECRET_KEY com valor nulo")

configuracoes = {"dev": DevConfig, "prod":ProdConfig, "test":TestConfig}
