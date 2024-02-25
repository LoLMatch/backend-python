from flask import Flask, request, jsonify
import player
import player_recommender
import json
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Summoner Recommender"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Create player object
def create_player(summoner_name):
    with open("static/summoners.json", "r") as f:
        all_summoners = json.load(f)

    summoner_info = all_summoners[summoner_name]
    sex = summoner_info["sex"]
    country = summoner_info["country"]
    languages = summoner_info["languages"]
    level = summoner_info["level"]
    tier = summoner_info["tier"]
    rank = summoner_info["rank"]
    wins = summoner_info["wins"]
    losses = summoner_info["losses"]
    age = summoner_info["age"]
    preferred_champions_and_lines = summoner_info["preferred_champions_and_lines"]
    return player.Player(
        summoner_name,
        sex,
        country,
        languages,
        level,
        tier,
        rank,
        wins,
        losses,
        age,
        preferred_champions_and_lines,
    )


# Get recommendations for a user
@app.route("/recommendations/<string:summoner_name>", methods=["GET"])
def get_recommendations(summoner_name):
    number_of_recommendations = request.args.get(
        "number_of_recommendations", default=10, type=int
    )

    user = create_player(summoner_name)
    user_recommender = player_recommender.PlayerRecommender(user)

    recommendations = []
    for i in range(number_of_recommendations):
        recommendation = user_recommender.recommend()
        if recommendation:
            recommendations.append(recommendation)
        else:
            break

    return jsonify(recommendations), 200


@app.route("/")
def home_page():
    return "<h1>Test</h1>"


@app.route("/recommendation/update/<string:summoner_name>", methods=["POST"])
def update_recommendation_status(summoner_name):
    if request.method == "POST":
        data = request.get_json()
        recommendation = data.get("recommendation")
        status = data.get("status")  # 'accept' or 'reject'

        user = create_player(
            summoner_name
        )  # In a real-world scenario, you'd retrieve the user object from a database or session

        if status == "accept":
            user.accepted_recommendations.append(recommendation)
        elif status == "reject":
            user.rejected_recommendations.append(recommendation)

        # In a real-world scenario, you'd save the user object back to the database or session here

        return (
            jsonify(
                {"message": f"Recommendation {recommendation} has been {status}ed."}
            ),
            200,
        )


if __name__ == "__main__":
    app.run(debug=True)
