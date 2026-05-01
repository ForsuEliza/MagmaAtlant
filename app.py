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
    SELECT Vulkani.*, 
           Vulkani_valstis.country,
           Vulkani_continenti.continent
    FROM Vulkani
    JOIN Vulkani_valstis ON Vulkani.id_country = Vulkani_valstis.id
    JOIN Vulkani_continenti ON Vulkani_valstis.id_continent = Vulkani_continenti.id
    """).fetchall()

    conn.close()
    return render_template("vulkani.html", vulkani=vulkani)


@app.route('/vulkani/<int:id>')
def vulkans(id):
    db = get_db()
    vulkans = db.execute("SELECT * FROM vulkani WHERE id=?", (id,)).fetchone()
    return render_template('vulkans.html', vulkans=vulkans)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()

    if request.method == 'POST':
        db.execute("""
        UPDATE vulkani SET
        name=?, height=?, diameter=?, country=?, continent=?, type=?, last_eruption=?, damage=?, activity=?
        WHERE id=?
        """, (
            request.form['name'],
            request.form['height'],
            request.form['diameter'],
            request.form['country'],
            request.form['continent'],
            request.form['type'],
            request.form['last_eruption'],
            request.form['damage'],
            request.form['activity'],
            id
        ))
        db.commit()
        return redirect(url_for('vulkani'))

    vulkans = db.execute("SELECT * FROM vulkani WHERE id=?", (id,)).fetchone()
    return render_template('edit.html', vulkans=vulkans)


@app.route('/edit_activity/<int:id>', methods=['POST'])
def edit_activity(id):
    db = get_db()
    db.execute("UPDATE vulkani SET activity=? WHERE id=?", 
               (request.form['activity'], id))
    db.commit()
    return redirect(url_for('vulkans', id=id))


if __name__ == '__main__':
    app.run(debug=True)