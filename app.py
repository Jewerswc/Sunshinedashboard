from flask import Flask, request, jsonify
import requests
import googlemaps
import openai

app = Flask(__name__)

# API keys
GOOGLE_MAPS_API_KEY = 'your_google_maps_api_key_here'
OPENAI_API_KEY = 'your_openai_api_key_here'

# Initialize clients
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
openai.api_key = OPENAI_API_KEY

@app.route('/generate_challenge', methods=['POST'])
def generate_challenge():
    data = request.json
    start_location = data['start_location']
    end_location = data['end_location']
    transport_modes = data.get('transport_modes', ['driving', 'bicycling'])

    # Get travel times for each transport mode
    routes = {}
    for mode in transport_modes:
        directions_result = gmaps.directions(start_location, end_location, mode=mode)
        duration = directions_result[0]['legs'][0]['duration']['text']
        routes[mode] = duration

    # Generate a challenge narrative using ChatGPT
    prompt = f"Create a travel challenge between {transport_modes[0]} and {transport_modes[1]} from {start_location} to {end_location}."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    challenge_description = response.choices[0].text.strip()

    # Create a narrow time margin (this is a basic example; you'd refine this in a real app)
    winner = min(routes, key=routes.get)
    loser = max(routes, key=routes.get)

    # Slightly adjust the winner's time to ensure a close race (example logic)
    routes[winner] = f"{int(routes[winner].split()[0]) + 1} mins"  # Adding 1 minute to make it closer

    return jsonify({
        'challenge_description': challenge_description,
        'routes': routes,
        'predicted_winner': winner
    })

if __name__ == '__main__':
    app.run(debug=True)
