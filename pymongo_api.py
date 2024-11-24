from flask import Blueprint, request, jsonify
import pymongo
from pymongo.synchronous.database import Database
from typing import Mapping, Any

# Define the blueprint for MongoDB APIs
mongo_api = Blueprint('mongo_api', __name__)

# MongoDB client and database (placeholders for now)
client: pymongo.MongoClient[Mapping[str, Any]]
database: Database[Mapping[str, Any]]


# Function to initialize MongoDB (to be called from QuizForKids.py)
def init_mongo(mongo_client: pymongo.MongoClient[Mapping[str, Any]], db_name: str):
    global client, database
    client = mongo_client
    database = client[db_name]


# Helper function: Fetch item by identifier
def get_item(collection, identifier: str):
    my_query = {"_id": identifier}
    my_item = collection.find(my_query)

    my_json = []

    for item in my_item:
        # Convert ObjectId to string
        item['_id'] = str(item['_id'])
        my_json.append(item)

    return jsonify(my_json[0]), 200


# Route: Get player by ID
@mongo_api.route("/get-player/<player_id>")
def get_users(player_id):
    players_collection = database["quiz_player_stats"]
    return get_item(players_collection, player_id)


# Route: Update player level
@mongo_api.route("/update-level/<player_id>", methods=["PUT"])
def update_level(player_id):
    try:
        players_collection = database["quiz_player_stats"]
        id_query = {"_id": player_id}

        request_body = request.get_json()
        new_level = request_body.get("level")

        if not new_level:
            return jsonify({"error": "Invalid input: 'level' is required"}), 400

        # Update the player's level
        update_result = players_collection.update_one(
            id_query,
            {"$set": {"level": new_level}}
        )

        if update_result.modified_count == 0:
            return jsonify({"error": "Invalid input: 'level' is same as before"}), 400

        return jsonify({"message": f"Player {player_id} level updated to {new_level}"}), 200

    except Exception as error:
        print(f"Error: {error}")
        return jsonify({"error": "An error occurred while updating the level"}), 500


# Function to create a record in MongoDB
def create_player_record(player_id: str, email: str, name: str):
    try:
        players_collection = database["quiz_player_stats"]
        new_player = {
            "_id": player_id,
            "email": name,
            "username": email,
            "level": "1"  # Default level for a new player
        }
        players_collection.insert_one(new_player)
        return {"message": "Player record created in MongoDB", "player": new_player}, 201
    except Exception as error:
        print(f"Error creating player record in MongoDB: {error}")
        return {"error": "Failed to create player record in MongoDB"}, 500
