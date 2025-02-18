from sqlalchemy.orm import Session
from models.models import User, Review  # Importing models for accessing the database


def get_user_data(user_id, db_session: Session):
    """
    Retrieve user data from the database based on user_id.
    """
    return db_session.query(User).filter(User.user_id == str(user_id)).first()


def get_review_data(review_id, db_session: Session):
    """
    Retrieve review data from the database based on review_id.
    """
    return db_session.query(Review).filter(Review.review_id == str(review_id)).first()


def calculate_user_reliability(user_id, db_session: Session):
    """
    Calculate the reliability of a user based on attributes from the database.
    """
    user = get_user_data(user_id, db_session)
    if not user:
        return None  # Return None if the user is not found

    # 1. Tenure: Calculate the years since the user joined Yelp
    joined = user.joined
    join_year = int(joined.split("-")[0]) if joined else 2000
    current_year = 2025
    tenure_score = min((current_year - join_year) / 6, 1)  # Normalize to 6 years

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
    user_avg_stars = user.average_stars or 0
    # Define the typical rating range based on actual data
    typical_min = 3.3
    typical_max = 4.5

    if typical_min <= user_avg_stars <= typical_max:
        average_stars_score = 1.0  # Full reliability for typical ratings
    else:
        # Penalize for extreme ratings
        deviation = min(abs(user_avg_stars - typical_min), abs(user_avg_stars - typical_max))
        penalty = 0.25 * deviation  # Adjust penalty factor as needed
        average_stars_score = max(1.0 - penalty, 0.0)

    # Final weighted reliability score
    reliability = (
        0.15 * tenure_score +
        0.3 * review_count_score +
        0.15 * compliments_score +
        0.3 * fans_score +
        0.1 * average_stars_score
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
    user_reliability = calculate_user_reliability(user_id, db_session)

    # Retrieve the specific review
    review = get_review_data(review_id, db_session)
    if not review:
        return None  # If the review is not found

    # Calculate the reliability of the review itself
    review_text_length = len(review.text.split())  # The number of words in the review

    # 1. Short reviews (e.g., 1 word or less) decrease reliability slightly
    review_text_score = 0.5 if review_text_length < 2 else 1

    # 2. Deviation from the restaurant's average score
    review_score = review.stars
    deviation = abs(review_score - restaurant_avg_score)
    deviation_score = max(1 - (deviation / 5), 0.8)

    # 3. Compute base reliability score (without useful bonus)
    base_reliability = (
        0.8 * user_reliability +
        0.1 * review_text_score +
        0.1 * deviation_score
    )

    # 4. Apply useful bonus *only if useful > 0*
    useful_bonus = 0.02 * min(review.useful, 10) if review.useful > 0 else 0  # Max bonus = 0.2

    # Final reliability score with useful bonus
    final_reliability = min(1, base_reliability + useful_bonus)  # Ensure max 1

    return final_reliability
