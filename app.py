import sqlite3
import urllib.parse
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = "profiles.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            bio TEXT NOT NULL,
            image_url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def make_svg_avatar(name):
    initial = name[:1].upper() if name else "U"
    svg = f'''<svg xmlns="http://w3.org" viewBox="0 0 100 100">
        <rect width="100" height="100" fill="#6366f1"/>
        <text x="50" y="64" font-size="44" font-family="sans-serif" font-weight="bold" fill="white" text-anchor="middle">{initial}</text>
    </svg>'''
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)

@app.route('/')
def index():
    conn = get_db_connection()
    profiles = conn.execute('SELECT * FROM profiles ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', profiles=profiles)

@app.route('/generate-card', methods=['POST'])
def generate_card():
    name = request.form.get('name', '').strip()
    role = request.form.get('role', '').strip() or "Creator"
    bio = request.form.get('bio', '').strip() or "Building cool things on the internet."
    image_url = request.form.get('image_url', '').strip()

    if not image_url:
        image_url = make_svg_avatar(name)

    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO profiles (name, role, bio, image_url) VALUES (?, ?, ?, ?)',
        (name, role, bio, image_url)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    profile = {
        "id": new_id,
        "name": name,
        "role": role,
        "bio": bio,
        "image_url": image_url
    }

    return render_template('card.html', profile=profile)

@app.route('/delete-card/<int:profile_id>', methods=['DELETE'])
def delete_card(profile_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM profiles WHERE id = ?', (profile_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": profile_id})

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    init_db()
    Timer(1, open_browser).start()
    app.run(debug=False)
