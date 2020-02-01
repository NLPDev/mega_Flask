from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
babel = Babel(app)

from app import routes, models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')


    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMIN'], subject='Microblog Failure',
                credentials=auth, secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # if not os.path.exists('logs'):
        #     os.mkdir('logs')
        # file_handler = RotatingFileHandler('logs/mega.log', maxBytes=10240, backupCount=10)
        # file_handler.setFormatter(logging.Formatter(
        #     '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        # file_handler.setLevel(logging.INFO)
        # app.logger.addHandler(file_handler)

        # app.logger.setLevel(logging.INFO)
        # app.logger.info('Mega startup')

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    