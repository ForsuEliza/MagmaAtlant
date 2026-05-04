from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path



app = Flask(__name__)

def get_db():
    db = Path(__file__).parent / "VulkanuSaraksts"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/vulkani")
def vulkani():
    conn = get_db()

    vulkani = conn.execute("""
    SELECT vulkani.*,
           Vulkani_kontinenti.continent,
           Vulkani_tips.type,
           Vulkani_aktivitate.eruption_reason
    FROM vulkani
    LEFT JOIN Vulkani_kontinenti ON vulkani.id_continent = Vulkani_kontinenti.id
    LEFT JOIN Vulkani_tips ON vulkani.id_type = Vulkani_tips.id
    LEFT JOIN Vulkani_aktivitate ON vulkani.id_activity = Vulkani_aktivitate.id
    """).fetchall()

    conn.close()
    return render_template("vulkani.html", vulkani=vulkani)


@app.route('/vulkani/<int:id>')
def vulkans(id):
    conn = get_db()

    vulkans = conn.execute("""
    SELECT vulkani.*,
           Vulkani_kontinenti.continent,
           Vulkani_tips.type,
           Vulkani_aktivitate.eruption_reason
    FROM vulkani
    LEFT JOIN Vulkani_kontinenti ON vulkani.id_continent = Vulkani_kontinenti.id
    LEFT JOIN Vulkani_tips ON vulkani.id_type = Vulkani_tips.id
    LEFT JOIN Vulkani_aktivitate ON vulkani.id_activity = Vulkani_aktivitate.id
    WHERE vulkani.id = ?
    """, (id,)).fetchone()

    aktivitate = conn.execute("SELECT * FROM Vulkani_aktivitate").fetchall()

    conn.close()

    return render_template("vulkans.html", vulkans=vulkans, aktivitate=aktivitate)



@app.route("/edit_activity/<int:id>", methods=["POST"])
def edit_activity(id):
    conn = get_db()

    conn.execute("""
    UPDATE vulkani 
    SET id_activity=?, last_eruption=?, damage=?
    WHERE id=?
    """, (
        request.form["activity"],
        request.form["last_eruption"],
        request.form["damage"],
        id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("vulkans", id=id))



@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM vulkani WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("vulkani"))



@app.route("/add", methods=["GET", "POST"])
def admin():
    conn = get_db()

    if request.method == "POST":

        conn.execute("""
        INSERT INTO Vulkani
        (name, height, diameter, images, country, id_continent, id_type, id_activity, coordinates, last_eruption, damage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["height"],
            request.form["diameter"],
            None,
            request.form["country"],
            request.form["continent"],
            request.form["type"],
            request.form["activity"],
            request.form["coordinates"],
            request.form["last_eruption"],
            request.form["damage"]
        ))

        conn.commit()

    kontinenti = conn.execute("SELECT * FROM Vulkani_kontinenti").fetchall()
    tipi = conn.execute("SELECT * FROM Vulkani_tips").fetchall()
    aktivitate = conn.execute("SELECT * FROM Vulkani_aktivitate").fetchall()

    conn.close()

    return render_template("admin.html",
        kontinenti=kontinenti,
        tipi=tipi,
        aktivitate=aktivitate
    )