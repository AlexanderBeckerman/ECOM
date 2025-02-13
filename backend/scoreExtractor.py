from concurrent.futures import ThreadPoolExecutor

import json
import numpy as np
from collections import defaultdict
from base import Session
from models.models import Review, Restaurant
from sqlalchemy import func
from backend.helpers.sentence_splitter import split_into_sentences
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# from reliability_calculator import calculate_review_reliability

business_to_scores = {}
categories = ["food", "price", "service", "ambience"]


def filter_reviews(reviews):
    filtered_reviews = []
    for review in reviews:
        sentences = split_into_sentences(review)
        if len(sentences) < 2:
            continue
        sentences = [s for s in sentences if len(s) > 10]
        filtered_reviews.append(" ".join(sentences))
    return filtered_reviews


def get_reviews_for_business(business_id):
    with Session() as session:
        reviews = (
            session.query(Review.text)
            .filter(Review.business_id == business_id,
                    func.length(Review.text) < 500)  # Model can handle max 512 characters
            .all()
        )
        review_texts = [r[0] for r in reviews]
        filtered_reviews = filter_reviews(review_texts)
        return filtered_reviews  # Return list of review texts


# Function to extract category ratings from reviews
def extract_category_ratings(reviews, relevance_classifier, sentiment_analyzer):
    category_scores = defaultdict(list)
    n = len(reviews)
    personal_category_scores = [{} for i in range(n)]
    category_relevance_scores = defaultdict(list)
    for i in range(n):
        review = reviews[i]
        # need to work on it
        reliability_score = 1
        # Relevance scores
        relevance_results = relevance_classifier(review, candidate_labels=categories)
        relevance_scores = {label: score for label, score in
                            zip(relevance_results["labels"], relevance_results["scores"])}
        # Sentiment analysis for relevant categories
        for category, relevance in relevance_scores.items():
            if relevance > 0.25:  # Consider relevant categories
                context = f"{category}: {review}"
                sentiment_result = sentiment_analyzer(context)[0]
                print("sentiment result", sentiment_result)
                sentiment_score = (
                    3 + 2 * sentiment_result["score"]
                    if sentiment_result["label"] == "POSITIVE"
                    else 3 - 2 * sentiment_result["score"]
                )

                category_scores[category].append(sentiment_score * reliability_score)
                personal_category_scores[i][category] = sentiment_score
                category_relevance_scores[category].append(relevance)
                print(
                    f"relevance score: {relevance}, sentiment score: {sentiment_score} for category: {category}, review:\n{review}")
                print()
    result = {}
    for category, scores in category_scores.items():
        if scores:
            result[category] = np.around(np.dot(scores, category_relevance_scores[category]) / sum(
                category_relevance_scores[category]), decimals=2)
        else:
            result[category] = 0

    return result, personal_category_scores


def extract_category_ratings_using_absa(reviews, absa_pipeline):
    sentiment_map = {"Positive": 5, "Neutral": 3, "Negative": 1}
    category_scores = {cat: [] for cat in categories}
    category_confidences = {cat: [] for cat in categories}
    personal_category_scores = [{} for i in range(len(reviews))]
    cnt = 0
    for review in reviews:
        for category in categories:
            result = absa_pipeline(review, text_pair=category)
            predicted_sentiment = result[0]
            print(f"Predicted Sentiment : {predicted_sentiment}")
            sentiment_label = predicted_sentiment['label']
            confidence = predicted_sentiment['score']
            sentiment = sentiment_map[sentiment_label]
            print(f"sentiment: {sentiment_label}, confidence: {confidence}, category: {category}, review:\n {review}")
            if confidence > 0.75:
                if sentiment_label == "Positive":
                    curr_score = 3 + 2 * confidence
                elif sentiment_label == "Negative":
                    curr_score = 3 - 2 * confidence
                else:
                    curr_score = 0
                category_scores[category].append(curr_score)
                category_confidences[category].append(confidence)
                personal_category_scores[cnt][category] = sentiment

        cnt += 1
    final_scores = {
        cat: round(sum(scores) / len(scores), 2) if scores else 0
        for cat, scores in category_scores.items()
    }
    return final_scores, personal_category_scores


def get_scores_for_all_businesses(relevance_classifier=None, sentiment_analyzer=None, absa_pipeline=None):
    with Session() as session:
        business_ids = session.query(Review.business_id).distinct().all()
        business_ids = [id[0] for id in business_ids]
        executor = ThreadPoolExecutor(max_workers=4)
        results = executor.map(get_reviews_for_business, business_ids)
        for business_id, reviews in zip(business_ids, results):
            if relevance_classifier and sentiment_analyzer:
                result, personal_category_scores = extract_category_ratings(reviews, relevance_classifier,
                                                                            sentiment_analyzer)
            elif absa_pipeline:
                result, personal_category_scores = extract_category_ratings_using_absa(reviews, absa_pipeline)
            business_to_scores[business_id] = result
            print(f"Business ID: {business_id}, Category Scores: {result}")
            print()
            # calculate_review_reliability(personal_category_scores, business_id)

    save_scores_to_db()


def save_scores_to_db():
    with Session() as session:
        for business_id, scores in business_to_scores.items():
            restaurant = session.query(Restaurant).filter(Restaurant.business_id == business_id).first()
            restaurant.scores = scores
        session.commit()
        print("Scores saved to database")
