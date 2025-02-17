
import google.generativeai as genai
import json
import warnings
warnings.filterwarnings("ignore", message="All log messages before absl::InitializeLog() is called are written to STDERR")


GEMINI_API_KEY =  "AIzaSyBJvCs7WGQvuuNIUel_5jytl1FEHBDM4HU"
genai.configure(api_key=GEMINI_API_KEY)

categories = ["food", "service", "music", "price"] # temp local
responses = ["what type of restaurant are you looking for?", "is there something else you want to add?", "I'm sorry its not what you are looking for, is there something you dislike?"] # temp
model = genai.GenerativeModel("gemini-pro")
def classify_request(user_input):
    """Classify user request using OpenAI or Gemini"""
    prompt = (
        f"Analyze the following user request and return a Python dictionary with ratings (1-5), 1 is bad and 5 is good, float values are allowed. "
        f"for each of these categories: {categories}, if it is related to the category. Format the response strictly as a valid Python dictionary. "
        f"User Request: {user_input}"
    )

    response = model.generate_content(prompt)
    text = response.text.strip().replace("'", '"').replace("\n", "").replace(" ", "")
    l_text = len(text)
    for i in range(l_text):
        if text[i] == "{":
            text = text[i:]
            l_text =l_text - i
            break
    for i in range(l_text-1, 0, -1):
        if text[i] == "}":
            text = text[:i+1]
            break
    try:
        category_ratings = json.loads(text)  # Ensure valid JSON format
    except json.JSONDecodeError:
        category_ratings = None  # Default values if parsing fails
    return category_ratings

def user_categories_calculator(user, num_of_responses):
    user_categories_rating = user.categories_rating
    str_input = responses[num_of_responses]
    user_input = input(str_input)
    category_ratings = classify_request(user_input)  
    for category, rating in category_ratings.items():
        if rating !=0:
            if category in user_categories_rating:
                user_categories_rating[category] = (user_categories_rating[category] + rating) / 2
            else:
                user_categories_rating[category] = rating
# Example usage
# user_input = input("What type of restaurant are you looking for?")
# catagory_ratings = classify_request(user_input)
# print(f"catagory_ratings = {catagory_ratings}")