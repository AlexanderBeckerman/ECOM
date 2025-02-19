import json
from models.models import Restaurant
from backend.restaurant_summarizer import summarize_reviews_for_restaurant
from backend.improvement_report import generate_improvement_report

restaurant_words = {"Food", "Diners", "Restaurants"}

def load_restaurants(session, file_path, limit=50, batch_size=10):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurants = []
        count = 0

        for line in file:
            restaurant = json.loads(line)
            categories = restaurant.get('categories', {})
            if not categories:
                continue
            intersect = set(categories.split(",")) & restaurant_words  # Check if the business is a restaurant
            if not intersect:
                continue
            new_restaurant = Restaurant(
                business_id=restaurant['business_id'],
                name=restaurant['name'],
                address=restaurant['address'],
                city=restaurant['city'],
                state=restaurant['state'],
                stars=restaurant.get('stars', 0.0),
                review_count=restaurant.get('review_count', 0),
                attributes=restaurant.get('attributes', {}),
                categories=categories,
                scores={},
                hours=restaurant.get('hours', {}),
                summary="",  # Placeholder for summary
                improvement_report=""  # Placeholder for improvement report
            )
            restaurants.append(new_restaurant)
            count += 1

            if len(restaurants) >= batch_size:
                session.bulk_save_objects(restaurants, update_changed_only=True)
                session.commit()
                restaurants = []  # Reset restaurants list

            if count >= limit:
                break

        # Commit remaining records
        if restaurants:
            session.bulk_save_objects(restaurants, update_changed_only=True)
            session.commit()