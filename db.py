import os

from motor.motor_asyncio import AsyncIOMotorClient


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


client = AsyncIOMotorClient(DB_HOST, DB_PORT)
db = client.fit_bot
coll_exc = db.excercises
coll_train = db.training
