from concurrent.futures import ThreadPoolExecutor

from transformers import pipeline
import json
import numpy as np
from collections import defaultdict


def get_reviews_for_business(business_id, review_file, num_reviews):
    reviews = []
    reviews_cnt = 0
    with open(review_file, "r", encoding="utf-8") as f:
        print("started reading reviews...")
        for line in f:
            if reviews_cnt >= num_reviews:
                break
            review = json.loads(line)
            if review["business_id"] == business_id:
                reviews.append(review["text"])
                reviews_cnt += 1

    return reviews


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
def extract_category_ratings(reviews, categories, relibility):
    category_scores = defaultdict(list)
    n = len(reviews)
    personal_category_scores = [{} for i in range(n)]
    for i in range(n):
        review = reviews[i]
        realability_score = relibility[i]
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
                category_scores[category].append(sentiment_score*realability_score)
                personal_category_scores[i][category] = sentiment_score
                print(
                    f"relevence score: {relevance}, sentiment score: {sentiment_score} for category: {category}, review:\n{review}")
                print()

    # Average scores for each category
    return {category: [np.sum(scores),len(scores)] if scores else 0 for category, scores in category_scores.items()}, personal_category_scores


business_id = "k0hlBqXX-Bt0vf1op7Jr1w"
review_cnt = 19
reviews = get_reviews_for_business(business_id, "../../Dataset/yelp_academic_dataset_review.json", review_cnt)

# Load NLP models
relevance_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Define categories to analyze - changes according to user preferences
categories = ["food", "service", "atmosphere", "music", "price"]

# Extract category ratings from reviews
category_ratings ,personal_category_scores = extract_category_ratings(reviews, categories)
print(category_ratings)
