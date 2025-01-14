import json
from Project.models.models import Restaurant

def load_restaurants(session, file_path, limit=50, batch_size=10):

    with open(file_path, 'r') as file:
        restaurants = []
        count = 0

        for line in file:
            restaurant = json.loads(line)
            restaurants.append(Restaurant(
                business_id=restaurant['business_id'],
                name=restaurant['name'],
                address=restaurant['address'],
                city=restaurant['city'],
                state=restaurant['state'],
                stars=restaurant.get('stars', 0.0),
                review_count=restaurant.get('review_count', 0),
                attributes=restaurant.get('attributes', {}),
                categories=restaurant.get('categories', {}),
                hours=restaurant.get('hours', {})
            ))
            count += 1
            if len(restaurants) >= batch_size:
                session.bulk_save_objects(restaurants)
                session.commit()
                restaurants = []

            if count >= limit:
                break

        if restaurants:
            session.bulk_save_objects(restaurants)
            session.commit()
