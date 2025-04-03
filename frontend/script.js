document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Travel Plan Form Submission
    const travelForm = document.getElementById('travel-form');
    travelForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const source = document.getElementById('source').value;
        const destination = document.getElementById('destination').value;
        const dates = document.getElementById('dates').value;
        const budget = document.getElementById('budget').value;
        const travelers = document.getElementById('travelers').value;
        
        // Get selected interests
        const interestCheckboxes = document.querySelectorAll('#travel-form input[name="interests"]:checked');
        const selectedInterests = Array.from(interestCheckboxes).map(checkbox => checkbox.value);

        // Add custom interests if provided
        const customInterests = document.getElementById('custom-interests').value;
        if (customInterests) {
            const customInterestsList = customInterests.split(',').map(interest => interest.trim());
            selectedInterests.push(...customInterestsList);
        }

        // Check if flight details should be included
        const includeFlights = document.getElementById('include-flights').checked;
        
        // Validate form
        if (!source || !destination || !dates || !budget || !travelers || selectedInterests.length === 0) {
            alert('Please fill in all required fields and select at least one interest.');
            return;
        }
        
        // Show loading spinner
        document.getElementById('planner').classList.remove('active');
        document.getElementById('loading').classList.remove('hidden');
        
        try {
            // Send request to backend
            const response = await fetch('/api/generate-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source,
                    destination,
                    dates,
                    budget,
                    travelers,
                    interests: selectedInterests,
                    include_flights: includeFlights
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Format and display the result
                const resultContent = document.getElementById('result-content');

                // Add airport codes if available
                let headerContent = '';
                if (data.source_code || data.destination_code) {
                    headerContent += '<div class="airport-codes">';
                    if (data.source_code) {
                        headerContent += `<div class="airport-code"><span>From:</span> ${data.source_code}</div>`;
                    }
                    if (data.destination_code) {
                        headerContent += `<div class="airport-code"><span>To:</span> ${data.destination_code}</div>`;
                    }
                    headerContent += '</div>';
                }

                // Check if flight details were requested but not available
                if (includeFlights && !data.flight_details) {
                    console.warn('Flight details were requested but not available');
                    // Add a note about flight details not being available
                    headerContent += '<div class="flight-warning">Flight details could not be retrieved. This could be due to invalid airport codes or API limitations.</div>';
                }

                // Format the travel plan
                const formattedPlan = formatTravelPlan(data.travel_plan);

                // Add the content to the page
                resultContent.innerHTML = headerContent + formattedPlan;

                // The flight table now has a class directly in the HTML

                // Hide loading and show result
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('result').classList.remove('hidden');
            } else {
                throw new Error(data.error || 'Failed to generate travel plan');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);
            
            // Hide loading and show form again
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('planner').classList.add('active');
        }
    });
    
    // Recommendations Form Submission
    const recommendationsForm = document.getElementById('recommendations-form');
    recommendationsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const dates = document.getElementById('rec-dates').value;
        const budget = document.getElementById('rec-budget').value;
        const travelers = document.getElementById('rec-travelers').value;
        
        // Get selected interests
        const interestCheckboxes = document.querySelectorAll('#recommendations-form input[name="interests"]:checked');
        const selectedInterests = Array.from(interestCheckboxes).map(checkbox => checkbox.value);
        
        // Add custom interests if provided
        const customInterests = document.getElementById('rec-custom-interests').value;
        if (customInterests) {
            const customInterestsList = customInterests.split(',').map(interest => interest.trim());
            selectedInterests.push(...customInterestsList);
        }
        
        // Validate form
        if (!dates || !budget || !travelers || selectedInterests.length === 0) {
            alert('Please fill in all required fields and select at least one interest.');
            return;
        }
        
        // Show loading spinner
        document.getElementById('recommendations').classList.remove('active');
        document.getElementById('loading').classList.remove('hidden');
        
        try {
            // Send request to backend
            const response = await fetch('/api/recommend-destinations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dates,
                    budget,
                    travelers,
                    interests: selectedInterests
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Format and display the result
                const resultContent = document.getElementById('result-content');
                resultContent.innerHTML = formatRecommendations(data.recommendations);
                
                // Hide loading and show result
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('result').classList.remove('hidden');
            } else {
                throw new Error(data.error || 'Failed to get recommendations');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);
            
            // Hide loading and show form again
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('recommendations').classList.add('active');
        }
    });
    
    // Airport Code Form Submission
    const airportCodeForm = document.getElementById('airport-code-form');
    airportCodeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Get location
        const location = document.getElementById('location').value;

        // Validate form
        if (!location) {
            alert('Please enter a location.');
            return;
        }

        // Show loading spinner
        document.getElementById('airport-codes').classList.remove('active');
        document.getElementById('loading').classList.remove('hidden');

        try {
            // Send request to backend
            const response = await fetch('/api/get-airport-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    location
                })
            });

            const data = await response.json();

            // Hide loading
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('airport-codes').classList.add('active');

            if (data.success) {
                // Display the result
                document.getElementById('airport-location').textContent = data.location;
                document.getElementById('airport-code-value').textContent = data.airport_code;
                document.getElementById('airport-result').classList.remove('hidden');
            } else {
                alert('Could not find airport code: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);

            // Hide loading and show form again
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('airport-codes').classList.add('active');
        }
    });

    // Back button functionality
    const backButton = document.getElementById('back-btn');
    backButton.addEventListener('click', () => {
        // Hide result and show active tab
        document.getElementById('result').classList.add('hidden');

        // Determine which tab was active
        const activeTabBtn = document.querySelector('.tab-btn.active');
        const activeTabId = activeTabBtn.getAttribute('data-tab');
        document.getElementById(activeTabId).classList.add('active');
    });
    
    // Helper function to format travel plan with Markdown
    function formatTravelPlan(travelPlanText) {
        // Use the marked library to convert Markdown to HTML
        try {
            // Configure marked options
            marked.setOptions({
                breaks: true,  // Convert line breaks to <br>
                gfm: true,     // Use GitHub Flavored Markdown
                headerIds: true, // Add IDs to headers for linking
                mangle: false,  // Don't mangle header IDs
                sanitize: false, // Don't sanitize HTML
                tables: true,   // Enable tables
                smartLists: true, // Use smarter list behavior
                smartypants: true // Use "smart" typographic punctuation
            });

            // Convert Markdown to HTML
            const formattedText = marked.parse(travelPlanText);

            return formattedText;
        } catch (error) {
            console.error('Error parsing Markdown:', error);

            // Fallback to basic formatting if Markdown parsing fails
            let formattedText = travelPlanText.replace(/\n/g, '<br>');
            formattedText = formattedText.replace(/^(Day \d+:.*?)(<br>)/gm, '<h3>$1</h3>$2');
            formattedText = formattedText.replace(/(^|\<br\>)([\w\s]+:)(\<br\>|$)/g, '$1<strong>$2</strong>$3');

            return formattedText;
        }
    }
    
    // Helper function to format recommendations with Markdown
    function formatRecommendations(recommendationsText) {
        // Use the same Markdown parser for recommendations
        return formatTravelPlan(recommendationsText);
    }
});