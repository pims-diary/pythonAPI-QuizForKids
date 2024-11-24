from flask import Blueprint, request, jsonify
import sqlite3
from pymongo_api import create_player_record

sqlite_api = Blueprint('sqlite_api', __name__, url_prefix='/sqlite')


# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect('players.db')  # Use your database file
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


# 1. Login Endpoint
@sqlite_api.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('Email')
    password = data.get('Password')
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM Players WHERE Email = ? AND Password = ?',
        (email, password)
    ).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user)), 200
    return jsonify({"error": "Invalid credentials"}), 401


# 2. Registration Endpoint
@sqlite_api.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('Email')
    password = data.get('Password')
    name = data.get('Name')

    conn = get_db_connection()
    # Check if user exists
    existing_user = conn.execute(
        'SELECT * FROM Players WHERE Email = ?',
        (email,)
    ).fetchone()
    if existing_user:
        conn.close()
        return jsonify({"error": "User already exists"}), 400

    # Get last PlayerId
    last_id = conn.execute(
        'SELECT PlayerId FROM Players ORDER BY PlayerId DESC LIMIT 1'
    ).fetchone()
    next_id = str(int(last_id['PlayerId']) + 1) if last_id else "10001"

    # Insert new user
    conn.execute(
        'INSERT INTO Players (PlayerId, Email, Password, Name) VALUES (?, ?, ?, ?)',
        (next_id, email, password, name)
    )
    conn.commit()
    conn.close()

    # Create record in MongoDB
    mongo_response = create_player_record(next_id, name, email)
    if mongo_response[1] != 201:  # If MongoDB insertion fails
        delete_player(next_id)
        return jsonify({"error": "MongoDB sync failed"}), 500

    return jsonify({"PlayerId": next_id, "message": "User registered successfully"}), 201


def delete_player(player_id):
    conn = get_db_connection()
    # Check if user exists
    existing_user = conn.execute(
        'SELECT * FROM Players WHERE PlayerId = ?',
        (player_id)
    ).fetchone()
    if existing_user:
        conn.execute(
            'DELETE FROM Players WHERE PlayerId = ?;',
            (player_id)
        )

    conn.commit()
    conn.close()


