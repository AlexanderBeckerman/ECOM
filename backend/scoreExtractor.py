from concurrent.futures import ThreadPoolExecutor

import json
import numpy as np
from collections import defaultdict
from base import Session
from models.models import Review
# from reliability_calculator import calculate_review_reliability

def get_reviews_for_business(business_id):
    with Session() as session:
        reviews = (
            session.query(Review.text)
            .filter(Review.business_id == business_id)
            .all()
        )
        return [r[0] for r in reviews]  # Return list of review texts


# Function to process a chunk of the review file
def process_chunk(chunk, business_id):
    relevant_reviews = []
    for line in chunk:
        review = json.loads(line)
        if review["business_id"] == business_id:
            review_sentences = review["text"].split(".")
            for sentence in review_sentences:
                relevant_reviews.append(sentence)
    return relevant_reviews


# Function to split the file into chunks
def read_file_in_chunks(file_path, chunk_size=1000):
    with open(file_path, "r", encoding="utf-8") as file:
        chunk = []
        for line in file:
            chunk.append(line)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:  # Yield the last chunk
            yield chunk


# Function to read reviews for a business using multithreading
def get_reviews_with_multithreading(business_id, review_file, chunk_size=1000, max_threads=32):
    reviews = []
    with ThreadPoolExecutor(max_threads) as executor:
        futures = [
            executor.submit(process_chunk, chunk, business_id)
            for chunk in read_file_in_chunks(review_file, chunk_size)
        ]
        for future in futures:
            reviews.extend(future.result())
    return reviews


# Function to extract category ratings from reviews
def extract_category_ratings(reviews, categories, relevance_classifier, sentiment_analyzer):
    category_scores = defaultdict(list)
    n = len(reviews)
    personal_category_scores = [{} for i in range(n)]
    category_relevance_scores = defaultdict(list)
    for i in range(n):
        review = reviews[i]
        #need to work on it
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
                    f"relevence score: {relevance}, sentiment score: {sentiment_score} for category: {category}, review:\n{review}")
                print()
    result = {}
    for category, scores in category_scores.items():
        if scores:
            result[category] = np.dot(scores, category_relevance_scores[category]) / sum(
                category_relevance_scores[category])
        else:
            result[category] = 0

    return result, personal_category_scores

    # Average scores for each category
    # return {category: [np.sum(scores), len(scores)] if scores else 0 for category, scores in
    #         category_scores.items()}, personal_category_scores


