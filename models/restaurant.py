from sqlalchemy import Column, String, Float, Integer, JSON, ARRAY
from Project.models.base import Base


class Restaurant(Base):
    __tablename__ = 'restaurants'
    business_id = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    stars = Column(Float)
    review_count = Column(Integer)
    attributes = Column(JSON)
    categories = Column(JSON)
    hours = Column(JSON)
    reviews = Column(ARRAY(String))
