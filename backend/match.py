import numpy as np

#def euclidean_distance(customer_scores, restaurant_scores):
#    return np.linalg.norm(np.array(customer_scores) - np.array(restaurant_scores))

def calculate_weights(customer_scores):
    # Higher weight for scores near the edges (1 or 5), lower weight for scores near the middle (3)
    return [abs(score - 3) + 1 for score in customer_scores]

def weighted_score(customer_scores, restaurant_scores, weights):
    return sum(w * (5 - abs(r - c)) for w, r, c in zip(weights, restaurant_scores, customer_scores))


def rank_restaurants(customer_scores, restaurants, categories, max_threshold=3, min_threshold=0.3):
    rankings = []
    
    weights = calculate_weights(customer_scores) # option 2
    for restaurant_id, restaurant_data in restaurants.items():
        restaurant_scores = [restaurant_data.get(category, 3) for category in categories] #set default score to 3 if category not found
        
        differences = np.abs(np.array(customer_scores) - np.array(restaurant_scores))
        
        if np.any(differences > max_threshold):  # If any category difference is over the threshold: skip restaurant
            continue
        
        similar_categories = [categories[i] for i in range(len(differences)) if differences[i] <= min_threshold] # mark categories that are similar

        #score = euclidean_distance(customer, restaurant_scores) # option 1
        
        score = weighted_score(customer_scores, restaurant_scores, weights) # option 2

        rankings.append((restaurant_id, score, similar_categories))
    
    return sorted(rankings, key=lambda x: x[1])