import os
from pathlib import Path
SECRET_KEY = os.urandom(24)
SQLALCHEMY_DATABASE_URI = "postgresql://storage_admin:THw7l0bxvPPkWUhP@db:5432/strg_users_db"
