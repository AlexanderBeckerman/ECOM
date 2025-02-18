import {useState, useEffect, useRef} from "react";
import './App.css';

export default function ReviewsComponent() {
    const [restaurants, setRestaurants] = useState([]);
    const [selectedRestaurant, setSelectedRestaurant] = useState("");
    const [reviewsCache, setReviewsCache] = useState({}); // Cache for reviews
    const [scoresCache, setScoresCache] = useState({}); // Cache for scores
    const reviewsContainerRef = useRef(null); // Ref for the reviews container
    // const [selectedCategories, setSelectedCategories] = useState([]); // Default selected categories
    const [weights, SetWeights] = useState({}); // Default weights for categories
    const [recommendations, setRecommendations] = useState([]);
    const [showRecommendations, setShowRecommendations] = useState(false);
    const [appliedPreferences, setAppliedPreferences] = useState(false);

    const availableCategories = ["food", "service", "music", "price", "cleanliness"];

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

    const fetchRecommendations = () => {
        fetch("/recommendations")
            .then((res) => res.json())
            .then((data) => setRecommendations(data));
    };

    const fetchScores = async (restaurantName) => {
        if (scoresCache[restaurantName]) {
            return; // Use cached data if available
        }
        const response = await fetch(`/scores?name=${restaurantName}`);
        const data = await response.json();
        setScoresCache((prev) => ({...prev, [restaurantName]: data}));
    };
    const fetchRestaurantData = (restaurant) => {
        setSelectedRestaurant(restaurant);
        fetchReviews(restaurant);
        fetchScores(restaurant);
    }
    const handleRestaurantChange = (e) => {
        const restaurantName = e.target.value;
        setSelectedRestaurant(restaurantName);
        fetchReviews(restaurantName);
        fetchScores(restaurantName);
    };

    // const toggleCategory = (category) => {
    //     setSelectedCategories((prev) =>
    //         prev.includes(category) ? prev.filter((c) => c !== category) : [...prev, category]
    //     );
    // };

    // Initialize category weights with default 3
    useEffect(() => {
        SetWeights(prevState => availableCategories.reduce((acc, category) => ({
            ...acc,
            [category]: prevState[category] || 3
        }), {}));
    }, []);

    const handleSliderChange = (category, value) => {
        setShowRecommendations(false);
        setAppliedPreferences(false);
        setSelectedRestaurant("");
        SetWeights((prevWeights) => ({
            ...prevWeights,
            [category]: parseFloat(value),
        }));
    };

    const handleSubmitPreferences = () => {
        fetch("/userpreferences", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(weights),
        }).then(() => {
            setShowRecommendations(true);
        });
        fetchRecommendations()
        setAppliedPreferences(true);
    };

    return (
        <div className="container">
            <header className="app-header">
                <h1 className="app-title">Spot<span className="highlight">On</span></h1>
            </header>
            {/*<h1>See Reviews For</h1>*/}
            {/*<div className="dropdown-container">*/}
            {/*    <select className="dropdown" onChange={handleRestaurantChange}>*/}
            {/*        <option value="">Select a restaurant</option>*/}
            {/*        {restaurants.map((name, index) => (*/}
            {/*            <option key={index} value={name}>*/}
            {/*                {name}*/}
            {/*            </option>*/}
            {/*        ))}*/}
            {/*    </select>*/}
            {/*</div>*/}

            {/*/!* Category Selection (Independent of Restaurant) *!/*/}
            {/*<h2>Select Score Categories</h2>*/}
            {/*<div className="categories-container">*/}
            {/*    {availableCategories.map((category) => (*/}
            {/*        <button*/}
            {/*            key={category}*/}
            {/*            className={`category-button ${selectedCategories.includes(category) ? "active" : ""}`}*/}
            {/*            onClick={() => toggleCategory(category)}*/}
            {/*        >*/}
            {/*            {category}*/}
            {/*        </button>*/}
            {/*    ))}*/}
            {/*</div>*/}
            {/* Category Sliders */}
            <div className="category-container">
                <h2>Adjust Category Importance</h2>
                <div className="sliders">
                    {Object.keys(weights).map((category) => (
                        <div key={category} className="slider-group">
                            <label>{category}: {weights[category]}</label>
                            <input
                                type="range"
                                min="1"
                                max="5"
                                step="0.5"
                                value={weights[category]}
                                onChange={(e) => handleSliderChange(category, e.target.value)}
                            />
                        </div>
                    ))}
                </div>
                <button className="submit-button" onClick={handleSubmitPreferences}>Apply Preferences</button>
            </div>
            {/* Show Recommendations Button */}
            {appliedPreferences && (
                <button className="recommendations-btn" onClick={() => setShowRecommendations(!showRecommendations)}>
                    Show Recommendations
                </button>
            )}
            {/* Recommendations List */}
            {showRecommendations && recommendations.length > 0 && (
                <div className="recommendations">
                    <h2>Recommended Restaurants</h2>
                    <ul>
                        {recommendations.map((restaurant, index) => (
                            <li key={index} onClick={() => fetchRestaurantData(restaurant[0])}>{restaurant[0]}</li>
                        ))}
                    </ul>
                </div>
            )}
            {showRecommendations && selectedRestaurant && (
                <>
                    {scoresCache[selectedRestaurant] && (
                        <div className="scores-container">
                            <h2>Scores for {selectedRestaurant}</h2>
                            <ul>
                                {availableCategories.map((category) =>
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
                </>
            )}
        </div>
    );
}
