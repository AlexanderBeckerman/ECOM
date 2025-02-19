import json
from models.models import Review
from loaders.load_users import load_users_from_reviews, get_user_data
from models.models import User


def load_reviews(session, file_path, limit=50, batch_size=10):
    with open(file_path, 'r', encoding='utf-8') as file:
        reviews = []
        count = 0

        for line in file:
            review = json.loads(line)
            if len(review['text']) > 500:
                continue
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


def load_reviews_by_business(session, file_path, business_id, review_cnt, limit=50, batch_size=10):
    with open(file_path, 'r', encoding='utf-8') as file:
        reviews = []
        users_to_add = []
        count = 0
        user_ids = set()  # Set to keep track of user_ids already processed

        for line in file:
            review = json.loads(line)
            if review['business_id'] == business_id:
                # Add the review to the reviews list
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

                # Check if the user is already added to the list
                if review['user_id'] not in user_ids:
                    user_ids.add(review['user_id'])

                    # Add the user to the users_to_add list
                    user_data = get_user_data(review['user_id'])
                    if user_data:
                        users_to_add.append(User(
                            user_id=user_data['user_id'],
                            name=user_data.get('name', 'Unknown'),
                            joined=user_data.get('yelping_since', 'Unknown'),
                            fans=user_data.get('fans', 0),
                            average_stars=user_data.get('average_stars', 0.0),
                            compliments=user_data.get('compliments', {}).get('total', 0)
                        ))

                count += 1

                # Insert in batches
                if len(reviews) >= batch_size:
                    session.bulk_save_objects(reviews, update_changed_only=True)
                    session.bulk_save_objects(users_to_add)
                    session.commit()
                    reviews = []  # Reset reviews list
                    users_to_add = []  # Reset users list

                if count >= limit or count >= review_cnt:
                    break

        # Commit remaining records
        if reviews:
            session.bulk_save_objects(reviews, update_changed_only=True)
            session.bulk_save_objects(users_to_add)
            session.commit()
