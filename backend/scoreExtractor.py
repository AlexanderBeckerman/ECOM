from concurrent.futures import ThreadPoolExecutor

import json
import numpy as np
from collections import defaultdict
from base import Session
from models.models import Review, Restaurant
from sqlalchemy import func
from backend.helpers.sentence_splitter import split_into_sentences

# from reliability_calculator import calculate_review_reliability

business_to_scores = {}
business_to_weights = {}
categories = ["food", "service", "music", "price", "cleanliness"]


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
    weight = {category: sum(category_relevance_scores[category]) for category in categories}
    for category, scores in category_scores.items():
        if scores:
            result[category] = np.dot(scores, category_relevance_scores[category]) / sum(
                category_relevance_scores[category])
        else:
            result[category] = 0

    return result, personal_category_scores, weight


def get_scores_for_all_businesses(relevance_classifier, sentiment_analyzer):
    with Session() as session:
        business_ids = session.query(Review.business_id).distinct().all()
        business_ids = [id[0] for id in business_ids]
        executor = ThreadPoolExecutor(max_workers=4)
        results = executor.map(get_reviews_for_business, business_ids)
        for business_id, reviews in zip(business_ids, results):
            result, personal_category_scores, weight = extract_category_ratings(reviews, relevance_classifier,
                                                                                sentiment_analyzer)
            business_to_scores[business_id] = result
            business_to_weights[business_id] = weight
            print(f"Business ID: {business_id}, Category Scores: {result}")
            print()
            # calculate_review_reliability(personal_category_scores, business_id)

    save_scores_to_db()


def save_scores_to_db():
    with Session() as session:
        for business_id, scores in business_to_scores.items():
            weights = business_to_weights[business_id]
            restaurant = session.query(Restaurant).filter(Restaurant.business_id == business_id).first()
            past_scores = restaurant.scores
            past_weights = restaurant.score_weights
            if past_scores:
                future_score = {}
                future_weight = {}
                for category, score in scores.items():
                    if category in past_scores:
                        future_weight[category] = past_weights[category] + weights[category]
                        future_score[category] = (past_scores[category] * past_weights[category] + score * weights[
                            category]) / future_weight[category]
                    else:
                        future_score[category] = score
                        future_weight[category] = weights[category]
                restaurant.scores = future_score
                restaurant.score_weights = future_weight
            else:
                restaurant.scores = scores
                restaurant.score_weights = weights
        session.commit()
        print("Scores saved to database")
