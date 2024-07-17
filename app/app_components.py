from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()
sess = Session()
task_scheduler = APScheduler()
