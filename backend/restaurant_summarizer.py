from transformers import pipeline
from sqlalchemy.orm import Session
from models import Review
from reliability_calculator import calculate_reliability

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def summarize_reviews_for_restaurant(restaurant_id, db_session: Session, top_n=3, min_words=5):
    """
    Retrieve the top N users based on reliability for a specific restaurant's reviews and generate a summarized review.
    This function now ensures reviews have a minimum number of words to be considered.
    """
    # Step 1: Retrieve all reviews for the restaurant
    reviews = db_session.query(Review).filter(Review.business_id == restaurant_id).all()

    if not reviews:
        return "No reviews available for this restaurant."  # If no reviews found

    user_reliabilities = []

    # Step 2: Calculate reliability for each user based on their reviews
    for review in reviews:
        user_id = review.user_id
        user_reliability = calculate_reliability(user_id, db_session)

        if user_reliability is not None:
            review_text = review.text
            # Check if the review has more than the minimum number of words
            if len(review_text.split()) >= min_words:
                user_reliabilities.append((user_id, user_reliability, review_text))

    # If no valid reviews found
    if not user_reliabilities:
        return "No valid reviews with enough detail found for this restaurant."

    # Step 3: Sort users by reliability and select the top N
    top_users = sorted(user_reliabilities, key=lambda x: x[1], reverse=True)[:top_n]

    # Step 4: Combine the reviews from top users
    combined_reviews = " ".join([user_review[2] for user_review in top_users])

    # Step 5: Summarize the combined reviews using the summarization model
    summary = summarizer(combined_reviews, max_length=150, min_length=50, do_sample=False)

    return summary[0]['summary_text']