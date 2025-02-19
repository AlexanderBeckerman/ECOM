import google.generativeai as genai
from sqlalchemy.orm import Session
from models.models import Review, Restaurant
from backend.reliability_calculator import calculate_user_reliability


def generate_improvement_report(restaurant_id, db_session: Session, threshold=3):
    """
    Generates either an improvement or enhancement report for the restaurant based on its ratings.
    If low ratings are detected, the report focuses on improvement points.
    If high ratings are detected, the report focuses on strengths and how to leverage them for greater success.
    """
    restaurant = db_session.query(Restaurant).filter(Restaurant.business_id == str(restaurant_id)).first()
    if not restaurant or not restaurant.scores:
        return "No scores available for this restaurant."

    low_categories = {category: score for category, score in restaurant.scores.items() if score < threshold}

    if low_categories:
        # In case of low ratings, generate an improvement report
        reviews = db_session.query(Review).filter(Review.business_id == str(restaurant_id)).all()

        relevant_reviews = []
        for review in reviews:
            user_reliability = calculate_user_reliability(review.user_id, db_session)
            if user_reliability >= 0.5 and review.stars <= threshold:
                relevant_reviews.append(review.text)

        if not relevant_reviews:
            return "No relevant reviews found from reliable users with low ratings."

        combined_reviews = " ".join(relevant_reviews)
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(
            f"""
            Generate an improvement report for a restaurant based on the following reviews.
            Focus on specific weaknesses mentioned in the reviews (mention them) and provide actionable insights.
            Write the report in bullet points.
            Categories with low scores: {', '.join(low_categories.keys())}.

            Reviews:
            {combined_reviews}
            """
        )
        return response.text.strip()
    else:
        # In case of high ratings, generate a report focusing on strengths and enhancement opportunities
        high_categories = {category: score for category, score in restaurant.scores.items() if score >= threshold}

        if not high_categories:
            return "No significant strengths detected in the restaurant's ratings."

        reviews = db_session.query(Review).filter(Review.business_id == str(restaurant_id)).all()

        positive_reviews = []
        for review in reviews:
            user_reliability = 1  # Default value, can be replaced with calculate_reliability(review.user_id)
            if user_reliability >= 0.5 and review.stars > threshold:
                positive_reviews.append(review.text)

        if not positive_reviews:
            return "No relevant reviews found from reliable users with high ratings."

        combined_positive_reviews = " ".join(positive_reviews)
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(
            f"""
            Generate a report for a restaurant focusing on the strengths mentioned in the following reviews.
            Provide actionable insights on how the restaurant can leverage these strengths to achieve even greater success.
            Write the report in bullet points.
            Categories with high scores: {', '.join(high_categories.keys())}.

            Reviews:
            {combined_positive_reviews}
            """
        )
        return response.text.strip()
