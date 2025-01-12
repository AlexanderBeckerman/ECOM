from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Configure your database URI
DATABASE_URI = 'sqlite:///yelp.db'

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)


def create_tables():
    Base.metadata.create_all(engine)
