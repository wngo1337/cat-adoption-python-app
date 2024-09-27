# This method populates the cat table with all known cats on app setup
# Note: we do not have a solution for when cat table has existing entries

from .app_components import db
from flask import current_app as app
from .models import Cat, CatRarity

initial_cats = [
    (
        108,
        "Tubbs",
        "Finicky Feaster",
        "Fluffy",
        130,
        CatRarity.RARE,
        "BIG ol cat but placeholder",
        "Images/tubbs.png",
    ),
    (
        104,
        "Saint Purrtrick",
        "Awe-inspiring",
        "Ethereal",
        222,
        CatRarity.RARE,
        "Awe-inspiring placeholder bro",
        "Images/saint_purrtrick.png",
    ),
    (
        107,
        "Conductor Whiskers",
        "Vigilant",
        "Railway Uniform",
        50,
        CatRarity.RARE,
        "CUTIE placeholder",
        "Images/conductor_whiskers.png",
    ),
    (
        105,
        "Ms. Fortune",
        "Charismatic",
        "Gold",
        20,
        CatRarity.RARE,
        "Waving placeholder",
        "Images/ms_fortune.png",
    ),
    (
        114,
        "Sassy Fran",
        "Enthusiastic",
        "Waitress",
        180,
        CatRarity.RARE,
        "Classy placeholder",
        "Images/sassy_fran.png",
    ),
    (
        102,
        "Xerxes IX",
        "Regal",
        "Persian",
        70,
        CatRarity.RARE,
        "Regal placeholder",
        "Images/xerxes_ix.png",
    ),
    (
        106,
        "Bob the Cat",
        "Outdoorsy",
        "Adventurer",
        40,
        CatRarity.RARE,
        "Adventurer placeholder",
        "Images/bob_the_cat.png",
    ),
    (
        101,
        "Senor Don Gato",
        "Scheming",
        "Fisherman",
        30,
        CatRarity.RARE,
        "Scheming placeholder",
        "Images/senor_don_gato.png",
    ),
    (
        109,
        "Mr. Meowgi",
        "Mentoring",
        "Ronin",
        250,
        CatRarity.RARE,
        "Mentor placeholder",
        "Images/mr_meowgi.png",
    ),
    (
        103,
        "Chairman Meow",
        "Boorish",
        "Camouflage",
        111,
        CatRarity.RARE,
        "Boorish placeholder",
        "Images/chairman_meow.png",
    ),
    (
        110,
        "Lady Meow-Meow",
        "Diva",
        "American Shorthair",
        100,
        CatRarity.RARE,
        "Diva placeholder",
        "Images/lady_meow_meow.png",
    ),
    (
        111,
        "Guy Furry",
        "Artisan",
        "Apron",
        30,
        CatRarity.RARE,
        "Artisan placeholder",
        "Images/guy_furry.png",
    ),
    (
        112,
        "Kathmandu",
        "Refined",
        "Hunting Coat",
        150,
        CatRarity.RARE,
        "Refined placeholder",
        "Images/kathmandu.png",
    ),
    (
        113,
        "Ramses the Great",
        "Riddler",
        "Sphinx",
        230,
        CatRarity.RARE,
        "Riddler placeholder",
        "Images/ramses_the_great.png",
    ),
    (
        115,
        "Billy the Kitten",
        "Nihilistic",
        "Western Wear",
        250,
        CatRarity.RARE,
        "Nihilistic placeholder",
        "Images/billy_the_kitten.png",
    ),
    (
        116,
        "Frosty",
        "Sensitive",
        "Straw Coat",
        5,
        CatRarity.RARE,
        "Sensitive placeholder",
        "Images/frosty.png",
    ),
]


def populate_cat_table(app):
    with app.app_context():
        db.create_all()

        # Returns a list of tuples, so we need to extract id values
        existing_cat_ids_raw = Cat.query.with_entities(Cat.id).all()
        existing_cat_ids = [id_[0] for id_ in existing_cat_ids_raw]

        cats_to_add = [cat for cat in initial_cats if cat[0] not in existing_cat_ids]

        if cats_to_add:
            print(cats_to_add)
            db.session.bulk_save_objects(
                Cat(
                    id=id_,
                    name=name,
                    personality=personality,
                    appearance=appearance,
                    power_level=power_level,
                    rarity=rarity,
                    description=description,
                    image_path=image_path,
                )
                for id_, name, personality, appearance, power_level, rarity, description, image_path in cats_to_add
            )
        db.session.commit()
