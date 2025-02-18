import numpy as np
from base import Session
from models.models import Restaurant

def calculate_weights(customer_scores):
    # Higher weight for scores near the edges (1 or 5), lower weight for scores near the middle (3)
    return [abs(score - 3) + 1 for score in customer_scores]

def weighted_score(customer_scores, restaurant_scores, weights, restaurant_stars):
    base_score = sum(w * (5 - abs(r - c)) for w, r, c in zip(weights, restaurant_scores, customer_scores))
    # Adjust the score based on restaurant rating (scale it to have more influence)
    rating_factor = 0.9 + restaurant_stars / 50 # rating_factor between [0.92, 1.0] for minimal influence
    return base_score * rating_factor

def location_match_score(customer_city, customer_state, restaurant_city, restaurant_state):
    if customer_state and restaurant_state and customer_state.lower() == restaurant_state.lower():
        if customer_city and restaurant_city and customer_city.lower() == restaurant_city.lower():
            return 1000  # City and state match => bump all the restaurants in the same city to the top
        return 500  # Only state matches
    return 0  # No match

def rank_restaurants(customer_scores, restaurants, categories, customer_location=None, max_threshold=3, min_threshold=0.3):
    rankings = []
    
    weights = calculate_weights(customer_scores)

    for restaurant in restaurants:
        temp = restaurant.scores
        restaurant_scores = [temp.get(category, 3) for category in categories] # set default score to 3 if category not found

        restaurant_rating = getattr(restaurant, "stars", 3)  # set default score to 3 if rating not found
        
        differences = np.abs(np.array(customer_scores) - np.array(restaurant_scores))
        
        if np.any(differences > max_threshold):  # If any category difference is over the threshold: set score to -inf
            score = float('-inf')
            rankings.append((restaurant.business_id, score, []))
            continue
        
        similar_categories = [categories[i] for i in range(len(differences)) if differences[i] <= min_threshold] # mark categories that are similar
        
        score = weighted_score(customer_scores, restaurant_scores, weights, restaurant_rating)
        
        if(customer_location is not None):
            city = getattr(restaurant, "city", None)
            state = getattr(restaurant, "state", None)
            score += location_match_score(customer_location[0], customer_location[1], city, state)

        rankings.append((restaurant.business_id, score, similar_categories))
    
    return sorted(rankings, key=lambda x: x[1], reverse= True)

def match_restaurants_to_user(user_scores, categories, location=None):
    with Session() as session:
        restaurants = session.query(Restaurant).all()
        results = rank_restaurants(user_scores, restaurants, categories=categories, customer_location=location)
        #for result in results:
        #    print(result)