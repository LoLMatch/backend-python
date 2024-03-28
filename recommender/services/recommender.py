import random
from ..db.database import fetch_all
from .recommender_helpers import (
    load_summoner_descriptions,
    load_summoner_languages,
    load_summoner_preferred_champions_and_lines,
    load_favourite_champion,
)


class Recommender:
    def __init__(self, summoner):
        self.summoner = summoner
        self.original_thresholds = {}
        self.thresholds = {}
        self.recommendations = {}
        self.load_recommendations()

    def load_summoners_matching_criteria(self):
        th = self.thresholds
        query = """
            SELECT * FROM summoners
            JOIN languages_spoken ON summoners.id = languages_spoken.summoner_id
            WHERE level BETWEEN %s AND %s
            AND tier = %s
            AND (wins + losses) BETWEEN %s AND %s
            AND age BETWEEN %s AND %s
            AND languages_spoken.language IN %s
            AND summoners.name <> %s
        """
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
        while len(self.recommendations) < 20:
            self.set_thresholds(relaxation)
            summoners = self.load_summoners_matching_criteria()
            for summoner in summoners:
                summoner_id = summoner["id"]
                summoner_name = summoner["name"]
                if (
                    summoner_id not in self.summoner.accepted_recommendations
                    and summoner_id not in self.summoner.rejected_recommendations
                ):
                    long_description, short_description = load_summoner_descriptions(
                        summoner_id
                    )
                    languages_spoken = load_summoner_languages(summoner_id)
                    preferred_champions_and_lines = (
                        load_summoner_preferred_champions_and_lines(summoner_id)
                    )
                    favourite_champion = load_favourite_champion(summoner_id)
                    summoner_info = {
                        "name": summoner_name,
                        "short_description": short_description,
                        "long_description": long_description,
                        "languages": languages_spoken,
                        "level": summoner["level"],
                        "tier": summoner["tier"],
                        "wins": summoner["wins"],
                        "losses": summoner["losses"],
                        "age": summoner["age"],
                        "preferred_champion_ids_and_lines": preferred_champions_and_lines,
                        "favourite_champion_id": favourite_champion,
                        "favourite_line": summoner["favourite_line"],
                        "country": summoner["country"],
                        "win_rate": (
                            summoner["wins"] / (summoner["wins"] + summoner["losses"])
                            if (summoner["wins"] + summoner["losses"]) != 0
                            else 0
                        ),
                    }

                    if summoner_name not in self.recommendations:
                        self.recommendations[summoner_name] = summoner_info

            relaxation += 0.05  # Increment to relax the criteria

    def get_recommendations(self, number_of_recommendations):
        return random.sample(
            list(self.recommendations.values()), number_of_recommendations
        )
