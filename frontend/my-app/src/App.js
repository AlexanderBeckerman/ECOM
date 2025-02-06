import React, { useState, useEffect } from 'react';

const App = () => {
    const [restaurants, setRestaurants] = useState([]);
    const [selectedRestaurant, setSelectedRestaurant] = useState('');
    const [reviews, setReviews] = useState([]);
    const [scores, setScores] = useState({});

    // Fetch restaurant names
    useEffect(() => {
        fetch('/restaurants')
            .then(response => response.json())
            .then(data => setRestaurants(data));
    }, []);

    // Fetch reviews when a restaurant is selected
    const fetchReviews = (restaurantName) => {
        fetch(`/reviews?name=${restaurantName}`)
            .then(response => response.json())
            .then(data => setReviews(data));
    };

    // Fetch scores when a restaurant is selected
    const fetchScores = (restaurantName) => {
        fetch(`/scores?name=${restaurantName}`)
            .then(response => response.json())
            .then(data => setScores(data));
    };
    return (
        <div style={{ padding: '20px' }}>
            <h1>See Reviews For</h1>
            <select
                onChange={(e) => {
                    setSelectedRestaurant(e.target.value);
                    fetchReviews(e.target.value);
                    fetchScores(e.target.value);
                }}
            >
                <option value="">Select a restaurant</option>
                {restaurants.map((name, index) => (
                    <option key={index} value={name}>
                        {name}
                    </option>
                ))}
            </select>

            <div>
                Scores for {selectedRestaurant}
                <ul>
                    {Object.keys(scores).map((score, index) => (
                        <li key={index}>
                            {score}: {scores[score]}
                        </li>
                    ))}
                </ul>
            </div>

            <div>
                <h2>Reviews for {selectedRestaurant}</h2>
                <ul>
                    {reviews.map((review, index) => (
                        <li key={index}>{review}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default App;
