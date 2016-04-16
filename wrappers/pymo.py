import pymongo
from threading import Lock

pymongoLock = Lock()

def find(collection, filter):
	with pymongoLock:
		return collection.find(filter)
		
def find_one(collection, filter):
	with pymongoLock:
		return collection.find_one(filter)

def delete_one(collection, filter):
	with pymongoLock:
		return collection.delete_one(filter)

def update_one(collection, filter, update, upsert=False):
	with pymongoLock:
		return collection.update_one(filter, update, upsert)