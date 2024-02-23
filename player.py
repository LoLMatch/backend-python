class Player:
    def __init__(self, name, sex, country, languages, level, tier, rank, wins, losses, age, preferred_champions_and_lines):
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
        self.already_recommended = {}  # Assuming we want to keep track of recommendations as in PlayerRecommender

    @staticmethod
    def calculate_win_rate(wins, losses):
        return wins / (wins + losses) * 100 if (wins + losses) != 0 else 0

