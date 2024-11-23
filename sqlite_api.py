from flask import Blueprint, request, jsonify
import sqlite3

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
    return jsonify({"PlayerId": next_id, "message": "User registered successfully"}), 201


# 3. Check User Exists Endpoint
@sqlite_api.route('/check_user', methods=['POST'])
def check_user():
    data = request.json
    email = data.get('Email')
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM Players WHERE Email = ?',
        (email,)
    ).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user)), 200
    return jsonify({"error": "User does not exist"}), 404


# 4. Get Last PlayerId Endpoint
@sqlite_api.route('/last_player_id', methods=['GET'])
def last_player_id():
    conn = get_db_connection()
    last_id = conn.execute(
        'SELECT PlayerId FROM Players ORDER BY PlayerId DESC LIMIT 1'
    ).fetchone()
    conn.close()
    if last_id:
        return jsonify({"LastPlayerId": last_id['PlayerId']}), 200
    return jsonify({"LastPlayerId": "10000"}), 200  # Default if no players exist
