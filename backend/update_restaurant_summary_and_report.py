from models.models import Restaurant
from backend.restaurant_summarizer import summarize_reviews_for_restaurant
from backend.improvement_report import generate_improvement_report


def update_restaurant_summary_and_report(session):
    all_restaurants = session.query(Restaurant).all()
    for restaurant in all_restaurants:
        # Calculate the restaurant's summary based on its reviews
        summary = summarize_reviews_for_restaurant(restaurant.business_id, session)
        restaurant.summary = summary  # Save the summary to the restaurant object

        # Calculate the improvement report based on the restaurant's ratings and reviews
        improvement_report = generate_improvement_report(restaurant.business_id, session)
        restaurant.improvement_report = improvement_report  # Save the improvement report

        # Commit changes to the database (save the summary and report)
        session.commit()
