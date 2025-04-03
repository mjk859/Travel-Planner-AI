import os
import re
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API with your API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No Gemini API key found. Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_API_KEY)

# Use the Gemini 2.0 Flash model
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_travel_plan(source, destination, dates, budget, travelers, interests, include_flights=False):
    """
    Generate a travel plan using Gemini 2.0 Flash model.

    Args:
        source (str): Departure location
        destination (str): Travel destination
        dates (str): Travel dates
        budget (str): Budget for the trip
        travelers (str): Number of travelers
        interests (list): List of interests/preferences
        include_flights (bool): Whether to include flight details

    Returns:
        dict: Generated travel plan and airport codes
    """
    # Get airport codes for source and destination
    source_code = get_airport_code(source)
    destination_code = get_airport_code(destination)

    # Format interests as a comma-separated string
    interests_str = ", ".join(interests)

    # Create a prompt for the Gemini model
    prompt = f"""
    Act as an expert travel planner. Create a detailed travel itinerary with the following information:

    - Source: {source} {f"({source_code})" if source_code else ""}
    - Destination: {destination} {f"({destination_code})" if destination_code else ""}
    - Travel Dates: {dates}
    - Budget: {budget}
    - Number of Travelers: {travelers}
    - Interests: {interests_str}

    Please include:
    1. A day-by-day itinerary with activities and attractions
    2. Estimated costs for accommodations, food, transportation, and activities
    3. Recommended places to stay within the budget
    4. Local transportation options
    5. Must-try local food and restaurants
    6. Tips for the destination considering the interests provided
    7. Any special considerations based on the travel dates (seasonal events, weather, etc.)

    Format your response in Markdown with proper headings (using # for main headings, ## for subheadings),
    bullet points, and emphasis where appropriate. Make it visually structured and easy to read.
    """

    # Generate content using Gemini
    response = model.generate_content(prompt)
    travel_plan = response.text

    # Add flight details if requested and airport codes are available
    flight_details = None
    if include_flights and source_code and destination_code:
        # Try to extract a date in YYYY-MM-DD format from the dates string
        # This is a simple approach - in a production app, you would want more robust date parsing
        travel_date = None

        # Try to find a date in YYYY-MM-DD format
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', dates)
        if date_match:
            travel_date = date_match.group(1)
        else:
            # Try to parse common date formats
            # For simplicity, we will just use a default date if we can not parse
            # In a real app, you would want to use a proper date parsing library
            travel_date = "2025-04-02"  # Default date for testing

        # Get flight details
        flight_data = get_flight_details(source_code, destination_code, travel_date)

        if flight_data:
            # Check if there was an error
            if 'error' in flight_data:
                flight_details = f"## ✈️ Flight Information\n\n{flight_data['error']}\n\nPlease try again later or check your airport codes."
            else:
                flight_details = format_flight_details_markdown(flight_data, source_code, destination_code)

            # Combine flight details with travel plan
            travel_plan = flight_details + "\n\n" + travel_plan

    return {
        "travel_plan": travel_plan,
        "source_code": source_code,
        "destination_code": destination_code,
        "flight_details": flight_details if include_flights else None
    }

def get_airport_code(location):
    """
    Convert a location name to its corresponding airport code using Gemini API.

    Args:
        location (str): Name of the location (city, country, etc.)

    Returns:
        str: 3-letter IATA airport code or None if not found
    """
    prompt = f"""
    Convert the following location to its primary international airport's IATA code:
    Location: {location}

    Respond with ONLY the 3-letter IATA airport code in uppercase. If there are multiple major airports,
    provide the code for the most commonly used international airport. If you cannot determine the airport code
    with confidence, respond with "UNKNOWN".
    """

    try:
        response = model.generate_content(prompt)
        airport_code = response.text.strip()

        # Validate that the response is a 3-letter code
        if re.match(r'^[A-Z]{3}$', airport_code):
            return airport_code
        else:
            # If the response contains a 3-letter code, extract it
            match = re.search(r'[A-Z]{3}', airport_code)
            if match:
                return match.group(0)
            return None
    except Exception as e:
        print(f"Error getting airport code: {e}")
        return None

