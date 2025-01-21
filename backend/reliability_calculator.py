
import json

def get_user_data(user_id, file_path):
    # Open the JSON file and read through each line
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            user = json.loads(line)
            # If the user_id matches, return the user's data
            if user['user_id'] == user_id:
                return user
    # Return None if no matching user is found
    return None

def calculate_reliability(user_id, file_path):
    # Get user data from JSON based on user_id
    user = get_user_data(user_id, file_path)
    if not user:
        return None  # Return None if the user is not found

    # 1. Tenure: Calculate the years since the user joined Yelp
    joined = user.get("yelping_since", "2000-01-01")
    join_year = int(joined.split("-")[0]) if joined else 2000
    current_year = 2024
    tenure_score = min((current_year - join_year) / 10, 1)  # Normalize to 10 years

    # 2. Review count: Indicates activity level
    review_count = user.get("review_count", 0)
    review_count_score = min(review_count / 100, 1)  # Normalize to 100 reviews

    # 3. Compliments: Reflects the quality of reviews
    compliments = user.get("compliments", 0)
    compliments_score = min(compliments / 50, 1)  # Normalize to 50 compliments

    # 4. Fans: Represents social influence
    fans = user.get("fans", 0)
    fans_score = min(fans / 10, 1)  # Normalize to 10 fans

    # 5. Average stars: Measures rating consistency
    average_stars = user.get("average_stars", 0)
    average_stars_score = average_stars / 5  # Normalize to 5 stars

    # Final weighted reliability score
    reliability = (
        0.3 * tenure_score +
        0.3 * review_count_score +
        0.2 * compliments_score +
        0.15 * fans_score +
        0.05 * average_stars_score
    )

    return reliability

def calculate_review_reliability(user_id, review_id, file_path, review_file_path):
    # Retrieve the user data,
    user = get_user_data(user_id, file_path)
    if not user:
        return None  # If the user is not found

    # Calculate the user's reliability
    user_reliability = calculate_reliability(user_id, file_path)

    # Retrieve the specific review
    review = get_review_data_from_json(review_id, review_file_path)
    if not review:
        return None  #If the review is not found

    # Calculate the reliability of the review itself
    review_length = len(review.get("text", "").split())  # The number of words in the review
    review_score = review.get("stars", 0)  # Rating given in the review

    # Longer reviews may indicate more investment and thus higher reliability
    review_reliability_score = min(review_length / 200, 1)  # Review reliability based on length
    score_reliability = min(abs(review_score - 3) / 2, 1)  # Deviation from average rating (3) reliability

    # Combine the user's reliability with the review's reliability
    final_reliability = 0.7 * user_reliability + 0.3 * review_reliability_score + 0.2 * score_reliability

    return final_reliability