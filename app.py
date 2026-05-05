from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db():
    db = Path(__file__).parent / "VulkanuSaraksts"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/vulkani")
def vulkani():
    conn = get_db()

    vulkani = conn.execute("""
        SELECT Vulkani.*,
               Vulkani_kontinenti.continent,
               Vulkani_tips.type,
               Vulkani_aktivitate.eruption_reason
        FROM Vulkani
        LEFT JOIN Vulkani_kontinenti
            ON Vulkani.id_continent = Vulkani_kontinenti.id
        LEFT JOIN Vulkani_tips
            ON Vulkani.id_type = Vulkani_tips.id
        LEFT JOIN Vulkani_aktivitate
            ON Vulkani.id_activity = Vulkani_aktivitate.id
    """).fetchall()

    conn.close()
    return render_template("vulkani.html", vulkani=vulkani)


@app.route("/vulkani/<int:id>")
def vulkans(id):
    conn = get_db()

    vulkans = conn.execute("""
        SELECT Vulkani.*,
               Vulkani_kontinenti.continent,
               Vulkani_tips.type,
               Vulkani_aktivitate.eruption_reason
        FROM Vulkani
        LEFT JOIN Vulkani_kontinenti
            ON Vulkani.id_continent = Vulkani_kontinenti.id
        LEFT JOIN Vulkani_tips
            ON Vulkani.id_type = Vulkani_tips.id
        LEFT JOIN Vulkani_aktivitate
            ON Vulkani.id_activity = Vulkani_aktivitate.id
        WHERE Vulkani.id = ?
    """, (id,)).fetchone()

    aktivitate = conn.execute(
        "SELECT * FROM Vulkani_aktivitate"
    ).fetchall()

    conn.close()

    return render_template(
        "vulkans.html",
        vulkans=vulkans,
        aktivitate=aktivitate
    )


@app.route("/edit_activity/<int:id>", methods=["POST"])
def edit_activity(id):
    conn = get_db()

    conn.execute("""
        UPDATE Vulkani
        SET id_activity = ?,
            last_eruption = ?,
            damage = ?
        WHERE id = ?
    """, (
        request.form.get("activity"),
        request.form.get("last_eruption"),
        request.form.get("damage"),
        id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("vulkans", id=id))


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()

    conn.execute(
        "DELETE FROM Vulkani WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("vulkani"))


@app.route("/add", methods=["GET", "POST"])
def add():
    conn = get_db()

    if request.method == "POST":

        image_file = request.files.get("image")
        filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            image_file.save(image_path)

        conn.execute("""
            INSERT INTO Vulkani
            (
                name,
                height,
                diameter,
                images,
                country,
                id_continent,
                id_type,
                id_activity,
                coordinates,
                last_eruption,
                damage
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["height"],
            request.form["diameter"],
            filename,
            request.form["country"],
            request.form["continent"],
            request.form["type"],
            request.form["activity"],
            request.form["coordinates"],
            request.form["last_eruption"],
            request.form["damage"]
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("vulkani"))

    kontinenti = conn.execute(
        "SELECT * FROM Vulkani_kontinenti"
    ).fetchall()

    tipi = conn.execute(
        "SELECT * FROM Vulkani_tips"
    ).fetchall()

    aktivitate = conn.execute(
        "SELECT * FROM Vulkani_aktivitate"
    ).fetchall()

    conn.close()

    return render_template(
        "add.html",
        kontinenti=kontinenti,
        tipi=tipi,
        aktivitate=aktivitate
    )


if __name__ == "__main__":
    app.run(debug=True)