def get_flight_details(source_code, destination_code, date):
    """
    Generate flight details using Gemini.

    Args:
        source_code (str): Source airport code
        destination_code (str): Destination airport code
        date (str): Travel date in YYYY-MM-DD format

    Returns:
        dict: Flight details
    """
    try:
        # Format the date if needed (assuming date might be in various formats)
        # If date is not in YYYY-MM-DD format, we need to convert it
        formatted_date = date
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            # This is a simple conversion - in a real app, you would want more robust date parsing
            # For now, we will just use a default date if the format doesn't match
            formatted_date = "2025-04-02"  # Default date

        # Instead of using an API, we'll create a direct link to Google Flights
        # and generate some basic flight information using Gemini

        # Create a Google Flights URL that users can visit
        google_flights_url = f"https://www.google.com/travel/flights?hl=en&curr=USD&q=flights%20{source_code}%20to%20{destination_code}&dates={formatted_date}"

        # Use Gemini to generate some basic flight information
        prompt = f"""
        Generate realistic flight information for a flight from {source_code} to {destination_code} on {formatted_date}.

        Include the following details for 3 flight options:
        1. Airline name
        2. Price (in USD)
        3. Duration
        4. Departure time
        5. Arrival time
        6. Number of stops

        Format the response as JSON with this structure:
        {{
          "best_flights": [
            {{
              "airline": "Airline Name",
              "price": "1234",
              "total_duration": 360,
              "flights": [
                {{
                  "departure_airport": {{"id": "{source_code}", "name": "Source Airport", "time": "10:00"}},
                  "arrival_airport": {{"id": "{destination_code}", "name": "Destination Airport", "time": "14:00"}},
                  "airline": "Airline Name",
                  "flight_number": "AB123",
                  "duration": 240,
                  "airplane": "Boeing 737"
                }}
              ]
            }}
          ],
          "search_metadata": {{
            "google_flights_url": "{google_flights_url}"
          }}
        }}

        Make the data realistic but varied between the 3 options. Include both direct and connecting flights.
        """

        # Generate flight data using Gemini
        response = model.generate_content(prompt)

        try:
            # Try to parse the response as JSON
            flight_data = json.loads(response.text)
            return flight_data
        except json.JSONDecodeError:
            # If the response is not valid JSON, extract it from the text
            json_match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
            if json_match:
                try:
                    flight_data = json.loads(json_match.group(1))
                    return flight_data
                except json.JSONDecodeError:
                    return {
                        'error': "Unable to parse flight data from Gemini response"
                    }
            else:
                return {
                    'error': "Unable to retrieve flight data in the correct format"
                }

    except Exception as e:
        print(f"Error generating flight data: {e}")
        return {
            'error': f"Error generating flight data: {str(e)}"
        }

