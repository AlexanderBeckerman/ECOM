from flask import jsonify, Blueprint, request
from models.models import Review, Restaurant
from base import Session
from backend.match import match_restaurants_to_user

user_bp = Blueprint('user_bp', __name__)
restaurant_to_reviews = {}
available_restaurants = []
user_preferences = {}


@user_bp.route('/reviews', methods=['GET'])
def get_reviews_by_restaurant_name():
    restaurant_name = request.args.get('name')
    global restaurant_to_reviews
    if restaurant_name in restaurant_to_reviews:
        return jsonify(restaurant_to_reviews[restaurant_name])

    with Session() as session:
        reviews = (
            session.query(Review.text)
            .join(Restaurant, Restaurant.business_id == Review.business_id)
            .filter(Restaurant.name == restaurant_name)
            .all()
        )

        restaurant_to_reviews[restaurant_name] = [r[0] for r in reviews]
        return jsonify(restaurant_to_reviews[restaurant_name])  # Return list of review texts


@user_bp.route('/restaurants', methods=['GET'])
def get_available_restaurants():
    global available_restaurants
    if available_restaurants:
        return jsonify(available_restaurants)

    with Session() as session:
        restaurants = session.query(Restaurant.name).all()
        return jsonify([r[0] for r in restaurants])


@user_bp.route('/scores', methods=['GET'])
def get_scores_for_restaurant():
    restaurant_name = request.args.get('name')
    with Session() as session:
        scores = (
            session.query(Restaurant.scores)
            .filter(Restaurant.name == restaurant_name)
            .first()
        )
        return jsonify(scores[0]) if scores else jsonify({})


@user_bp.route('/userpreferences', methods=['POST'])
def update_preferences():
    global user_preferences
    user_preferences = request.json  # Receive category weights from frontend
    print("Received preferences:", user_preferences)

    return jsonify({"message": "Preferences updated successfully"}), 200


@user_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    global user_preferences
    if not user_preferences:
        return jsonify({"message": "No preferences set"}), 400

    user_scores = list(user_preferences.values())
    categories = list(user_preferences.keys())

    results = match_restaurants_to_user(user_scores, categories)
    print("Recommendations:", results)
    return jsonify(results)
