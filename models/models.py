from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from base import Base


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
    scores = Column(JSON, nullable=True)
    hours = Column(JSON)
    summary = Column(String, nullable=True)
    improvement_report = Column(String, nullable=True)
    reviews = relationship("Review", back_populates="business")


class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    review_count = Column(Integer)
    joined = Column(String)
    # friends = Column(JSON)
    fans = Column(Integer)
    average_stars = Column(Float)
    compliments = Column(Integer)

    reviews = relationship('Review', back_populates='user')


class Review(Base):
    __tablename__ = 'reviews'
    review_id = Column(String, primary_key=True, unique=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    business_id = Column(String, ForeignKey('restaurants.business_id'), nullable=False)
    stars = Column(Float, nullable=False)
    date = Column(String)
    text = Column(String)
    useful = Column(Integer)
    funny = Column(Integer)
    cool = Column(Integer)

    user = relationship('User', back_populates='reviews')
    business = relationship('Restaurant', back_populates='reviews')
