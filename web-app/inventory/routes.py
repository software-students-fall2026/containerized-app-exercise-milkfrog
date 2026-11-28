"""Inventory pages and food form handling."""

from bson import ObjectId
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from itsdangerous import BadSignature, URLSafeSerializer

from inventory import repository

inventory = Blueprint("inventory", __name__, url_prefix="/foods")


def get_db():
    """Return the MongoDB database shared by the Web modules."""
    return current_app.extensions["expirymate_db"]


@inventory.app_context_processor
def food_options():
    """Make common food fields available to scan and inventory templates."""
    return {"labels": repository.LABELS, "places": repository.PLACES}


@inventory.get("/")
def index():
    """Show the current food inventory with optional filters."""
    place = request.args.get("place", "")
    word = request.args.get("q", "").strip()[:100]
    order = request.args.get("order", "asc")
    if place and place not in repository.PLACES or order not in {"asc", "desc"}:
        abort(400, "Choose a valid storage location and date order.")
    foods = repository.find(
        get_db(), place=place, word=word, descending=order == "desc"
    )
    reminder_for = current_app.config["INVENTORY_REMINDER"]
    return render_template(
        "inventory.html",
        foods=foods,
        place=place,
        q=word,
        order=order,
        reminder_for=reminder_for,
    )


def save_new_food(values, *, request_id):
    """Save either entry form through the same inventory workflow."""
    repository.add(get_db(), values, request_id=request_id)
    flash("Food added to your inventory.", "success")
    return redirect(url_for("inventory.index"), code=303)


@inventory.route("/new", methods=["GET", "POST"])
def create():
    """Create a food from the manual entry form."""
    signer = URLSafeSerializer(current_app.secret_key, salt="manual-food")
    values, error = {}, None
    if request.method == "POST":
        submission = request.form.get("submission", "")
        try:
            key = signer.loads(submission)
        except BadSignature:
            abort(400, "Reload the form and try again.")
        values = request.form
        try:
            return save_new_food(values, request_id=key)
        except ValueError as failure:
            error = str(failure)
    else:
        submission = signer.dumps(str(ObjectId()))
    return render_template(
        "food_form.html",
        title="Add food manually",
        values=values,
        error=error,
        submission=submission,
    ), (400 if error else 200)


@inventory.route("/<key>/edit", methods=["GET", "POST"])
def update(key):
    """Edit a food while preserving its status and linked scan."""
    db = get_db()
    values = repository.get(db, key)
    if values is None:
        abort(404, "This food could not be found.")
    error = None
    if request.method == "POST":
        values = request.form
        try:
            updated = repository.edit(
                db,
                key,
                {
                    field: values.get(field)
                    for field in ("name", "date", "label", "place")
                },
            )
        except ValueError as failure:
            error = str(failure)
        else:
            if not updated:
                abort(404, "This food could not be found.")
            flash("Food updated.", "success")
            return redirect(url_for("inventory.index"), code=303)
    return render_template(
        "food_form.html", title="Edit food", values=values, error=error
    ), (400 if error else 200)
