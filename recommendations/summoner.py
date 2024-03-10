import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from utils import connect

class Summoner:
    def __init__(
        self,
        name,
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
        favourite_champion,
        favourite_line,
        accepted_recommendations=[],
        rejected_recommendations=[],
    ):
        self.name = name
        self.sex = sex
        self.country = country
        self.languages = languages
        self.level = level
        self.tier = tier
        self.rank = rank
        self.wins = wins
        self.losses = losses
        self.win_rate = self.calculate_win_rate(wins, losses)
        self.age = age
        self.preferred_champions_and_lines = preferred_champions_and_lines
        self.favourite_champion = favourite_champion
        self.favourite_line = favourite_line
        self.accepted_recommendations = accepted_recommendations
        self.rejected_recommendations = rejected_recommendations

    @staticmethod
    def calculate_win_rate(wins, losses):
        return wins / (wins + losses) * 100 if (wins + losses) != 0 else 0

    @classmethod
    def create_from_name(cls, summoner_name):
        query = '''
            SELECT * FROM summoners WHERE name = %s
        '''
        summoner = connect.fetch_one(query, (summoner_name,))
        if summoner:
            languages_query = '''
                SELECT * FROM languages_spoken WHERE summoner_id = %s
            '''
            languages = connect.fetch_all(languages_query, (summoner['id'],))
            languages_list = [language['language'] for language in languages]

            champions_query = '''
                SELECT * FROM preferred_champions_and_lines WHERE summoner_id = %s
            '''
            champions = connect.fetch_all(champions_query, (summoner['id'],))
            champions_list = [{
                "champion_id": champion['champion_id'],
                "champion_name": champion['champion_name'],
                "line": champion['line'],
            } for champion in champions]

            favourite_champion_query = '''SELECT * FROM favourite_champions WHERE summoner_id = %s'''
            champion = connect.fetch_one(favourite_champion_query, (summoner['id'],))
            favourite_champion = {
                "champion_id": champion['champion_id'],
                "champion_name": champion['champion_name'],
                "line": champion['line'],
            }

            accepted_query = '''
                SELECT * FROM accepted_recommendations WHERE summoner_id = %s
            '''
            accepted = connect.fetch_all(accepted_query, (summoner['id'],))

            rejected_query = '''
                SELECT * FROM rejected_recommendations WHERE summoner_id = %s
            '''
            rejected = connect.fetch_all(rejected_query, (summoner['id'],))
            
            return cls(
                summoner['name'],
                summoner['sex'],
                summoner['country'],
                languages_list,
                summoner['level'],
                summoner['tier'],
                summoner['rank'],
                summoner['wins'],
                summoner['losses'],
                summoner['age'],
                champions_list,
                favourite_champion,
                summoner['favourite_line'],
                [rec['recommended_summoner_id'] for rec in accepted],
                [rec['recommended_summoner_id'] for rec in rejected],
            )
        else:
            return None

