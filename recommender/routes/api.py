from ..services.front_api_helpers import (
    get_summoner_id,
    get_summoner_matches,
    update_recommendation,
    check_if_match,
    save_summoner_profile,
    champion_id_to_name,
)
from flask import Blueprint, jsonify, request
from ..services.recommender import Recommender
from ..services.summoner import Summoner
from ..services.riot_api_functions import RiotAPI
from ..db.database import get_db_connection, execute_query

main = Blueprint("main", __name__)

API_KEY = "RGAPI-8b53ca8c-8b3c-4470-9b82-94517072c7bf"


@main.route("/matches/<string:summoner_name>", methods=["GET"])
def get_matches(summoner_name):
    summoner_id = get_summoner_id(summoner_name)

    if not summoner_id:
        return jsonify({"message": "Summoner not found"}), 404

    matches = get_summoner_matches(summoner_id)
    return jsonify(matches), 200


@main.route("/champions", methods=["GET"])
def get_champions():
    result = list()

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM champions")
        for champion in cur.fetchall():
            result.append(
                {
                    "champion_id": champion[0],
                    "champion_name": champion[1],
                }
            )

    return jsonify(result), 200


@main.route("/champion-rotations", methods=["GET"])
def get_champion_rotations():
    riot_api = RiotAPI(api_key=API_KEY)
    champion_rotations = riot_api.get_champion_rotations()

    if not champion_rotations:
        return jsonify({"message": "Champion rotations not found"}), 404

    free_champions = [
        champion_id_to_name(free_champion_id, API_KEY)
        for free_champion_id in champion_rotations["freeChampionIds"]
    ]
    free_champions_for_new_players = [
        champion_id_to_name(free_champion_id_for_new_players, API_KEY)
        for free_champion_id_for_new_players in champion_rotations[
            "freeChampionIdsForNewPlayers"
        ]
    ]
    max_new_player_level = champion_rotations["maxNewPlayerLevel"]

    result = {
        "freeChampions": free_champions,
        "freeChampionsForNewPlayers": free_champions_for_new_players,
        "maxNewPlayerLevel": max_new_player_level,
    }

    return jsonify(result), 200


@main.route("/recommendations/<string:summoner_name>", methods=["GET"])
def get_recommendations(summoner_name):
    number_of_recommendations = request.args.get(
        "number_of_recommendations", default=10, type=int
    )

    user = Summoner.create_from_name(summoner_name)
    if not user:
        return jsonify({"message": "User not found"}), 404

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
            return jsonify({"message": "Summoner not found."}), 404

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


@main.route("/profile", methods=["POST"])
def profile():
    if request.method == "POST":
        data = request.get_json()

        try:
            name = data.get("summoner_name")
            sex = data.get("sex")
            country = data.get("country")
            languages = data.get("languages")
            age = data.get("age")
            preferred_champions_ids_and_lines = data.get(
                "preferred_champion_ids_and_lines"
            )
            favourite_champion_id = data.get("favourite_champion_id")
            favourite_line = data.get("favourite_line")
            long_description = data.get("long_description")
            short_description = data.get("short_description")
        except KeyError:
            return jsonify({"message": "Invalid request"}), 400

        profile_exists = get_summoner_id(name)

        if profile_exists:
            return jsonify({"message": "Profile already exists"}), 409

        save_summoner_profile(
            API_KEY,
            name,
            sex,
            country,
            languages,
            age,
            preferred_champions_ids_and_lines,
            favourite_champion_id,
            favourite_line,
            long_description,
            short_description,
        )

        return jsonify({"message": "Profile created successfully"}), 200

    return jsonify({"message": "Invalid request"}), 400
