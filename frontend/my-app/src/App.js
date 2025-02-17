import {useState, useEffect, useRef} from "react";
import './App.css';

export default function ReviewsComponent() {
    const [restaurants, setRestaurants] = useState([]);
    const [selectedRestaurant, setSelectedRestaurant] = useState("");
    const [reviewsCache, setReviewsCache] = useState({}); // Cache for reviews
    const [scoresCache, setScoresCache] = useState({}); // Cache for scores
    const reviewsContainerRef = useRef(null); // Ref for the reviews container
    const [selectedCategories, setSelectedCategories] = useState([]); // Default selected categories

    const availableCategories = ["food", "service", "music", "price", "drinks", "cleanliness"];
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
        setReviewsCache((prev) => ({...prev, [restaurantName]: data}));


    };

    const fetchScores = async (restaurantName) => {
        if (scoresCache[restaurantName]) {
            return; // Use cached data if available
        }
        const response = await fetch(`/scores?name=${restaurantName}`);
        const data = await response.json();
        setScoresCache((prev) => ({...prev, [restaurantName]: data}));
    };

    const handleRestaurantChange = (e) => {
        const restaurantName = e.target.value;
        setSelectedRestaurant(restaurantName);
        fetchReviews(restaurantName);
        fetchScores(restaurantName);
    };

    const toggleCategory = (category) => {
        setSelectedCategories((prev) =>
            prev.includes(category) ? prev.filter((c) => c !== category) : [...prev, category]
        );
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

            {/* Category Selection (Independent of Restaurant) */}
            <h2>Select Score Categories</h2>
            <div className="categories-container">
                {availableCategories.map((category) => (
                    <button
                        key={category}
                        className={`category-button ${selectedCategories.includes(category) ? "active" : ""}`}
                        onClick={() => toggleCategory(category)}
                    >
                        {category}
                    </button>
                ))}
            </div>

            {selectedRestaurant && scoresCache[selectedRestaurant] && (
                <div className="scores-container">
                    <h2>Scores for {selectedRestaurant}</h2>
                    <ul>
                        {selectedCategories.map((category) =>
                            scoresCache[selectedRestaurant][category] !== undefined ? (
                                <li key={category}>
                                    {category}: {scoresCache[selectedRestaurant][category].toFixed(2)}
                                </li>
                            ) :
                                <li key={category}>
                                    {category}: Not Enough Data
                                </li>
                        )}
                    </ul>
                </div>
            )}

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
