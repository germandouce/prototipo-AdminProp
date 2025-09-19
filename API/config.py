import os

# Solo cargar .env si no estamos en Docker (ISDOCKER no está seteado o es False)
if os.environ.get("ISDOCKER", "False") != "True":
    #estamos en render
    from dotenv import load_dotenv
    load_dotenv()

#si no estamos en dcoker la funcion de arriba piso los environ con los valores del .env
#si estamos en docker los environ van a valer lo q deicia el env-docker
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
API_PORT = os.environ.get("API_PORT")
DEBUG = os.environ.get("DEBUG", "False")
ISDOCKER = os.environ.get("ISDOCKER", "True")
USE_SSL = os.environ.get("USE_SSL", "False")