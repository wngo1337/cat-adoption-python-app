import os
from flask import Flask, session
from flask_session import Session
from flask_login import LoginManager
from flask_migrate import Migrate

# from flask_sqlalchemy import SQLAlchemy
from .app_components import db, sess, task_scheduler

from .jobs import update_display_cats

from .populate_cats import populate_cat_table

import redis


class Config:
    SCHEDULER_API_ENABLED = True


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY")
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = redis.from_url("redis://localhost:6379")

    app.config.from_object(__name__)
    app.config.from_object(Config())
    sess.init_app(app)

    task_scheduler.init_app(app)
    task_scheduler.add_job(
        id="random cat task",
        func=update_display_cats,
        trigger="interval",
        seconds=60,
        kwargs={"app": app},
    )
    task_scheduler.start()

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "Data/adoption_agency.db"
    )

    db.init_app(app)
    populate_cat_table(app)

    login_manager = LoginManager()
    login_manager.login_view = "authentication.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .authentication import authentication as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    migrate = Migrate(app, db)

    return app
