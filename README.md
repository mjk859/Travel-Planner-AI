# Travel Planner AI

A travel planning assistant powered by Google's Gemini 2.0 Flash API.

## Features

- Generate personalized travel itineraries
- Provide destination recommendations based on user interests
- Suggest activities within budget constraints
- Offer accommodation and transportation options
- Create day-by-day schedules

## User Inputs

The system accepts the following inputs:

- Source location
- Destination
- Travel dates
- Budget
- Number of travelers
- Interests/preferences

## Tech Stack

- **Backend**: Python with Flask
- **AI**: Google Gemini 2.0 Flash API
- **Frontend**: HTML, CSS, JavaScript

## Setup Instructions

1. Clone this repository
2. Install backend dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```
3. Set up your Gemini API key:
   - Create a `.env` file in the backend directory
   - Add your API key: `GEMINI_API_KEY=your_api_key_here`

4. Run the application:
   ```
   python app.py
   ```
5. Open your browser and navigate to `http://localhost:5000`

## Project Structure

- `/backend` - Python Flask server and Gemini API integration
- `/frontend` - HTML, CSS, and JavaScript for the user interface

## Note

This application runs locally and is not configured for deployment.