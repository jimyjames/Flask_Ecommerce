import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    FLASKY_ADMIN = os.environ.get("FLASKY_ADMIN")
    MAIL_PORT = 587  # int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS").lower() in ["true", "1", "yes"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    FLASKY_MAIL_SUBJECT_PREFIX = os.environ.get("FLASKY_MAIL_SUBJECT_PREFIX")
    FLASKY_MAIL_SENDER = os.environ.get("FLASKY_MAIL_SENDER")
    MAIL_SENDER = os.environ.get("MAIL_SENDER")
    MAIL_SUBJECT_PREFIX = os.environ.get("MAIL_SUBJECT_PREFIX")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    ).lower() in ["true", "1", "yes"]
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    IMAGE_UPLOAD = os.environ.get("IMAGE_UPLOAD")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # SQLALCHEMY_DATABASE_URI = "sqlite:///myshop.db"
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DATABASE_HOSTNAME=os.environ.get("DATABASE_HOSTNAME")
    DATABASE_PORT=5432
    DATABASE_PASSWORD=os.environ.get("DATABASE_PASSWORD")
    DATABASE_NAME=os.environ.get("DATABASE_NAME")
    DATABASE_USERNAME=os.environ.get("DATABASE_USERNAME")
    SQLALCHEMY_DATABASE_URI=f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"




config = {"development": DevelopmentConfig, "default": DevelopmentConfig}
