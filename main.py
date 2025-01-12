# from loaders.load_restaurants import load_restaurants
# from loaders.load_users import load_users
# from loaders.load_reviews import load_reviews
# from models.base import create_tables, Session
# from Project.models.restaurant import Restaurant
from concurrent.futures import ThreadPoolExecutor

from transformers import pipeline
import json
import numpy as np
from collections import defaultdict


def get_reviews_for_business(business_id, review_file, num_reviews):
    reviews = []
    reviews_cnt = 0
    with open(review_file, "r", encoding="utf-8") as f:
        print("started reading reviews...")
        for line in f:
            if reviews_cnt >= num_reviews:
                break
            review = json.loads(line)
            if review["business_id"] == business_id:
                reviews.append(review["text"])
                reviews_cnt += 1

    return reviews

# Function to process a chunk of the review file
def process_chunk(chunk, business_id):
    relevant_reviews = []
    for line in chunk:
        review = json.loads(line)
        if review["business_id"] == business_id:
            review_sentences = review["text"].split(".")
            for sentence in review_sentences:
                relevant_reviews.append(sentence)
    return relevant_reviews

# Function to split the file into chunks
def read_file_in_chunks(file_path, chunk_size=1000):
    with open(file_path, "r", encoding="utf-8") as file:
        chunk = []
        for line in file:
            chunk.append(line)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:  # Yield the last chunk
            yield chunk

# Function to read reviews for a business using multithreading
def get_reviews_with_multithreading(business_id, review_file, chunk_size=1000, max_threads=32):
    reviews = []
    with ThreadPoolExecutor(max_threads) as executor:
        futures = [
            executor.submit(process_chunk, chunk, business_id)
            for chunk in read_file_in_chunks(review_file, chunk_size)
        ]
        for future in futures:
            reviews.extend(future.result())
    return reviews


# Function to extract category ratings from reviews
def extract_category_ratings(reviews, categories):
    category_scores = defaultdict(list)

    for review in reviews:
        # Relevance scores
        relevance_results = relevance_classifier(review, candidate_labels=categories)
        relevance_scores = {label: score for label, score in zip(relevance_results["labels"], relevance_results["scores"])}
        # Sentiment analysis for relevant categories
        for category, relevance in relevance_scores.items():
            if relevance > 0.25:  # Consider relevant categories
                context = f"{category}: {review}"
                sentiment_result = sentiment_analyzer(context)[0]
                print("sentiment result", sentiment_result)
                sentiment_score = (
                    3 + 2 * sentiment_result["score"]
                    if sentiment_result["label"] == "POSITIVE"
                    else 3 - 2 * sentiment_result["score"]
                )
                category_scores[category].append(sentiment_score)
                print(f"relevence score: {relevance}, sentiment score: {sentiment_score} for category: {category}, review:\n{review}")
                print()

    # Average scores for each category
    return {category: np.mean(scores) if scores else 0 for category, scores in category_scores.items()}

if __name__ == '__main__':
    # create_tables()  # Create tables if they don't exist

    # # Example: Load restaurant data
    # load_users('../Dataset/yelp_academic_dataset_user.json')
    # load_restaurants('../Dataset/yelp_academic_dataset_business.json')
    # load_reviews('../Dataset/yelp_academic_dataset_review.json')

    # session = Session()
    # restaurant = session.query(Restaurant).filter_by(business_id='some_id').first()
    # print(restaurant.name, restaurant.city)

    business_id = "k0hlBqXX-Bt0vf1op7Jr1w"
    review_cnt = 19
    reviews = get_reviews_for_business(business_id, "../Dataset/yelp_academic_dataset_review.json", review_cnt)
    # reviews = ["Good Greek American food. I highly recomend the saginaki and the chicken modega. Both dishes are rich and over the top so you won't be disappointed.",
    #            "Wife and I have eaten lunch here a few times over the past 6-weeks.  Always a take-out and we have never dined-in.  For the most part the lunches have been OK. Nothing real special to brag about. On the last visit, we ordered a Greek salad and two bowls of chili.\nThe bar tender is a great lady to work with and pleasant.  every time we call in an order, we are told the estimated time it will take to be ready.  Usually 10-minutes.  Every time we arrive, generally between 10-15 minutes, we have to wait an additional 5-+ minutes.  This last visit was no different.  Paid the bill, about $15.00 and went back to the office to eat.  Very disappointed in the $5.95 salad as there was virtually no lettuce and only a 1\/8 wedge of tomato.  The chili was served in 20-ounce styrofoam go-cups.  The chili was Luke-warm at best.  By the way, the drive takes 4-minutes to get to my office from the retaraunt.  I have found the place an OK place as a restaurant but certainly appears to be nothing special.",
    #            "After about 7 minutes of waiting patiently for any form of life to serve us, a chef came out and asked if we had been served. He sent over a waitress. My boyfriend claims his Budweiser didn't taste right and his salad had a slight brown tint to it and barely any green. He got a steak and broccoli. The steak was tiny and shitty, but the broccoli was perfecto. I got a half burnt salmon\/ bacon wrap. Then I went to the bathroom and felt like I was peeing outside in the -4 degree weather. Went back to the table and waited for the waitress for bout 5 mins then took her the credit card. I explained to the manager how cold it is in the women's bathroom. He said, \" would you like me to bring in the fire pit from outside and light a fire for you?\" While laughing at his own joke another worker sitting next to him said, \" it's the same in the men's bathroom , my dick shrivels up every time I go in there.\" This place must be a drug front.",
    #            "Three of us decided to try this place out last weekend after driving past it for months.  I will not be going back.  I can overlook the fact that the place was smoky, due to the fact that there could have been people ordering the saganaki, but there were no redeeming qualities.  Between the three of us, we ordered three drinks.  Two were beers, which is hard to mess up.  The last was supposed to have been a cherry vodka with sprite.  We instead got regular vodka with sometime resembling sprite (with about as much carbonation as a glass of water) and grenadine.  Needless to say, it didn't taste great.  I then ordered the saganaki.  The less than enthusiastic male who brought it out seemed to have added too much oil or something.  It proceeded to continue sizzling and shooting oil all over our table after he put it down.  The bottom was charred and stuck to the pan before it was even cool enough for us to take a bite.  We decided that we were going to cut our losses and head across the street to Fortel's.  We were charged for everything, despite that fact that we only had one bite of the saganaki before decided it was too burnt to eat.  Don't go!!!!!!!!!!!!!!!!!!!!!!!!!  Go to a real Greek place, such as Momos.",
    #            ]
    # Load NLP models
    relevance_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    # Define categories to analyze
    categories = ["food", "service", "atmosphere", "music", "price"]

    # Extract category ratings from reviews
    category_ratings = extract_category_ratings(reviews, categories)
    print(category_ratings)


