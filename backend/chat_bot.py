
import google.generativeai as genai
import json
GEMINI_API_KEY =  "AIzaSyBJvCs7WGQvuuNIUel_5jytl1FEHBDM4HU"
genai.configure(api_key=GEMINI_API_KEY)

categories = ["food", "service", "music", "price"] # temp local
responses = ["what type of restaurant are you looking for?", "is there something else you want to add?", "I'm sorry its not what you are looking for, is there something you dislike?"] # temp
def classify_request(user_input):
    """Classify user request using OpenAI or Gemini"""
    prompt = (
        f"Analyze the following user request and return a Python dictionary with ratings (1-5) "
        f"for each of these categories: {categories}. Format the response strictly as a valid Python dictionary. "
        f"User Request: {user_input}"
    )

    response = genai.generate_text(prompt=prompt)
    
    try:
        category_ratings = json.loads(response.result.strip().replace("'", '"'))  # Ensure valid JSON format
    except json.JSONDecodeError:
        category_ratings = None  # Default values if parsing fails
    return category_ratings

def user_categories_calculator(user, num_of_responses):
    user_categories_rating = user.categories_rating
    str_input = responses[num_of_responses]
    user_input = input(str_input)
    category_ratings = classify_request(user_input)  
    for category, rating in category_ratings.items():
        if category in user_categories_rating:
            user_categories_rating[category] = (user_categories_rating[category] + rating) / 2
        else:
            user_categories_rating[category] = rating
# Example usage
