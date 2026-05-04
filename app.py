from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)

def get_db():
    db = Path(__file__).parent / "Datubaze"
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
           Vulkani_valstis.country,
           Vulkani_continenti.continent
    FROM vulkani
    JOIN Vulkani_valstis ON vulkani.id_country = Vulkani_valstis.id
    JOIN Vulkani_continenti ON Vulkani_valstis.id_continent = Vulkani_continenti.id
    """).fetchall()

    conn.close()
    return render_template("vulkani.html", vulkani=vulkani)


@app.route('/vulkani/<int:id>')
def vulkans(id):
    conn = get_db()

    vulkans = conn.execute("""
    SELECT vulkani.*, 
           Vulkani_valstis.country,
           Vulkani_continenti.continent,
           Vulkanu_tips.type,
           Vulkani_aktivitate.eruption_reason
    FROM vulkani
    JOIN Vulkani_valstis ON vulkani.id_country = Vulkani_valstis.id
    JOIN Vulkani_continenti ON Vulkani_valstis.id_continent = Vulkani_continenti.id
    JOIN Vulkanu_tips ON vulkani.id_type = Vulkanu_tips.id
    JOIN Vulkani_aktivitate ON vulkani.id_activity = Vulkani_aktivitate.id
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
def add():
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        INSERT INTO vulkani 
        (name, height, diameter, coordinates, images, id_country, id_type, id_activity, last_eruption, damage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["height"],
            request.form["diameter"],
            request.form["coordinates"],
            request.form["images"],
            request.form["country"],
            request.form["type"],
            request.form["activity"],
            request.form["last_eruption"],
            request.form["damage"]
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("vulkani"))

    valstis = conn.execute("SELECT * FROM Vulkani_valstis").fetchall()
    tipi = conn.execute("SELECT * FROM Vulkanu_tips").fetchall()
    aktivitate = conn.execute("SELECT * FROM Vulkani_aktivitate").fetchall()

    conn.close()

    return render_template("add.html",
        valstis=valstis,
        tipi=tipi,
        aktivitate=aktivitate
    )


if __name__ == '__main__':
    app.run(debug=True)