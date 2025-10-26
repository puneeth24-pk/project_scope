import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Environment variables for Render or Railway
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "OxlvxnNzxEsnhhqBMAgurtxZnNSEctru")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "maglev.proxy.rlwy.net")
MYSQL_DB = os.environ.get("MYSQL_DB", "railway")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "27275")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
