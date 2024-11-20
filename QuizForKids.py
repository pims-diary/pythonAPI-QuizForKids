import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify
import pymongo
from pymongo.synchronous.database import Database

from typing import Mapping, Any

app = Flask(__name__)

client: pymongo.MongoClient[Mapping[str, Any]]
database: Database[Mapping[str, Any]]

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

try:
    # Creating a MongoClient to connect to the local MongoDB server
    client = pymongo.MongoClient(
        os.getenv("MONGODB_CONNECTION_STRING"),
        tls=True,
        tlsAllowInvalidCertificates=True
    )

    database = client[os.getenv("DATABASE_NAME")]


except Exception as e:
    # Handling exceptions and printing an error message if collection creation fails
    print(f"Error: {e}")


def get_item(collection, identifier: str):
    my_query = {"_id": identifier}
    my_item = collection.find(my_query)

    my_json = []

    for item in my_item:
        # Convert ObjectId to string
        item['_id'] = str(item['_id'])
        my_json.append(item)

    return jsonify(my_json[0]), 200


@app.route("/get-player/<player_id>")
def get_users(player_id):
    players_collection = database["quiz_player_stats"]
    return get_item(players_collection, player_id)


@app.route("/update-level/<player_id>", methods=["PUT"])
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
        # Handling exceptions and printing an error message if data insertion fails
        print(f"Error: {error}")
        return jsonify({"error": "An error occurred while updating the level"}), 500


if __name__ == '__main__':
    app.run(debug=True)
