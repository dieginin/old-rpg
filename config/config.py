from dotenv import dotenv_values

dot = dotenv_values()
DISCORD_TOKEN = dot["DISCORD_TOKEN"]

DB_CLUSTER = dot["DB_CLUSTER"]
DB_PASSWORD = dot["DB_PASSWORD"]
DB_USER = dot["DB_USER"]
