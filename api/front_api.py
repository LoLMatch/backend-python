import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from flask import Flask, request, jsonify
from utils.connect import execute_query, fetch_one
from recommendations.summoner import Summoner
from recommendations.recommender import Recommender
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Summoner Recommender"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

insert_into_matches_table_query = '''
    INSERT INTO matches (summoner1_id, summoner2_id, match_date) VALUES (%s, %s, %s)
    '''

# Get matches
@app.route("/matches/<string:summoner_name>", methods=["GET"])
def get_matches(summoner_name):
    query = '''
        SELECT id FROM summoners WHERE name = %s
    '''
    summoner_id = fetch_one(query, (summoner_name,))['id']

    if not summoner_id:
        return jsonify({"message": "Summoner not found."}), 404

    query = '''
        SELECT * FROM matches WHERE summoner1_id = %s OR summoner2_id = %s
    '''
    matches = fetch_one(query, (summoner_id, summoner_id))
    return jsonify(matches), 200

# Get recommendations for a user
@app.route("/recommendations/<string:summoner_name>", methods=["GET"])
def get_recommendations(summoner_name):
    number_of_recommendations = request.args.get(
        "number_of_recommendations", default=10, type=int
    )

    user = Summoner.create_from_name(summoner_name)
    if not user:
        return jsonify({"message": "User not found."}), 404

    user_recommender = Recommender(user)
    recommendations = user_recommender.get_recommendations(number_of_recommendations)

    return jsonify(recommendations), 200


@app.route("/")
def home_page():
    return "<h1>Test</h1>"


@app.route("/recommendation/update/<string:summoner_name>", methods=["POST"])
def update_recommendation_status(summoner_name):
    if request.method == "POST":
        data = request.get_json()
        recommended_summoner_name = data.get("recommendation")
        status = data.get("status")  # 'accept' or 'reject'

        try:
            match = update_recommendation(summoner_name, recommended_summoner_name, status)
            return jsonify(
                {
                    "message": f"Recommendation {recommended_summoner_name} has been {status}ed.",
                    "match": match,
                }
            ), 200
        except ValueError as e:
            return jsonify({"message": str(e)}), 400

def update_recommendation(summoner_name, recommended_summoner_name, status):
    match = False

    query = '''
        SELECT id FROM summoners WHERE name = %s
    '''
    try:
        summoner_id = fetch_one(query, (summoner_name,))['id']
        recommended_summoner_id = fetch_one(query, (recommended_summoner_name,))['id']
    except TypeError:
        raise ValueError("Invalid summoner name.")

    if status == "accept":
        query = '''
            INSERT INTO accepted_recommendations (summoner_id, recommended_summoner_id, recommendation_date) VALUES (%s, %s, %s)
        '''
    elif status == "reject":
        query = '''
            INSERT INTO rejected_recommendations (summoner_id, recommended_summoner_id, recommendation_date) VALUES (%s, %s, %s)
        '''
    else:
        raise ValueError("Invalid status. Status must be 'accept' or 'reject'.")

    execute_query(query, (summoner_id, recommended_summoner_id, datetime.today()), commit=True)

    query = '''
        SELECT * FROM accepted_recommendations WHERE summoner_id = %s AND recommended_summoner_id = %s
    '''

    is_match = fetch_one(query, (recommended_summoner_id, summoner_id))
    if is_match:
        match = True
        execute_query(insert_into_matches_table_query, (summoner_id, recommended_summoner_id, datetime.today()), commit=True)

    return match

if __name__ == "__main__":
    app.run(debug=True)
