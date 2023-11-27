import pymongo
from datetime import datetime

def connect_to_mongodb(collection_name):
    try:
        # MongoDB connection details
        mongo_host = "localhost"
        mongo_port = 27017
        database_name = "Airbnb"

        # Connect to the MongoDB server
        client = pymongo.MongoClient(mongo_host, mongo_port)

        # Access the database
        database = client[database_name]

        # Access the specified collection
        collection = database[collection_name]

        return client, collection

    except pymongo.errors.ConnectionFailure as e:
        print(f"Error: Unable to connect to MongoDB. {e}")
        return None, None

def insert_document(collection, document):
    try:
        # Insert the new document into the collection
        result = collection.insert_one(document)

        # Print the inserted document's ID
        print("Inserted document ID:", result.inserted_id)

    except Exception as e:
        print(f"Error: Unable to insert document into MongoDB. {e}")

def close_connection(client):
    try:
        # Close the MongoDB connection
        client.close()
        print("Connection closed successfully.")

    except Exception as e:
        print(f"Error: Unable to close MongoDB connection. {e}")