import random
import json

class PlayerRecommender:
    def __init__(self, summoner):
        self.summoner = summoner
        self.original_thresholds = {}
        self.thresholds = {}
        self.recommendations = {}
        self.load_recommendations()

    def set_thresholds(self, relaxation=0.0):
        # Adjust thresholds based on the relaxation parameter
        summoner = self.summoner
        self.thresholds = {
            'min_level': round((0.9 - relaxation) * summoner.level),
            'max_level': round((1.1 + relaxation) * summoner.level),
            'tier': summoner.tier,  # Assuming tier is a strict match, not relaxed
            'min_games_played': round((0.9 - relaxation) * (summoner.wins + summoner.losses)),
            'max_games_played': round((1.1 + relaxation) * (summoner.wins + summoner.losses)) if summoner.wins + summoner.losses != 0 else 10,
            'min_age': round((0.8 - relaxation) * summoner.age),
            'max_age': round((1.2 + relaxation) * summoner.age),
        }

    def matches_criteria(self, summoner_info):
        th = self.thresholds
        level, games_played, age = summoner_info['level'], summoner_info['wins'] + summoner_info['losses'], summoner_info['age']
        return (
            set(self.summoner.languages) & set(summoner_info['languages']) and
            th['min_level'] <= level <= th['max_level'] and
            self.summoner.tier == summoner_info['tier'] and
            th['min_games_played'] <= games_played <= th['max_games_played'] and
            set(self.summoner.roles) & set(summoner_info['preferred_roles']) and
            set(self.summoner.game_modes) & set(summoner_info['preferred_gamemode']) and
            th['min_age'] <= age <= th['max_age']
        )

    def load_recommendations(self):
        relaxation = 0.0
        while len(self.recommendations) < 10: #and relaxation <= 0.2:  # Adjust the threshold up to a certain point
            self.set_thresholds(relaxation)
            try:
                with open('summoners.json', 'r') as f:
                    all_summoners = json.load(f)
                self.recommendations = {name: info for name, info in all_summoners.items() if name not in self.summoner.already_recommended and self.matches_criteria(info) and name != self.summoner.name}
            except FileNotFoundError:
                print("summoners.json file not found.")
            relaxation += 0.05  # Increment to relax the criteria

    def recommend(self):
        if self.recommendations:
            recommended_summoner_name = random.choice(list(self.recommendations.keys()))
            recommended_summoner_info = self.recommendations.pop(recommended_summoner_name)
            self.summoner.already_recommended[recommended_summoner_name] = recommended_summoner_info
            return recommended_summoner_info
        else:
            return None
