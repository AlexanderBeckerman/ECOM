from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database setup
DB_URI = "sqlite:///yelp.db"  # SQLite database
engine = create_engine(DB_URI, echo=True)  # echo=True logs SQL commands
Session = sessionmaker(bind=engine)

# Base class for models
Base = declarative_base()
def create_tables():
    """Create all tables defined in models."""
    Base.metadata.create_all(engine)
