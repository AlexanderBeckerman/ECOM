import google.generativeai as genai
from sqlalchemy.orm import Session
from models.models import Review
from backend.reliability_calculator import calculate_reliability

GOOGLE_API_KEY = "AIzaSyDDxhcSjPH6qugsGURmzE8tBcr6E3FdQCc"

# אתחול ה-API של Gemini
genai.configure(api_key=GOOGLE_API_KEY)


def summarize_reviews_for_restaurant(restaurant_id, db_session: Session, top_n=4, min_words=0):
    """
    שולף את המשתמשים האמינים ביותר למסעדה ויוצר סיכום ביקורות בעזרת Gemini.
    """
    print("Function Called!")
    all_reviews = db_session.query(Review).all()
    print(f"Total reviews in DB: {len(all_reviews)}")

    # שולף את כל הביקורות למסעדה הנתונה
    reviews = db_session.query(Review).filter(Review.business_id == restaurant_id).all()

    if not reviews:
        print("No reviews available for this restaurant.")
        return "No reviews available for this restaurant."

    user_reliabilities = []

    # חישוב אמינות לכל משתמש על סמך הביקורות שלו
    for review in reviews:
        user_id = review.user_id
        user_reliability = 1  # כאן ניתן להחליף עם חישוב האמינות האמיתי

        review_text = review.text
        # בודק אם הביקורת עומדת בתנאי המינימום של מילים
        if len(review_text.split()) >= min_words:
            user_reliabilities.append((user_id, user_reliability, review_text))

    # אם אין ביקורות שעומדות בתנאים
    if not user_reliabilities:
        return "No valid reviews with enough detail found for this restaurant."

    # ממיין את המשתמשים לפי האמינות ובוחר את ה-N הטובים ביותר
    top_users = sorted(user_reliabilities, key=lambda x: x[1], reverse=True)[:top_n]
    print(top_users)
    # מאחד את כל הביקורות של המשתמשים האמינים ביותר
    combined_reviews = " ".join([user_review[2] for user_review in top_users])

    # יוצר אובייקט של מודל Gemini
    model = genai.GenerativeModel("gemini-pro")

    response = model.generate_content(
        f"Provide a single, cohesive summary of the restaurant based on the following reviews. "
        f"Focus on common themes, strengths, and weaknesses, without listing separate reviews, write 50 words max:\n\n{combined_reviews}"
    )

    return response.text.strip()


