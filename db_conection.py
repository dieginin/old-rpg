import pymongo

from config import DB_PASSWORD

client = pymongo.MongoClient(
    f"mongodb+srv://dieginin:{DB_PASSWORD}@cluster0.5d4ybta.mongodb.net/"
)
db = client["db"]
characters = db["characters"]

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
