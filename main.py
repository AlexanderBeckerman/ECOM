import sqlite3

from base import create_tables, engine, Session
# from models.models import Restaurant, User, Review
from loaders.load_users import load_users
from loaders.load_reviews import load_reviews, load_reviews_by_business
from loaders.load_restaurants import load_restaurants
from models.models import User, Restaurant, Review
from sqlalchemy import inspect
from transformers import pipeline
from backend.scoreExtractor import get_scores_for_all_businesses
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

    # Uncomment if you want to load data from scratch
    with Session() as session:
    #load_users(session, USERS_FILEPATH)
        #load_restaurants(session, RESTAURANTS_FILEPATH, limit=15)
        #business_id = session.query(Restaurant.business_id).all()
        #for id in business_id:
            #business_id = id[0]
            #review_cnt = session.query(Restaurant.review_count).filter(Restaurant.business_id == business_id).first()[0]
            #try:
                #load_reviews_by_business(session, REVIEWS_FILEPATH, business_id, review_cnt)
            #except sqlite3.InternalError as e:
                #continue
        summary = summarize_reviews_for_restaurant("ABxoFuzZy5mqQ8C5FJJajQ",session)
        print(summary)
        report = generate_improvement_report("ABxoFuzZy5mqQ8C5FJJajQ",session)
        print(report)
    # Load NLP models
    relevance_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    # Uncomment if you want to calculate scores for all businesses in advance
    #get_scores_for_all_businesses(relevance_classifier,
                                  #sentiment_analyzer)  # Calculate scores for all businesses in advance


    #match_restaurants_to_user([2.4, 3.3, 4.2, 4.6], ["food", "service", "music", "price"], ("Harvey", "LA"))

if __name__ == '__main__':
    main()
    app.run(debug=True, use_reloader=False)
