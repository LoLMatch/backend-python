from ..db.database import fetch_all, fetch_one


def load_summoner_descriptions(summoner_id):
    query = """
        SELECT * FROM summoners_descriptions WHERE summoner_id = %s
    """
    descriptions = fetch_one(query, (summoner_id,))
    if descriptions:
        return descriptions["description"], descriptions["short_description"]
    return None, None


def load_summoner_languages(summoner_id):
    query = """
        SELECT * FROM languages_spoken WHERE summoner_id = %s
    """
    languages = fetch_all(query, (summoner_id,))
    return [language["language"] for language in languages]


def load_summoner_preferred_champions_and_lines(summoner_id):
    query = """
        SELECT * FROM preferred_champions_and_lines WHERE summoner_id = %s
    """
    champions_and_lines = fetch_all(query, (summoner_id,))
    return [
        {
            "champion_id": champion["champion_id"],
            "line": champion["line"],
        }
        for champion in champions_and_lines
    ]


def load_favourite_champion(summoner_id):
    query = """
        SELECT * FROM favourite_champions WHERE summoner_id = %s
    """
    champion = fetch_one(query, (summoner_id,))
    return champion["champion_id"] if champion else None
