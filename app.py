
from flask import Flask, render_template, request
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from pathlib import Path
import json

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
CATALOG_FILE = BASE_DIR / "data" / "catalog.json"


def load_catalog():
    with open(CATALOG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def home():
    return render_template(
        "index.html",
        products=[],
        message=None
    )


@app.route("/search", methods=["POST"])
def search():
    uploaded = request.files.get("image")

    if not uploaded or not uploaded.filename:
        return render_template(
            "index.html",
            products=[],
            message="Please upload a product screenshot."
        )

    try:
        image = Image.open(BytesIO(uploaded.read()))
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        return render_template(
            "index.html",
            products=[],
            message="Invalid image. Please upload a valid picture."
        )

    category = request.form.get("category", "all")
    budget_text = request.form.get("budget", "").strip()

    try:
        budget = float(budget_text) if budget_text else None

        if budget is not None and budget < 0:
            raise ValueError

    except ValueError:
        return render_template(
            "index.html",
            products=[],
            message="Please enter a valid non-negative budget."
        )

    try:
        catalog = load_catalog()

        if not isinstance(catalog, list):
            raise ValueError("Catalogue must be a list")

    except (OSError, json.JSONDecodeError, ValueError):
        return render_template(
            "index.html",
            products=[],
            message="Catalogue data could not be loaded."
        )

    # Filter by category
    products = [
        product for product in catalog
        if category == "all"
        or product.get("category") == category
    ]

    # Filter by maximum budget
    if budget is not None:
        products = [
            product for product in products
            if isinstance(product.get("price"), (int, float))
            and not isinstance(product.get("price"), bool)
            and product["price"] <= budget
        ]

    # Display up to five catalogue products
    products = products[:5]

    results = []

    for product in products:
        image_path = product.get("image", "")

        results.append({
            **product,
            "image_url": "/" + image_path.lstrip("/"),
            "difference": product.get(
                "description",
                "Product details unavailable"
            ),
            "confidence": "Not yet visually matched"
        })

    if results:
        message = (
            "These products match your filters. "
            "Visual similarity has not yet been evaluated."
        )
    else:
        message = (
            "No products match your filters. "
            "Try another category or increase your budget."
        )

    return render_template(
        "index.html",
        products=results,
        message=message
    )


@app.errorhandler(413)
def file_too_large(error):
    return (
        "Image is too large. Please upload an image under 5 MB.",
        413
    )


if __name__ == "__main__":
    app.run(debug=True)
