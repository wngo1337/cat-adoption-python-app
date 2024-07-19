from flask import session
from .app_components import db

from .models import Cat, DisplayCat
from flask import current_app as app
from flask_apscheduler import APScheduler, scheduler
import random

NUM_CATS_TO_DISPLAY = 8


def update_display_cats(app):
    with app.app_context():
        all_cats = Cat.query.all()
        random.shuffle(all_cats)
        new_display_cats = all_cats[:NUM_CATS_TO_DISPLAY]

        # wipe the table before adding new cats
        DisplayCat.query.delete()
        db.session.commit()
        print("we deleted cats in display cat, buh")

        for cat in new_display_cats:
            display_cat = DisplayCat(
                id=cat.id,
                name=cat.name,
                personality=cat.personality,
                appearance=cat.appearance,
                power_level=cat.power_level,
                description=cat.description,
                image_path=cat.image_path,
                latest_adoption_id=cat.latest_adoption_id,
            )
            db.session.add(display_cat)
        db.session.commit()


"""
Scan the display_cat table for the adopted cat and update accordingly so that
changes show immediately in the UI.

This job must run after every adoption because the display_cat table has no
knowledge of the cat table.
"""


def update_display_after_adoption(adopted_cat):
    display_cat = DisplayCat.query.get(adopted_cat.id)
    if display_cat:
        display_cat.latest_adoption_id = adopted_cat.latest_adoption_id
        db.session.commit()
