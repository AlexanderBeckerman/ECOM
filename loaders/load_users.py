import json
from Project.models.models import User

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
                session.bulk_save_objects(users)
                session.commit()
                users = []
            if count >= limit:
                break

            # Commit remaining records
        if users:
            session.bulk_save_objects(users)
            session.commit()
