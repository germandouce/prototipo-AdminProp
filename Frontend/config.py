import os
from dotenv import dotenv_values

# Por defecto, cargamos desde el archivo .env (para producción)
env = dotenv_values()

# Verificamos si estamos en Docker. os.environ.get() es más seguro.
# El .lower() in ('true', '1') hace la comprobación más flexible.
is_docker_env = os.environ.get('ISDOCKER', 'false').lower() in ('true', '1')

# Si estamos en Docker, las variables de os.environ (inyectadas por env_file)
# tienen prioridad.
if is_docker_env:
    env = os.environ

# api
API_PORT = env["API_PORT"]
API_HOST = env["API_HOST"]

# flask
FRONT_PORT = env["FRONT_PORT"]
DEBUG = env.get("DEBUG", "False")

# SOURCES_PATH = "./static/images/rooms"
