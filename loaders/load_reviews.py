import json
from Project.models.models import Review


def load_reviews(session, file_path, limit=50, batch_size=10):
    with open(file_path, 'r') as file:
        reviews = []
        count = 0

        for line in file:
            review = json.loads(line)
            reviews.append(Review(
                review_id=review['review_id'],
                user_id=review['user_id'],  # Foreign key to User
                business_id=review['business_id'],  # Foreign key to Restaurant
                stars=review.get('stars', 0.0),
                date=review['date'],
                text=review.get('text', ''),
                useful=review.get('useful', 0),
                funny=review.get('funny', 0),
                cool=review.get('cool', 0)
            ))
            count += 1

            # Insert in batches
            if len(reviews) >= batch_size:
                session.bulk_save_objects(reviews)
                session.commit()
                reviews = []

            if count >= limit:
                break

        # Commit remaining records
        if reviews:
            session.bulk_save_objects(reviews)
            session.commit()
