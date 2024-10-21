import os
from pathlib import Path
SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = "postgresql://storage_admin:THw7l0bxvPPkWUhP@db:5432/strg_users_db"
