from transformers import pipeline
from sqlalchemy.orm import Session
from models import Review
from reliability_calculator import calculate_reliability

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def generate_negative_review_report(restaurant_id, db_session: Session, reliability_threshold=0.6, min_words=5):
    """
    Generate a report for a restaurant based on low-rated reviews from reliable users.
    """
    negative_reviews = db_session.query(Review).filter(
        (Review.business_id == restaurant_id)

    if not negative_reviews:
        return "No negative reviews available for this restaurant."

    reliable_negative_reviews = []

    for review in negative_reviews:
        user_id = review.user_id
        user_reliability = calculate_reliability(user_id, db_session)

        if user_reliability is not None and user_reliability >= reliability_threshold:
            review_text = review.text
            if len(review_text.split()) >= min_words:
                reliable_negative_reviews.append(review_text)

    if not reliable_negative_reviews:
        return "No reliable negative reviews found for this restaurant."

    combined_reviews = " ".join(reliable_negative_reviews)
    summary = summarizer(combined_reviews, max_length=150, min_length=50, do_sample=False)

    return summary[0]['summary_text']
