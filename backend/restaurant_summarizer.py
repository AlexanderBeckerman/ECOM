import google.generativeai as genai
from sqlalchemy.orm import Session
from models.models import Review
from backend.reliability_calculator import calculate_user_reliability

GOOGLE_API_KEY = "AIzaSyDDxhcSjPH6qugsGURmzE8tBcr6E3FdQCc"

genai.configure(api_key=GOOGLE_API_KEY)


def summarize_reviews_for_restaurant(restaurant_id, db_session: Session, top_n=4, min_words=0):
    """
    Retrieves the most reliable users for a restaurant and generates a summary of their reviews.
    """
    all_reviews = db_session.query(Review).all()
    print(f"Total reviews in DB: {len(all_reviews)}")

    reviews = db_session.query(Review).filter(Review.business_id == str(restaurant_id)).all()

    if not reviews:
        return "No reviews available for this restaurant."

    user_reliabilities = []

    # Calculate reliability for each user
    for review in reviews:
        user_id = review.user_id
        user_reliability = calculate_user_reliability(user_id, db_session)
        review_text = review.text

        # Check if the review meets the minimum word requirement
        if len(review_text.split()) >= min_words:
            user_reliabilities.append((user_id, user_reliability, review_text))

    if not user_reliabilities:
        return "No valid reviews with enough detail found for this restaurant."

    # Sort users by reliability and select the top N most reliable ones
    top_users = sorted(user_reliabilities, key=lambda x: x[1], reverse=True)[:top_n]

    # Combine reviews from the most reliable users
    combined_reviews = " ".join([user_review[2] for user_review in top_users])

    model = genai.GenerativeModel("gemini-pro")

    response = model.generate_content(
        f"Provide a single, cohesive summary of the restaurant based on the following reviews. "
        f"Focus on common themes, strengths, and weaknesses, without listing separate reviews, write 50 words max:\n\n{combined_reviews}"
    )

    return response.text.strip()
