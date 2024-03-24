from ..services.front_api_helpers import (
    get_summoner_id,
    get_summoner_matches,
    update_recommendation,
    check_if_match,
)
from flask import Blueprint, jsonify, request
from ..services.recommender import Recommender
from ..services.summoner import Summoner
from ..services.riot_api_functions import RiotAPI

main = Blueprint("main", __name__)


@main.route("/matches/<string:summoner_name>", methods=["GET"])
def get_matches(summoner_name):
    summoner_id = get_summoner_id(summoner_name)

    if not summoner_id:
        return jsonify({"message": "Summoner not found."}), 404

    matches = get_summoner_matches(summoner_id)
    return jsonify(matches), 200


@main.route("/champions/<string:api_key>", methods=["GET"])
def get_champions(api_key):
    result = list()

    riot_api = RiotAPI(api_key=api_key)
    latest_version = riot_api.get_latest_version()[0]

    riot_api_response = riot_api.get_champions(latest_version)

    if "data" not in riot_api_response:
        return jsonify({"message": "Invalid API key."}), 400

    champions = riot_api_response["data"]

    for champion in champions:
        champion_data = champions[champion]
        champion_id = champion_data["key"]
        champion_name = champion_data["name"]
        result.append({"id": champion_id, "name": champion_name})

    return jsonify(result), 200


@main.route("/champion-rotations/<string:api_key>", methods=["GET"])
def get_champion_rotations(api_key):
    riot_api = RiotAPI(api_key=api_key)
    champion_rotations = riot_api.get_champion_rotations()
    return jsonify(champion_rotations), 200


@main.route("/recommendations/<string:summoner_name>", methods=["GET"])
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


@main.route("/")
def home_page():
    return "<h1>Test</h1>"


@main.route("/recommendation/update/<string:summoner_name>", methods=["POST"])
def update_recommendation_status(summoner_name):
    if request.method == "POST":
        data = request.get_json()
        recommended_summoner_name = data.get("recommendation")
        status = data.get("status")

        summoner_id = get_summoner_id(summoner_name)
        recommended_summoner_id = get_summoner_id(recommended_summoner_name)

        if not summoner_id:
            return jsonify({"message": "Summoner not found."}), 404
        if not recommended_summoner_id:
            return jsonify({"message": "Recommended summoner not found."}), 404

        try:
            update_recommendation(summoner_id, recommended_summoner_id, status)
            return (
                jsonify(
                    {
                        "message": f"Recommendation {recommended_summoner_name} has been {status}ed.",
                        "match": check_if_match(summoner_id, recommended_summoner_id),
                    }
                ),
                200,
            )
        except ValueError as e:
            return jsonify({"message": str(e)}), 400

