import { useState, useEffect, useRef } from "react";
import './App.css';
export default function ReviewsComponent() {
    const [restaurants, setRestaurants] = useState([]);
    const [selectedRestaurant, setSelectedRestaurant] = useState("");
    const [reviewsCache, setReviewsCache] = useState({}); // Cache for reviews
    const [scoresCache, setScoresCache] = useState({}); // Cache for scores
    const reviewsContainerRef = useRef(null); // Ref for the reviews container

    useEffect(() => {
        // Fetch restaurant list from API
        fetch("/restaurants")
            .then((res) => res.json())
            .then((data) => setRestaurants(data));
    }, []);

    const fetchReviews = async (restaurantName) => {
        // Reset scroll to top when new restaurant is selected
        if (reviewsContainerRef.current) {
            reviewsContainerRef.current.scrollTop = 0;
        }
        if (reviewsCache[restaurantName]) {
            return; // Use cached data if available
        }
        const response = await fetch(`/reviews?name=${restaurantName}`);
        const data = await response.json();
        setReviewsCache((prev) => ({ ...prev, [restaurantName]: data }));


    };

    const fetchScores = async (restaurantName) => {
        if (scoresCache[restaurantName]) {
            return; // Use cached data if available
        }
        const response = await fetch(`/scores?name=${restaurantName}`);
        const data = await response.json();
        setScoresCache((prev) => ({ ...prev, [restaurantName]: data }));
    };

    const handleRestaurantChange = (e) => {
        const restaurantName = e.target.value;
        setSelectedRestaurant(restaurantName);
        fetchReviews(restaurantName);
        fetchScores(restaurantName);
    };

    return (
        <div className="container">
            <h1>See Reviews For</h1>
            <div className="dropdown-container">
                <select className="dropdown" onChange={handleRestaurantChange}>
                    <option value="">Select a restaurant</option>
                    {restaurants.map((name, index) => (
                        <option key={index} value={name}>
                            {name}
                        </option>
                    ))}
                </select>
            </div>

            <div className="scores-container">
                <h2>Scores for {selectedRestaurant}</h2>
                <ul>
                    {selectedRestaurant &&
                        scoresCache[selectedRestaurant] &&
                        Object.keys(scoresCache[selectedRestaurant]).map((score, index) => (
                            <li key={index}>
                                {score}: {scoresCache[selectedRestaurant][score]}
                            </li>
                        ))}
                </ul>
            </div>

            <div className="reviews-container" ref={reviewsContainerRef}>
                <h2>Reviews for {selectedRestaurant}</h2>
                <ul>
                    {selectedRestaurant &&
                        reviewsCache[selectedRestaurant] &&
                        reviewsCache[selectedRestaurant].map((review, index) => (
                            <li key={index} className="review-item">
                                {review}
                            </li>
                        ))}
                </ul>
            </div>
        </div>
    );
}
