from flask import Flask, request, jsonify
import player
import player_recommender
import json

app = Flask(__name__)

# Create player object
def create_player(summoner_name):
    with open('summoners.json', 'r') as f:
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
    roles = summoner_info["preferred_roles"]
    game_modes = summoner_info["preferred_gamemode"]
    age = summoner_info["age"]
    favorite_champions_and_lines = None #summoner_info["favorite_champions_and_lines"]
    return player.Player(summoner_name, sex, country, languages, level, tier, rank, wins, losses, roles, game_modes, age, favorite_champions_and_lines)

# Get recommendations for a user
@app.route('/recommendations/<string:summoner_name>', methods=['GET'])
def get_recommendations(summoner_name):
    number_of_recommendations = request.args.get('number_of_recommendations', default=1, type=int)

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

if __name__ == '__main__':
    app.run(debug=True)
