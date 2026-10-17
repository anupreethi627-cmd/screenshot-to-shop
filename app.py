
from flask import Flask, render_template, request
from PIL import Image, UnidentifiedImageError
from io import BytesIO

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


@app.route("/")
def home():
    return render_template("index.html", products=[], message=None)


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
            message="This image could not be opened. Please try another."
        )

    return render_template(
        "index.html",
        products=[],
        message=(
            "Image uploaded successfully! Catalogue matching "
            "will be added in the next step."
        )
    )


if __name__ == "__main__":
    app.run(debug=True)
