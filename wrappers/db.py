import json
import pymongo

# Load the profile configuration file
config = None
with open("profile.config") as f:
    config = json.load(f)

def get_instance():
    # Connect to the database
    connection=pymongo.MongoClient(config["database"]["host"], int(config["database"]["port"]))
    db = connection[config["database"]["db_name"]]
    db.authenticate(config["database"]["username"], config["database"]["password"])
    return db