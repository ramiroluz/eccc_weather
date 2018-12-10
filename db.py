from sqlalchemy import create_engine
from decouple import config

db_url = config('DB_URL', default='sqlite://')

engine = create_engine(db_url, echo=False)
