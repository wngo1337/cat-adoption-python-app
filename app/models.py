from datetime import datetime as dt
from datetime import timezone
import enum
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from .app_components import db


class CatRarity(enum.Enum):
    COMMON = "common"
    RARE = "rare"


class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    personality = db.Column(db.String(255), nullable=False)
    appearance = db.Column(db.String(255), nullable=False)
    power_level = db.Column(db.Integer, nullable=False)
    rarity = db.Column(Enum(CatRarity), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.Text, nullable=False)
    latest_adoption_id = db.Column(db.Integer, db.ForeignKey("adoption.id"))

    # define relationship to the Adoption table
    adoptions = db.relationship(
        "Adoption", back_populates="cat", foreign_keys="[Adoption.cat_id]"
    )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    cats_adopted = db.relationship(
        "Adoption", back_populates="adopter", foreign_keys="[Adoption.user_id]"
    )

    def __repr__(self):
        return f"<Cat {self.name}>"


class AdoptionMethod(enum.Enum):
    LEGAL_ADOPTION = "legal adoption"
    STOLEN = "stolen"


class Adoption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    previous_owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    cat_id = db.Column(db.Integer, db.ForeignKey("cat.id"), nullable=False)
    date = db.Column(db.DateTime, default=dt.now(timezone.utc), nullable=False)
    method = db.Column(Enum(AdoptionMethod), nullable=False)

    # Define the relationship to Cat table with explicit foreign keys
    adopter = db.relationship(
        "User", back_populates="cats_adopted", foreign_keys=[user_id]
    )
    cat = db.relationship("Cat", back_populates="adoptions", foreign_keys=[cat_id])


class DisplayCat(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    personality = db.Column(db.String(255), nullable=False)
    appearance = db.Column(db.String(255), nullable=False)
    power_level = db.Column(db.Integer, nullable=False)
    rarity = db.Column(Enum(CatRarity), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.Text, nullable=False)
    latest_adoption_id = db.Column(db.Integer, db.ForeignKey("adoption.id"))
