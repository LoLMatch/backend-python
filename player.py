class Player:
    def __init__(self, name, sex, country, languages, level, tier, rank, wins, losses, roles, game_modes, age):
        self.name = name
        self.sex = sex
        self.country = country
        self.languages = languages
        self.level = level
        self.tier = tier
        self.rank = rank
        self.wins = wins
        self.losses = losses
        self.win_loss_percentage = self.calculate_win_loss_percentage(wins, losses)
        self.roles = roles
        self.game_modes = game_modes
        self.age = age
        self.already_recommended = {}  # Assuming we want to keep track of recommendations as in PlayerRecommender

    @staticmethod
    def calculate_win_loss_percentage(wins, losses):
        return wins / (wins + losses) * 100 if (wins + losses) != 0 else 0

# rangi idą w dół (silver I > silver IV)
# zrobić forcowanie że muszą na siebie trafić
# napisać maila do riot
