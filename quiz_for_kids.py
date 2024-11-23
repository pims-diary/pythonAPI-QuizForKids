import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
import pymongo
from pymongo.synchronous.database import Database

from typing import Mapping, Any

# Import blueprints
from pymongo_api import mongo_api, init_mongo
from sqlite_api import sqlite_api

app = Flask(__name__)

client: pymongo.MongoClient[Mapping[str, Any]]
database: Database[Mapping[str, Any]]

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

try:
    # Initialize MongoDB client and database
    client = pymongo.MongoClient(
        os.getenv("MONGODB_CONNECTION_STRING"),
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    database_name = os.getenv("DATABASE_NAME")

    # Initialize MongoDB in pymongo_api
    init_mongo(client, database_name)

except Exception as e:
    print(f"Error: {e}")

# Register blueprints
app.register_blueprint(mongo_api, url_prefix='/mongo')  # MongoDB APIs under /mongo
app.register_blueprint(sqlite_api, url_prefix='/sqlite')  # SQLite APIs under /sqlite

if __name__ == '__main__':
    app.run(debug=True)
