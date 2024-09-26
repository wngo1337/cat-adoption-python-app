from datetime import datetime as dt
from datetime import timezone
from flask import (
    render_template,
    request,
    url_for,
    flash,
    redirect,
    Blueprint,
    session,
    current_app as app,
)
from flask_login import login_required, current_user
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound

from .models import Adoption, AdoptionMethod, Cat, User, DisplayCat
from .app_components import db
from .description_generator import DescriptionGenerator
from .jobs import update_display_after_adoption
import random

main = Blueprint("main", __name__)


@main.route("/")
def index():
    # Execute the query and fetch the results
    cat_info_query = (
        db.session.query(DisplayCat, User, Adoption.method)
        .outerjoin(Adoption, DisplayCat.latest_adoption_id == Adoption.id)
        .outerjoin(User, User.id == Adoption.user_id)
        .all()
    )

    return render_template("index.html", cat_info=cat_info_query)


@main.route("/profile")
@login_required
def profile():
    # Query to retrieve the cats and adoption information for cats that the current user owns
    owned_cats_and_adoptions = (
        db.session.query(Cat, Adoption)
        .join(Adoption, Cat.latest_adoption_id == Adoption.id)
        .filter(Adoption.user_id == current_user.id)
        .options(db.joinedload(Cat.adoptions))  # Load the associated adoptions
        .all()
    )

    # Format dates in the query result
    formatted_adoptions = [
        (cat, adoption, adoption.date.strftime("%B %d, %Y %I:%M %p"))
        for cat, adoption in owned_cats_and_adoptions
    ]

    return render_template(
        "profile.html", name=current_user.username, owned_cats=formatted_adoptions
    )


