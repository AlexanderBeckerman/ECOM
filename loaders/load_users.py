import json
from models.models import User


def get_user_data(user_id, file_path='./Dataset/yelp_academic_dataset_user.json'):
    """
    Retrieves user data from a JSON file based on the user_id.
    Instead of loading the entire file, it reads line by line.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                user = json.loads(line)
                if user['user_id'] == user_id:
                    return user
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the file {file_path}.")
    return None

def load_users(session, file_path, limit=50, batch_size=10):
    with open(file_path, 'r') as file:
        users = []
        count = 0
        for line in file:
            user = json.loads(line)
            # friends_list = user.get('friends', [])
            # if friends_list:
            #     friends_list = friends_list.split(', ')
            users.append(User(
                user_id=user['user_id'],
                name=user['name'],
                review_count=user.get('review_count', 0),
                joined=user['yelping_since'],
                fans=user.get('fans', 0),
                average_stars=user.get('average_stars', 0.0),
                compliments=user.get('compliments', {}).get('total', 0)
            ))
            count += 1
            # Insert in batches
            if len(users) >= batch_size:
                session.bulk_save_objects(users, update_changed_only=True)
                session.commit()
                users = []
            if count >= limit:
                break

            # Commit remaining records
        if users:
            session.bulk_save_objects(users, update_changed_only=True)
            session.commit()


def load_users_from_reviews(session, reviews, user_data_file='./Dataset/yelp_academic_dataset_user.json', batch_size=100000):
    # Create a list of user_ids from the reviews
    print(reviews)
    user_ids = set(review.user_id for review in reviews)
    users_to_add = []

    # Read user data from the file
    try:
        with open(user_data_file, 'r', encoding='utf-8') as file:
            for line in file:
                user = json.loads(line)
                # If the user_id is in the list of user_ids, add the user
                if user['user_id'] in user_ids:
                    users_to_add.append(User(
                        user_id=user['user_id'],
                        name=user.get('name', 'Unknown'),
                        joined=user.get('yelping_since', 'Unknown'),
                        fans=user.get('fans', 0),
                        average_stars=user.get('average_stars', 0.0),
                        compliments=user.get('compliments', {}).get('total', 0)
                    ))
                    # If the batch size is reached, save and commit the users to the database
                    if len(users_to_add) >= batch_size:
                        session.bulk_save_objects(users_to_add)
                        session.commit()
                        users_to_add = []

    except FileNotFoundError:
        print(f"Error: The file {user_data_file} was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the file {user_data_file}.")

    # Commit remaining users
    if users_to_add:
        session.bulk_save_objects(users_to_add)
        session.commit()

