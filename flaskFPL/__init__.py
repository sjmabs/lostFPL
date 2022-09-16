from flask import Flask
from flaskFPL.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from flaskFPL.main.routes import main
    app.register_blueprint(main)
    from flaskFPL.errors.handlers import errors
    app.register_blueprint(errors)

    return app

