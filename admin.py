from flask import Flask, render_template, request, jsonify
import sqlite3, os

app = Flask(__name__)
ADMIN_KEY = os.getenv("ADMIN_KEY") or "admin123"

def get_db():
    return sqlite3.connect("dexai.db")

@app.route("/")
def dashboard():
    if request.args.get("key") != ADMIN_KEY: return "Access Denied", 401
    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY taps DESC").fetchall()
    conn.close()
    return render_template("admin.html", users=users)

@app.route("/add_task", methods=["POST"])
def add_task():
    if request.args.get("key") != ADMIN_KEY: return "Denied", 401
    task = request.json["task"]
    # save to tasks table or broadcast via bot
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(debug=True)
