import os
import ssl

import pymysql
from flask import Flask, jsonify

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
