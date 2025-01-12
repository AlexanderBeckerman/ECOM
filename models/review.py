from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from Project.models.base import Base

class Review(Base):
    __tablename__ = 'reviews'
    review_id = Column(String, primary_key=True, unique=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    business_id = Column(String, ForeignKey('restaurants.business_id'), nullable=False)
    stars = Column(Float, nullable=False)
    date = Column(String)
    text = Column(Text)
    useful = Column(Integer)
    funny = Column(Integer)
    cool = Column(Integer)

    user = relationship('User', back_populates='reviews')
    business = relationship('Restaurant', back_populates='reviews')
