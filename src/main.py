import os
import ssl

os.environ.setdefault("USER", "wasmer")

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)


def connect_db():
    tls = ssl.create_default_context()
    tls.check_hostname = False
    tls.verify_mode = ssl.CERT_NONE

    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        ssl=tls,
        connect_timeout=10,
        read_timeout=10,
        write_timeout=10,
    )


@app.route("/")
def index():
    return "Challenge 07: applicazione aggiornata!"


@app.get("/api/notes")
def list_notes():
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, content, created_at FROM notes ORDER BY id"
            )
            notes = cursor.fetchall()

        for note in notes:
            note["created_at"] = note["created_at"].isoformat()

        return jsonify(notes)
    finally:
        connection.close()

@app.post("/api/notes")
def create_note():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invia un oggetto JSON"}), 400

    content = data.get("content")

    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "Il testo non può essere vuoto"}), 400

    content = content.strip()
    connection = connect_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO notes (content) VALUES (%s)",
                (content,),
            )
            note_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "id": note_id,
            "content": content,
        }), 201
    finally:
        connection.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
