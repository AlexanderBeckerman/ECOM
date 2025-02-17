import google.generativeai as genai
from sqlalchemy.orm import Session
from models.models import Review, Restaurant
from backend.reliability_calculator import calculate_reliability

genai.configure(api_key="AIzaSyDDxhcSjPH6qugsGURmzE8tBcr6E3FdQCc")


def generate_improvement_report(restaurant_id, db_session: Session, threshold=3):
    """
    יוצר דוח שיפור לבעל המסעדה על סמך ביקורות עם ציונים נמוכים ממשתמשים אמינים.
    """
    restaurant = db_session.query(Restaurant).filter(Restaurant.business_id == restaurant_id).first()
    if not restaurant or not restaurant.scores:
        return "No scores available for this restaurant."

    low_categories = {category: score for category, score in restaurant.scores.items() if score < threshold}
    if not low_categories:
        return "No significant weaknesses detected in the restaurant's ratings."

    reviews = db_session.query(Review).filter(Review.business_id == restaurant_id).all()

    relevant_reviews = []
    for review in reviews:
        user_reliability = 1  # כרגע ברירת מחדל, ניתן להחליף עם calculate_reliability(review.user_id)
        if user_reliability >= 1 and review.stars <= threshold:
            relevant_reviews.append(review.text)

    if not relevant_reviews:
        return "No relevant reviews found from reliable users with low ratings."

    combined_reviews = " ".join(relevant_reviews)
    model = genai.GenerativeModel("gemini-pro")

    response = model.generate_content(
        f"""
        Generate an improvement report for a restaurant based on the following reviews.
        Focus on specific weaknesses mentioned in the reviews and provide actionable insights.
        Write the report in bullet points.
        Categories with low scores: {', '.join(low_categories.keys())}.

        Reviews:
        {combined_reviews}
        """
    )

    return response.text.strip()
