import sqlite3

from base import create_tables, engine, Session
# from models.models import Restaurant, User, Review
from loaders.load_users import load_users
from loaders.load_reviews import load_reviews, load_reviews_by_business
from loaders.load_restaurants import load_restaurants
from models.models import User, Restaurant, Review
from sqlalchemy import inspect
from transformers import pipeline
from backend.scoreExtractor import extract_category_ratings
from backend.helpers.sentence_splitter import split_into_sentences
from flask import Flask, jsonify
from backend.routes.routes import user_bp

app = Flask(__name__)
app.register_blueprint(user_bp)

USERS_FILEPATH = './Dataset/yelp_academic_dataset_user.json'
RESTAURANTS_FILEPATH = './Dataset/yelp_academic_dataset_business.json'
REVIEWS_FILEPATH = './Dataset/yelp_academic_dataset_review.json'


def main():
    create_tables()  # Create tables if they don't exist
    # with Session() as session:
        # load_users(session, USERS_FILEPATH)
        # load_restaurants(session, RESTAURANTS_FILEPATH)
        # business_id = session.query(Restaurant.business_id).all()
        # for id in business_id:
        #     business_id = id[0]
        #     review_cnt = session.query(Restaurant.review_count).filter(Restaurant.business_id == business_id).first()[0]
        #     try:
        #         load_reviews_by_business(session, REVIEWS_FILEPATH, business_id, review_cnt)
        #     except sqlite3.InternalError as e:
        #         continue


    # Load NLP models
    # relevance_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    # sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    #
    # with Session() as session:
    #     reviews = session.query(Review.text).filter(Review.business_id == business_id).all()
    # reviews = [review[0] for review in reviews]
    # categories = ["food", "service", "music", "price"]
    # result, personal_category_scores = extract_category_ratings(reviews, categories, relevance_classifier,
    #                                                             sentiment_analyzer)


if __name__ == '__main__':
    main()
    app.run(debug=True)
