from sqlalchemy import Column, String, Float, Integer, JSON
from sqlalchemy.orm import relationship
from Project.models.base import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    review_count = Column(Integer)
    joined = Column(String)
    friends = Column(JSON)
    fans = Column(Integer)
    average_stars = Column(Float)
    compliments = Column(Integer)

    reviews = relationship('Review', back_populates='user')
