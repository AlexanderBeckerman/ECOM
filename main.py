from base import create_tables, engine, Session
# from models.models import Restaurant, User, Review
from loaders.load_users import load_users , load_restaurants, load_reviews
from Project.models.models import User, Restaurant, Review
from sqlalchemy import inspect

USERS_FILEPATH = '../Dataset/yelp_academic_dataset_user.json'
RESTAURANTS_FILEPATH = '../Dataset/yelp_academic_dataset_business.json'
REVIEWS_FILEPATH = '../Dataset/yelp_academic_dataset_review.json'

if __name__ == '__main__':
    create_tables()  # Create tables if they don't exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in the database:", tables)
    with Session() as session:
        load_users(session, USERS_FILEPATH)
        # load_restaurants(session, RESTAURANTS_FILEPATH)
        # load_reviews(session, REVIEWS_FILEPATH)


    # # Example: Load restaurant data
    # load_restaurants(engine, RESTAURANTS_FILEPATH)
    # load_reviews(engine, REVIEWS_FILEPATH)

    session = Session()
    user = session.query(User).filter_by(review_count=15).one()
    print(user.name, user.joined)




