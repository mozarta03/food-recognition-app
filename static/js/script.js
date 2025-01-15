// Select elements
const dropArea = document.getElementById('drop-area');
const imageContainer = document.getElementById('image-container');
const uploadedImage = document.getElementById('uploaded-image');
const nutritionResults = document.getElementById('result-container');
const nutritionList = document.getElementById('nutrition-list');
const foodItem = document.getElementById('food-item');
const analyzeButton = document.getElementById('analyze-btn');
const fileInput = document.getElementById('file-input');
let selectedImageData = null;

// Function to handle file upload and display image
function handleFileUpload(file) {
    console.log("Handling file upload...");
    // If there is already an image displayed, we will fade it out before replacing it
    if (imageContainer.style.display === 'block') {
        imageContainer.style.opacity = '0'; // Fade out the current image
        imageContainer.style.transform = 'translateY(20px)'; // Slide it down

        // Wait for the fade-out transition to finish, then replace the image
        setTimeout(() => {
            const reader = new FileReader();

            reader.onload = (e) => {
                // Update the image source
                uploadedImage.src = e.target.result;
                selectedImageData = e.target.result;

                // Fade the image in and slide it up
                imageContainer.style.opacity = '0'; // Ensure the container is hidden before transitioning
                imageContainer.style.transform = 'translateY(20px)';

                // Show the image container and trigger the transition
                setTimeout(() => {
                    imageContainer.style.display = 'block'; // Make the container visible
                    imageContainer.style.opacity = '1'; // Fade in the image
                    imageContainer.style.transform = 'translateY(0)'; // Slide it up
                }, 10); // Small timeout to allow for the opacity change to take effect
            };

            reader.readAsDataURL(file);
        }, 1000); // Duration of the fade-out transition (same as CSS transition duration)
    } else {
        // If no image is displayed, just show it normally
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImage.src = e.target.result;
            selectedImageData = e.target.result;
            imageContainer.style.display = 'block'; // Make the container visible

            // Trigger the fade-in and slide-up transition
            setTimeout(() => {
                imageContainer.style.opacity = '1';
                imageContainer.style.transform = 'translateY(0)';
            }, 10); // Small timeout to ensure the styles are applied after display change
        };

        reader.readAsDataURL(file);
    }
}

// Handle drop event
dropArea.addEventListener('drop', (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
        handleFileUpload(file);
    }
});

// Handle dragover event (allow dropping)
dropArea.addEventListener('dragover', (event) => {
    event.preventDefault();
    dropArea.style.backgroundColor = "#e0f7ff"; // Highlight drop area
});

// Handle dragleave event (reset drop area style)
dropArea.addEventListener('dragleave', () => {
    dropArea.style.backgroundColor = "#f9f9f9"; // Reset drop area style
});

// Handle click to upload image
dropArea.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        handleFileUpload(file);
    }
});

// Function to format label
function formatLabel(label) {
    return label
        .split('_') // Split the label by underscores
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize each word
        .join(' '); // Join the words with a space
}

// Function to display nutrition info
function displayNutrition(nutritionInfo) {
    const nutritionList = document.getElementById("nutrition-list");
    nutritionList.innerHTML = ""; // Clear previous list items

    console.log("Displaying Nutrition Info:", nutritionInfo);

    // Check if nutritionInfo contains the relevant food results
    if (nutritionInfo && nutritionInfo.foods_search && nutritionInfo.foods_search.results && nutritionInfo.foods_search.results.food && nutritionInfo.foods_search.results.food.length > 0) {
        const food = nutritionInfo.foods_search.results.food[0];  // Use the first food result

        // Ensure that servings and the relevant data exist
        if (food.servings && food.servings.serving) {
            const servings = Array.isArray(food.servings.serving) ? food.servings.serving[0] : food.servings.serving;  // Use the first serving info if it's an array

            const nutritionDetails = {
                "Calories": servings.calories || "N/A",
                "Carbohydrates": servings.carbohydrate || "N/A",
                "Protein": servings.protein || "N/A",
                "Fat": servings.fat || "N/A",
                "Saturated Fat": servings.saturated_fat || "N/A",
                "Cholesterol": servings.cholesterol || "N/A",
                "Sodium": servings.sodium || "N/A",
                "Fiber": servings.fiber || "N/A",
                "Sugar": servings.sugar || "N/A"
            };

            // Loop through the nutritionDetails object and display the data
            Object.entries(nutritionDetails).forEach(([key, value]) => {
                const listItem = document.createElement("li");
                listItem.innerHTML = `<strong>${key}</strong>${value}`;
                nutritionList.appendChild(listItem);
            });

            // Show the nutrition card
            nutritionResults.style.display = 'block';

        } else {
            console.log("No serving information available");
            nutritionList.innerHTML = "<li>No serving information available</li>";
        }
    } else {
        console.log("No nutrition information available");
        nutritionList.innerHTML = "<li>No nutrition information available</li>";
    }
}


// Handle analyze button click
analyzeButton.addEventListener('click', function () {
    const file = fileInput.files[0];
    if (file) {
        console.log("Analyzing file:", file.name);
        nutritionResults.style.display = 'block';

        // Create a FormData object to send the image
        var formData = new FormData();
        formData.append("file", file);

        // Send the file to the FastAPI backend
        fetch("http://127.0.0.1:8000/predict/", {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                console.log("Response status:", response.status);
                return response.json();
            })
            .then((data) => {
                console.log("Response Data:", data); // Debugging line

                if (data.prediction) {
                    var formattedPrediction = formatLabel(data.prediction);

                    document.getElementById("food-item").innerText = `Food Item: ${formattedPrediction}`;
                    document.getElementById("prediction-box");

                    // Fetch and display nutrition info
                    displayNutrition(data.nutrition_info);
                } else {
                    alert("Error: Unable to get prediction");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Error: Unable to process the image");
            });
    } else {
        alert("Please upload an image first!");
    }
});