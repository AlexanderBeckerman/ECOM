
from flask import jsonify, Blueprint, request
from models.models import Review, Restaurant
from base import Session

user_bp = Blueprint('user_bp', __name__)
restaurant_to_reviews = {}
available_restaurants = []
@user_bp.route('/reviews', methods=['GET'])
def get_reviews_by_restaurant_name():
    restaurant_name = request.args.get('name')
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