def format_flight_details_markdown(flight_data, source_code, destination_code):
    """
    Format flight details as Markdown with table format.

    Args:
        flight_data (dict): Flight data from SerpAPI
        source_code (str): Source airport code
        destination_code (str): Destination airport code

    Returns:
        str: Markdown formatted flight details
    """
    if not flight_data:
        return "## ✈️ Flight Information\n\nUnable to retrieve flight details at this time.\n\nPlease try again later."

    if 'error' in flight_data:
        return f"## ✈️ Flight Information\n\n{flight_data['error']}\n\nPlease check your airport codes and try again."

    if 'best_flights' not in flight_data or not flight_data['best_flights']:
        return "## ✈️ Flight Information\n\nNo flights found for this route and date.\n\nPlease try different dates or destinations."

    # Get up to 3 flight options
    flights = flight_data['best_flights'][:3]

    # Check if we're using mock data with different airport codes
    # If so, we'll display the user's requested codes but note that we're showing sample data
    actual_source = None
    actual_destination = None

    if flights and flights[0].get('flights'):
        first_flight = flights[0]['flights'][0]
        last_flight = flights[0]['flights'][-1]

        if first_flight.get('departure_airport', {}).get('id'):
            actual_source = first_flight['departure_airport']['id']

        if last_flight.get('arrival_airport', {}).get('id'):
            actual_destination = last_flight['arrival_airport']['id']

    markdown = "## ✈️ Flight Options\n\n"

    if actual_source and actual_destination and (actual_source != source_code or actual_destination != destination_code):
        markdown += f"**Requested Route**: {source_code} to {destination_code}\n\n"
        markdown += "*Note: Showing sample flight data for demonstration purposes.*\n\n"
    else:
        markdown += f"**From**: {source_code} to **{destination_code}**\n\n"

    # Create a table for flight options with proper spacing
    # Use HTML directly for better control over table formatting
    markdown += "<div class='flight-table-container'>\n"
    markdown += "<table class='flight-table'>\n"
    markdown += "<thead>\n"
    markdown += "<tr>\n"
    markdown += "<th>Airline</th>\n"
    markdown += "<th>Price</th>\n"
    markdown += "<th>Duration</th>\n"
    markdown += "<th>Departure</th>\n"
    markdown += "<th>Arrival</th>\n"
    markdown += "<th>Stops</th>\n"
    markdown += "<th>Book</th>\n"
    markdown += "</tr>\n"
    markdown += "</thead>\n"
    markdown += "<tbody>\n"

    for flight in flights:
        # Get basic flight info
        airline = flight.get('airline', 'Multiple')
        price = flight.get('price', 'N/A')

        # Format duration
        total_duration_min = flight.get('total_duration', 0)
        total_duration_hr = total_duration_min // 60
        total_duration_min_remainder = total_duration_min % 60
        duration = f"{total_duration_hr}h {total_duration_min_remainder}m"

        # Get first and last flight segments
        flight_segments = flight.get('flights', [])
        if flight_segments:
            first_segment = flight_segments[0]
            last_segment = flight_segments[-1]

            # Departure info
            departure = first_segment.get('departure_airport', {})
            dep_time = departure.get('time', '').split(' ')[1] if ' ' in departure.get('time', '') else departure.get('time', '')
            dep_info = f"{dep_time} ({departure.get('id', '')})"

            # Arrival info
            arrival = last_segment.get('arrival_airport', {})
            arr_time = arrival.get('time', '').split(' ')[1] if ' ' in arrival.get('time', '') else arrival.get('time', '')
            arr_info = f"{arr_time} ({arrival.get('id', '')})"

            # Stops
            stops = len(flight_segments) - 1
            stops_text = "Nonstop" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"

            # Booking link
            booking_link = "[Book](" + flight_data['search_metadata']['google_flights_url'] + ")"

            # Add row to table with HTML
            markdown += "<tr>\n"
            markdown += f"<td>{airline}</td>\n"
            markdown += f"<td>${price}</td>\n"
            markdown += f"<td>{duration}</td>\n"
            markdown += f"<td>{dep_info}</td>\n"
            markdown += f"<td>{arr_info}</td>\n"
            markdown += f"<td>{stops_text}</td>\n"
            markdown += f"<td><a href='{flight_data['search_metadata']['google_flights_url']}' target='_blank'>Book</a></td>\n"
            markdown += "</tr>\n"

    # Close the table
    markdown += "</tbody>\n"
    markdown += "</table>\n"
    markdown += "</div>\n"

    markdown += "\n### Flight Details\n\n"

    # Add detailed information for each flight
    for i, flight in enumerate(flights):
        markdown += f"#### Option {i+1}: ${flight.get('price', 'N/A')}\n\n"

        # Flight segments
        flight_segments = flight.get('flights', [])
        for j, segment in enumerate(flight_segments):
            departure = segment.get('departure_airport', {})
            arrival = segment.get('arrival_airport', {})

            # Format times
            dep_time = departure.get('time', '').split(' ')[1] if ' ' in departure.get('time', '') else departure.get('time', '')
            arr_time = arrival.get('time', '').split(' ')[1] if ' ' in arrival.get('time', '') else arrival.get('time', '')

            # Duration
            duration_min = segment.get('duration', 0)
            duration_hr = duration_min // 60
            duration_min_remainder = duration_min % 60

            markdown += f"**Segment {j+1}**: {departure.get('id', '')} → {arrival.get('id', '')}\n"
            markdown += f"* {segment.get('airline', 'N/A')} {segment.get('flight_number', '')}\n"
            markdown += f"* Depart: {departure.get('name', 'N/A')} at {dep_time}\n"
            markdown += f"* Arrive: {arrival.get('name', 'N/A')} at {arr_time}\n"
            markdown += f"* Duration: {duration_hr}h {duration_min_remainder}m\n"
            markdown += f"* Aircraft: {segment.get('airplane', 'N/A')}\n"

            if segment.get('overnight'):
                markdown += "* **Overnight flight**\n"

            markdown += "\n"

        # Layovers
        layovers = flight.get('layovers', [])
        if layovers:
            markdown += "**Layovers**:\n"
            for layover in layovers:
                duration_min = layover.get('duration', 0)
                duration_hr = duration_min // 60
                duration_min_remainder = duration_min % 60
                markdown += f"* {layover.get('name', 'N/A')} ({layover.get('id', 'N/A')}): {duration_hr}h {duration_min_remainder}m\n"

            markdown += "\n"

        # Carbon emissions
        carbon = flight.get('carbon_emissions', {})
        if carbon:
            diff = carbon.get('difference_percent', 0)
            comparison = "lower than" if diff < 0 else "higher than"
            markdown += f"**Carbon Emissions**: {carbon.get('this_flight', 0)/1000:.1f} kg ({abs(diff)}% {comparison} average)\n\n"

        markdown += "---\n\n"

    markdown += "*Flight data generated by Gemini AI. Click 'Book' to see actual flights on Google Flights.*\n\n"

    return markdown

def get_destination_recommendations(interests, budget, dates, travelers):
    """
    Get destination recommendations based on user preferences.

    Args:
        interests (list): List of interests/preferences
        budget (str): Budget for the trip
        dates (str): Travel dates
        travelers (str): Number of travelers

    Returns:
        str: Destination recommendations
    """
    interests_str = ", ".join(interests)

    prompt = f"""
    Act as a travel destination expert. Recommend 5 destinations that would be perfect for a traveler with the following preferences:

    - Interests: {interests_str}
    - Budget: {budget}
    - Travel Dates: {dates}
    - Number of Travelers: {travelers}

    For each destination, provide:
    1. Why it's a good match for the interests
    2. Typical costs and how they align with the budget
    3. Weather and conditions during the specified dates
    4. Top 3 attractions or activities related to the interests

    Format your response in Markdown with proper headings (using # for main headings, ## for subheadings),
    bullet points, and emphasis where appropriate. Make it visually structured and easy to read.
    """

    response = model.generate_content(prompt)

    return response.text