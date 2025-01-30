from flask import jsonify, Blueprint, request
from models.models import Review, Restaurant
from base import Session

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/reviews', methods=['GET'])
def get_reviews_by_restaurant_name():
    restaurant_name = request.args.get('name')
    with Session() as session:
        reviews = (
            session.query(Review.text)
            .join(Restaurant, Restaurant.business_id == Review.business_id)
            .filter(Restaurant.name == restaurant_name)
            .all()
        )
        return jsonify([r[0] for r in reviews])  # Return list of review texts


@user_bp.route('/restaurants', methods=['GET'])
def get_available_restaurants():
    with Session() as session:
        restaurants = session.query(Restaurant.name).all()
        return jsonify([r[0] for r in restaurants])
