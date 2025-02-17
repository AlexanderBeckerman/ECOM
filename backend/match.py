import numpy as np
from geopy.distance import geodesic

def calculate_weights(customer_scores):
    # Higher weight for scores near the edges (1 or 5), lower weight for scores near the middle (3)
    return [abs(score - 3) + 1 for score in customer_scores]

def weighted_score(customer_scores, restaurant_scores, weights, restaurant_stars, distance_factor):
    base_score = sum(w * (5 - abs(r - c)) for w, r, c in zip(weights, restaurant_scores, customer_scores))
    # Adjust the score based on restaurant rating (scale it to have more influence)
    rating_factor = 0.9 + restaurant_stars / 50 # rating_factor between [0.92, 1.0] for minimal influence
    return base_score * rating_factor * distance_factor

def rank_restaurants(customer_scores, restaurants, customer_location, categories, max_threshold=3, min_threshold=0.3):
    rankings = []
    
    weights = calculate_weights(customer_scores)

    for restaurant_id, restaurant_data in restaurants.items():
        restaurant_scores = [restaurant_data.get(category, 3) for category in categories] # set default score to 3 if category not found
        restaurant_rating = restaurant_data.get("stars", 3)  # set default score to 3 if rating not found
        

        latitude = restaurant_data.get("latitude")
        longitude = restaurant_data.get("longitude")
        restaurant_location = (latitude, longitude) if latitude is not None and longitude is not None else None  # Default location
 
        # Calculate distance factor (farther restaurants get lower scores)
        if customer_location is not None:
            if restaurant_location is None: # If no location provided, minimal distance factor
                distance_factor = 2/3
            else:
                distance = geodesic(customer_location, restaurant_location).kilometers
                # Higher distance reduces score 
                distance_factor = (1 / (1 + (distance / 40000))) # Earth's circumference is 40,075 km, so 20,000 km is halfway around the world => minimum value is 2/3
        else:
            distance_factor = 1.0  # No location provided, no distance factor


        differences = np.abs(np.array(customer_scores) - np.array(restaurant_scores))
        
        if np.any(differences > max_threshold):  # If any category difference is over the threshold: set score to -inf
            score = float('-inf')
            rankings.append((restaurant_id, score, []))
            continue
        
        similar_categories = [categories[i] for i in range(len(differences)) if differences[i] <= min_threshold] # mark categories that are similar
        
        score = weighted_score(customer_scores, restaurant_scores, weights, restaurant_rating, distance_factor)
        
        rankings.append((restaurant_id, score, similar_categories))
    
    return sorted(rankings, key=lambda x: x[1], reverse= True)