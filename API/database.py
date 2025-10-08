from sqlalchemy import create_engine
from config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DEBUG

# Creamos el engine aquí para que pueda ser importado desde cualquier parte
engine = create_engine(f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# También podemos exportar la variable DEBUG desde aquí si la necesitamos en varios sitios
IS_DEBUG = DEBUG == "True"