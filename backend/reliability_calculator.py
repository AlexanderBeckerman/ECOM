from sqlalchemy.orm import Session
from models import User, Review  # Importing models for accessing the database

def get_user_data(user_id, db_session: Session):
    """
    Retrieve user data from the database based on user_id.
    """
    return db_session.query(User).filter(User.user_id == user_id).first()

def get_review_data(review_id, db_session: Session):
    """
    Retrieve review data from the database based on review_id.
    """
    return db_session.query(Review).filter(Review.review_id == review_id).first()

def calculate_reliability(user_id, db_session: Session):
    """
    Calculate the reliability of a user based on attributes from the database.
    """
    user = get_user_data(user_id, db_session)
    if not user:
        return None  # Return None if the user is not found

    # 1. Tenure: Calculate the years since the user joined Yelp
    joined = user.yelping_since
    join_year = int(joined.split("-")[0]) if joined else 2000
    current_year = 2024
    tenure_score = min((current_year - join_year) / 10, 1)  # Normalize to 10 years

    # 2. Review count: Indicates activity level
    review_count = user.review_count or 0
    review_count_score = min(review_count / 100, 1)  # Normalize to 100 reviews

    # 3. Compliments: Reflects the quality of reviews
    compliments = user.compliments or 0
    compliments_score = min(compliments / 50, 1)  # Normalize to 50 compliments

    # 4. Fans: Represents social influence
    fans = user.fans or 0
    fans_score = min(fans / 10, 1)  # Normalize to 10 fans

    # 5. Average stars: Measures rating consistency
    average_stars = user.average_stars or 0
    average_stars_score = average_stars / 5  # Normalize to 5 stars

    # Final weighted reliability score
    reliability = (
        0.3 * tenure_score +
        0.3 * review_count_score +
        0.2 * compliments_score +
        0.15 * fans_score +
        0.05 * average_stars_score
    )

    return reliability

def calculate_review_reliability(user_id, review_id, restaurant_avg_score, db_session: Session):
    """
    Calculate the reliability of a review based on user and review data from the database.
    """
    # Retrieve the user data
    user = get_user_data(user_id, db_session)
    if not user:
        return None  # If the user is not found

    # Calculate the user's reliability
    user_reliability = calculate_reliability(user_id, db_session)

    # Retrieve the specific review
    review = get_review_data(review_id, db_session)
    if not review:
        return None  # If the review is not found

    # Calculate the reliability of the review itself
    review_text_length = len(review.text.split())  # The number of words in the review

    # 1. Short reviews (e.g., 2 words or less) decrease reliability slightly
    if review_text_length <= 2:
        review_text_score = 0.9  # Penalize slightly
    else:
        review_text_score = 1  # No penalty

    # 2. Deviation from the restaurant's average score
    review_score = review.stars
    deviation = abs(review_score - restaurant_avg_score)
    deviation_score = max(1 - (deviation / 5), 0.8)  # Minimal impact, capped at 0.8

    # Combine the user's reliability with the review's reliability
    final_reliability = (
        0.8 * user_reliability +
        0.1 * review_text_score +
        0.1 * deviation_score
    )

    return final_reliability
