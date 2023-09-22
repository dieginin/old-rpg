from dotenv import dotenv_values

dot = dotenv_values()
DISCORD_TOKEN = dot["DISCORD_TOKEN"]
DB_PASSWORD = dot["DB_PASSWORD"]
