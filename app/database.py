from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_HOST = os.getenv('DATABASE_HOST', 'db')
DATABASE_USER = os.getenv('DATABASE_USER', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '1234')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'api')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')

url_database = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

#url_database = 'postgresql://postgres:1234@db:5432/api'
engine = create_engine(url_database)
SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
