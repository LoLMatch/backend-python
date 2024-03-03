import random
from connect import fetch_all, fetch_one

class Recommender:
    def __init__(self, summoner):
        self.summoner = summoner
        self.original_thresholds = {}
        self.thresholds = {}
        self.recommendations = {}
        self.load_recommendations()

    def load_summoners_matching_criteria(self):
        th = self.thresholds
        query = '''
            SELECT * FROM summoners
            JOIN languages_spoken ON summoners.id = languages_spoken.summoner_id
            WHERE level BETWEEN %s AND %s
            AND tier = %s
            AND (wins + losses) BETWEEN %s AND %s
            AND age BETWEEN %s AND %s
            AND languages_spoken.language IN %s
            AND summoners.name <> %s
        '''
        params = (
            th["min_level"],
            th["max_level"],
            self.summoner.tier,
            th["min_games_played"],
            th["max_games_played"],
            th["min_age"],
            th["max_age"],
            tuple(self.summoner.languages) if self.summoner.languages else (),
            self.summoner.name,
        )
        return fetch_all(query, params)

    def load_summoner_descriptions(self, summoner_id):
        query = '''
            SELECT * FROM summoners_descriptions WHERE summoner_id = %s
        '''
        descriptions = fetch_one(query, (summoner_id,))
        if descriptions:
            return descriptions['description'], descriptions['short_description']
        return None, None


    def load_summoner_languages(self, summoner_id):
        query = '''
            SELECT * FROM languages_spoken WHERE summoner_id = %s
        '''
        languages = fetch_all(query, (summoner_id,))
        return [language['language'] for language in languages]

    def load_summoner_preferred_champions_and_lines(self, summoner_id):
        query = '''
            SELECT * FROM preferred_champions_and_lines WHERE summoner_id = %s
        '''
        champions_and_lines = fetch_all(query, (summoner_id,))
        return [
            {
                "champion_id": champion['champion_id'],
                "champion_name": champion['champion_name'],
                "line": champion['line'],
            }
            for champion in champions_and_lines
        ]

    def set_thresholds(self, relaxation=0.0):
        # Adjust thresholds based on the relaxation parameter
        summoner = self.summoner
        self.thresholds = {
            "min_level": round((0.9 - relaxation) * summoner.level),
            "max_level": round((1.1 + relaxation) * summoner.level),
            "tier": summoner.tier,  # Assuming tier is a strict match, not relaxed
            "min_games_played": round(
                (0.9 - relaxation) * (summoner.wins + summoner.losses)
            ),
            "max_games_played": (
                round((1.1 + relaxation) * (summoner.wins + summoner.losses))
                if summoner.wins + summoner.losses != 0
                else 10
            ),
            "min_age": round((0.8 - relaxation) * summoner.age),
            "max_age": round((1.2 + relaxation) * summoner.age),
        }

    def matches_criteria(self, summoner_info):
        th = self.thresholds
        level, games_played, age = (
            summoner_info["level"],
            summoner_info["wins"] + summoner_info["losses"],
            summoner_info["age"],
        )
        return (
            set(self.summoner.languages) & set(summoner_info["languages"])
            and th["min_level"] <= level <= th["max_level"]
            and self.summoner.tier == summoner_info["tier"]
            and th["min_games_played"] <= games_played <= th["max_games_played"]
            and th["min_age"] <= age <= th["max_age"]
        )

    def load_recommendations(self):
        relaxation = 0.0
        while (
            len(self.recommendations) < 10
        ):  # and relaxation <= 0.2:  # Adjust the threshold up to a certain point
            self.set_thresholds(relaxation)
            summoners = self.load_summoners_matching_criteria()
            for summoner in summoners:
                summoner_id = summoner['id']
                summoner_name = summoner['name']
                if (
                    summoner_name not in self.summoner.accepted_recommendations
                    and summoner_name not in self.summoner.rejected_recommendations
                ):
                    long_description, short_description = self.load_summoner_descriptions(
                        summoner_id
                    )
                    languages_spoken = self.load_summoner_languages(summoner_id)
                    preferred_champions_and_lines = self.load_summoner_preferred_champions_and_lines(
                        summoner_id
                    )
                    summoner_info = {
                        "name": summoner_name,
                        "short_description": short_description,
                        "long_description": long_description,
                        "languages": languages_spoken,
                        "level": summoner['level'],
                        "tier": summoner['tier'],
                        "wins": summoner['wins'],
                        "losses": summoner['losses'],
                        "age": summoner['age'],
                        "preferred_champions_and_lines": preferred_champions_and_lines,
                        "country": summoner['country'],
                        "win_rate": summoner['wins'] / (summoner['wins'] + summoner['losses']) if (summoner['wins'] + summoner['losses']) != 0 else 0,
                    }

                    if summoner_name not in self.recommendations:
                        self.recommendations[summoner_name] = summoner_info

            relaxation += 0.05  # Increment to relax the criteria

    def get_recommendations(self, number_of_recommendations):
        recommendations = []
        for _ in range(number_of_recommendations):
            recommended_summoner_info = self.recommend()
            if recommended_summoner_info:
                recommendations.append(recommended_summoner_info)
            else:
                break
        return recommendations

    def recommend(self):
        if self.recommendations:
            recommended_summoner_name = random.choice(list(self.recommendations.keys()))
            recommended_summoner_info = self.recommendations.pop(
                recommended_summoner_name
            )
            return recommended_summoner_info
        else:
            return None
