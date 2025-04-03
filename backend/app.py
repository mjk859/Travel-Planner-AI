from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from gemini_api import generate_travel_plan, get_destination_recommendations, get_airport_code

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    """Serve the frontend application"""
    return app.send_static_file('index.html')

@app.route('/api/generate-plan', methods=['POST'])
def create_travel_plan():
    """
    Generate a travel plan based on user inputs.
    
    Expected JSON payload:
    {
        "source": "New York",
        "destination": "Paris",
        "dates": "June 10-20, 2024",
        "budget": "$3000",
        "travelers": "2",
        "interests": ["art", "history", "food"]
    }
    """
    try:
        data = request.json
        
        # Extract data from request
        source = data.get('source', '')
        destination = data.get('destination', '')
        dates = data.get('dates', '')
        budget = data.get('budget', '')
        travelers = data.get('travelers', '')
        interests = data.get('interests', [])
        include_flights = data.get('include_flights', False)
        
        # Validate required fields
        if not all([source, destination, dates, budget, travelers]) or not interests:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Generate travel plan
        result = generate_travel_plan(
            source, destination, dates, budget, travelers, interests, include_flights
        )

        return jsonify({
            'success': True,
            'travel_plan': result['travel_plan'],
            'source_code': result['source_code'],
            'destination_code': result['destination_code'],
            'flight_details': result.get('flight_details')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend-destinations', methods=['POST'])
def recommend_destinations():
    """
    Get destination recommendations based on user preferences.
    
    Expected JSON payload:
    {
        "interests": ["beach", "hiking", "food"],
        "budget": "$2000",
        "dates": "August 5-15, 2024",
        "travelers": "2"
    }
    """
    try:
        data = request.json
        
        # Extract data from request
        interests = data.get('interests', [])
        budget = data.get('budget', '')
        dates = data.get('dates', '')
        travelers = data.get('travelers', '')
        
        # Validate required fields
        if not all([budget, dates, travelers]) or not interests:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Get recommendations
        recommendations = get_destination_recommendations(
            interests, budget, dates, travelers
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-airport-code', methods=['POST'])
def airport_code():
    """
    Get the airport code for a given location.

    Expected JSON payload:
    {
        "location": "New York"
    }
    """
    try:
        data = request.json
        location = data.get('location', '')

        if not location:
            return jsonify({
                'success': False,
                'error': 'Missing location'
            }), 400

        airport_code = get_airport_code(location)

        if airport_code:
            return jsonify({
                'success': True,
                'location': location,
                'airport_code': airport_code
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not determine airport code'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)