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

# db
DB_USERNAME = env["DB_USERNAME"]
DB_PASSWORD = env["DB_PASSWORD"]
DB_NAME = env["DB_NAME"]
DB_HOST = env["DB_HOST"]
DB_PORT = env["DB_PORT"]

# flask
API_PORT = env["API_PORT"]
DEBUG = env.get("DEBUG", "False")
ISDOCKER = env.get("ISDOCKER", "False")
API_BASE_URL = env["API_BASE_URL"]
FRONTEND_URL = env["FRONTEND_URL"]
SENDGRID_API_KEY = env["SENDGRID_API_KEY"]
FROM_EMAIL = env["FROM_EMAIL"]
