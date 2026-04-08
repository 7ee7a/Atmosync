import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL matches the docker-compose settings
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://aeros:aeros_password@localhost:5432/aeros_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