@main.route("/cat/<int:cat_id>/")
def cat(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    """
    NOTE: latest_adoption_id will not be set yet if cat is not adopted
    Does not cause error now, but gives SAWarning that it could if SQLAlchemy
    changes how this case is handled in the future
    """
    try:
        adoption_record = Adoption.query.get(cat.latest_adoption_id)
    except NoResultFound:
        adoption_record = None
    prompt = DescriptionGenerator.create_formatted_prompt(
        DescriptionGenerator.DescriptionType.CAT_SUMMARY,
        [cat.name, cat.personality, cat.appearance],
    )
    cat_summary = DescriptionGenerator.generate_response(prompt)

    return render_template(
        "cat.html", cat=cat, adoption_record=adoption_record, cat_summary=cat_summary
    )


@main.route("/adopt/<int:cat_id>")
@login_required
def adopt(cat_id):
    cat = Cat.query.get_or_404(cat_id)
    last_adoption = Adoption.query.filter_by(id=cat.latest_adoption_id).first()
    if last_adoption:
        last_owner = User.query.get(last_adoption.user_id)

        prompt = DescriptionGenerator.create_formatted_prompt(
            DescriptionGenerator.DescriptionType.CONTEMPLATE_STEAL,
            [
                current_user.username,
                cat.name,
                last_owner.username,
                cat.personality,
                cat.appearance,
            ],
        )
    else:
        last_adoption = None
        last_owner = None

        prompt = DescriptionGenerator.create_formatted_prompt(
            DescriptionGenerator.DescriptionType.CAT_DESCRIPTION,
            [cat.name, cat.personality, cat.appearance],
        )

    description = DescriptionGenerator.generate_response(prompt)

    return render_template(
        "adopt.html",
        cat=cat,
        last_adoption=last_adoption,
        last_owner=last_owner,
        description=description,
    )


@main.route("/adopt/<int:cat_id>", methods=["POST"])
@login_required
def adopt_post(cat_id):
    adoption_cat = Cat.query.get_or_404(cat_id)
    adoption_record = Adoption(
        user_id=current_user.id,
        cat_id=adoption_cat.id,
        date=dt.now(timezone.utc),
        method=AdoptionMethod.LEGAL_ADOPTION,
    )
    db.session.add(adoption_record)
    db.session.commit()

    cat_to_update = Cat.query.get_or_404(cat_id)
    cat_to_update.latest_adoption_id = adoption_record.id
    db.session.commit()

    # update the index page cat display after successful adoption
    update_display_after_adoption(cat_to_update)

    prompt = DescriptionGenerator.create_formatted_prompt(
        DescriptionGenerator.DescriptionType.CAT_ADOPT,
        [
            current_user.username,
            cat_to_update.name,
            cat_to_update.personality,
            cat_to_update.appearance,
        ],
    )

    description = DescriptionGenerator.generate_response(prompt)

    return render_template(
        "successful_adopt.html",
        cat=cat_to_update,
        adopter=current_user.username,
        description=description,
    )


@main.route("/steal/<int:cat_id>", methods=["POST"])
@login_required
def steal_post(cat_id):
    steal_cat = Cat.query.get_or_404(cat_id)
    previous_adoption_record = Adoption.query.get_or_404(steal_cat.latest_adoption_id)
    previous_owner = User.query.get_or_404(previous_adoption_record.user_id)
    adoption_record = Adoption(
        user_id=current_user.id,
        previous_owner_id=previous_owner.id,
        cat_id=steal_cat.id,
        date=dt.now(timezone.utc),
        method=AdoptionMethod.STOLEN,
    )
    db.session.add(adoption_record)
    db.session.commit()

    cat_to_update = Cat.query.filter_by(id=cat_id).first()
    cat_to_update.latest_adoption_id = int(adoption_record.id)

    db.session.commit()

    prompt = DescriptionGenerator.create_formatted_prompt(
        DescriptionGenerator.DescriptionType.CAT_STEAL,
        [
            current_user.username,
            cat_to_update.name,
            previous_owner.username,
            cat_to_update.personality,
            cat_to_update.appearance,
        ],
    )
    description = DescriptionGenerator.generate_response(prompt)

    return render_template(
        "successful_steal.html", cat=cat_to_update, description=description
    )


@main.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        cat_id = int(request.form["id"])
        name = request.form["name"]
        personality = request.form["personality"]
        appearance = request.form["appearance"]
        power_level = int(request.form["power_level"])
        rarity = request.form["rarity"]
        description = request.form["description"]
        image_path = request.form["image_path"]
        new_cat = Cat(
            id=cat_id,
            name=name,
            personality=personality,
            appearance=appearance,
            power_level=power_level,
            rarity=rarity,
            description=description,
            image_path=image_path,
        )
        db.session.add(new_cat)
        db.session.commit()

        flash(f"You have successfully added {new_cat.name} to the agency!")
        return redirect(url_for("main.index"))
    return render_template("create.html")


@main.route("/<int:cat_id>/edit", methods=("GET", "POST"))
def edit(cat_id):
    existing_cat = Cat.query.get_or_404(cat_id)
    if request.method == "POST":

        cat_id = int(request.form["id"])
        name = request.form["name"]
        personality = request.form["personality"]
        appearance = request.form["appearance"]
        power_level = int(request.form["power_level"])
        description = request.form["description"]
        image_path = request.form["image_path"]

        existing_cat.id = cat_id
        existing_cat.name = name
        existing_cat.personality = personality
        existing_cat.appearance = appearance
        existing_cat.power_level = power_level
        existing_cat.description = description
        existing_cat.image_path = image_path

        db.session.add(existing_cat)
        db.session.commit()

        flash(f"You have successfully edited {existing_cat.name}'s information!")
        return redirect(url_for("main.index"))
    return render_template("edit.html", cat=existing_cat)


@main.route("/<int:cat_id>/delete", methods=("POST",))
def delete(cat_id):
    cat_to_delete = Cat.query.get_or_404(cat_id)
    db.session.delete(cat_to_delete)
    db.session.commit()

    flash(f"You have successfully deleted {cat_to_delete.name} from the agency!")
    return redirect(url_for("main.index"))
    # return render_template('edit.html', cat=cat_to_delete)


@main.route("/cat/<int:cat_id>/interact", methods=["POST"])
def interact(cat_id):
    is_new_conversation_raw_val = request.form["is-new-conversation"]
    is_new_conversation = (
        True if is_new_conversation_raw_val.lower() == "true" else False
    )
    user_input = request.form["question"]
    cat = Cat.query.get_or_404(cat_id)
    user_cat_session_key = f"{current_user.id}_{cat.name}_context"

    if is_new_conversation:
        # Conversations should start from scratch each time to keep things
        # interesting
        # Plus, it helps us to save on the limited storage space on our VM 🤣
        session.pop(user_cat_session_key, None)
        prompt = DescriptionGenerator.create_formatted_prompt(
            DescriptionGenerator.DescriptionType.CAT_WISDOM,
            [cat.name, cat.personality, cat.appearance],
        )
        context = [{"role": "user", "parts": [prompt]}]

    else:
        # Retrieve stored chat history
        user_cat_history = session[user_cat_session_key]
        context = user_cat_history

    response, new_context = DescriptionGenerator.generate_response_from_history(
        context, user_input
    )

    # Store updated chat context in session for accessability from jinja call
    # template call
    session[user_cat_session_key] = new_context

    # Assumes that Gemini correctly generates output with specified tags 🥲
    # TODO: figure out how to get Gemini to consistently generate endline chars
    # where I want them so I can split on them to reliably break into
    # paragraphs
    line_break_tag = r"NEWPARAGRAPH"
    response_in_paragraphs = response.split(line_break_tag)

    return render_template(
        "interact.html",
        is_new_conversation=is_new_conversation,
        cat=cat,
        cat_wisdom=response_in_paragraphs,
        question=user_input,
        context=new_context,
    )


@main.route("/leaderboard")
def leaderboard():
    top_steal_users_statement = (
        select(Adoption.user_id, Adoption.method, func.count().label("num_steals"))
        .filter(Adoption.method == AdoptionMethod.STOLEN)
        .group_by(Adoption.user_id)
        .order_by(func.count().desc())
    )

    # Execute the SELECT statement
    steal_query_result = db.session.execute(top_steal_users_statement)
    steal_leaders = steal_query_result.fetchall()

    top_adopt_users_statement = (
        select(Adoption.user_id, Adoption.method, func.count().label("num_adoptions"))
        .filter(Adoption.method == AdoptionMethod.LEGAL_ADOPTION)
        .group_by(Adoption.user_id)
        .order_by(func.count().desc())
    )

    adopt_query_result = db.session.execute(top_adopt_users_statement)
    adoption_leaders = adopt_query_result.fetchall()

    user_ids_to_names = {}
    user_info = User.query.all()
    for user in user_info:
        user_ids_to_names[user.id] = user.username

    return render_template(
        "leaderboard.html",
        steal_leaders=steal_leaders,
        adoption_leaders=adoption_leaders,
        user_ids_to_names=user_ids_to_names,
    )


@main.route("/steal-log")
def steal_log():
    stolen_cat_adoption_logs = Adoption.query.filter_by(
        method=AdoptionMethod.STOLEN
    ).all()
    # Format dates in the query result
    adoption_logs_with_formatted_dates = [
        (adoption, adoption.date.strftime("%B %d, %Y %I:%M %p"))
        for adoption in stolen_cat_adoption_logs
    ]

    # Doing the double join to fetch user and cat names via ID seems overly complex, so just construct a dictionary to retrieve them when needed
    cat_ids_to_names = {}
    cat_info = Cat.query.all()
    for cat in cat_info:
        cat_ids_to_names[cat.id] = cat.name

    user_ids_to_names = {}
    user_info = User.query.all()
    for user in user_info:
        user_ids_to_names[user.id] = user.username

    return render_template(
        "steal_log.html",
        stolen_cat_info=adoption_logs_with_formatted_dates,
        user_ids_to_usernames=user_ids_to_names,
        cat_ids_to_names=cat_ids_to_names,
    )


@main.route("/about")
def about():
    return render_template("about.html")
