from dotenv import dotenv_values

env = dotenv_values()

# db
DB_USERNAME = env["DB_USERNAME"]
DB_PASSWORD = env["DB_PASSWORD"]
DB_NAME = env["DB_NAME"]
DB_HOST = env["DB_HOST"]
DB_PORT = env["DB_PORT"]

# flask
API_PORT = env["API_PORT"]
DEBUG = env["DEBUG"]
ISDOCKER = env["ISDOCKER"]
API_BASE_URL = env["API_BASE_URL"]