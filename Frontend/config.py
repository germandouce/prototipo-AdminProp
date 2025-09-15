from dotenv import dotenv_values

env = dotenv_values()

# api
API_PORT = env["API_PORT"]
API_HOST = env["API_HOST"]

# flask
FRONT_PORT = env["FRONT_PORT"]
DEBUG = env["DEBUG"]

# SOURCES_PATH = "./static/images/rooms"