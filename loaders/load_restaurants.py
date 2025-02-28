import json
from models.models import Restaurant

restaurant_words = {"Diners", "Restaurants", "Bars", "Italian", "Japanese"}


def load_restaurants(session, file_path, limit=50, batch_size=10):
    with open(file_path, 'r', encoding='utf-8') as file:
        restaurants = []
        count = 0

        for line in file:
            restaurant = json.loads(line)
            categories = restaurant.get('categories', {})
            if not categories:
                continue
            intersect = set(categories.split(",")) & restaurant_words # check if the business is indeed a restaurant
            if not intersect:
                continue
            restaurants.append(Restaurant(
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
                score_weights={},
                hours=restaurant.get('hours', {})
            ))
            count += 1
            if len(restaurants) >= batch_size:
                session.bulk_save_objects(restaurants, update_changed_only=True)
                session.commit()
                restaurants = []

            if count >= limit:
                break

        if restaurants:
            session.bulk_save_objects(restaurants, update_changed_only=True)
            session.commit()
