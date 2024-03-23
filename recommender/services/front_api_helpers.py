from ..db.database import execute_query, fetch_one, fetch_all
from datetime import datetime


def get_summoner_id(summoner_name):
    query = """
        SELECT id FROM summoners WHERE name = %s
    """
    try:
        summoner_id = fetch_one(query, (summoner_name,))["id"]
    except TypeError:
        summoner_id = None

    return summoner_id


def get_summoner_matches(summoner_id):
    query = """
        SELECT * FROM matches WHERE summoner1_id = %s OR summoner2_id = %s
    """
    matches = fetch_all(query, (summoner_id, summoner_id))

    return matches


def update_recommendation(summoner_id, recommended_summoner_id, status):

    if status == "accept":
        query = """
            INSERT INTO accepted_recommendations (summoner_id, recommended_summoner_id, recommendation_date) VALUES (%s, %s, %s)
        """
    elif status == "reject":
        query = """
            INSERT INTO rejected_recommendations (summoner_id, recommended_summoner_id, recommendation_date) VALUES (%s, %s, %s)
        """
    else:
        raise ValueError("Invalid status. Status must be 'accept' or 'reject'.")

    execute_query(
        query=query,
        params=(summoner_id, recommended_summoner_id, datetime.today()),
        commit=True,
    )


def check_if_match(summoner_id, recommended_summoner_id):
    match = False

    query = """
        SELECT * FROM accepted_recommendations WHERE summoner_id = %s AND recommended_summoner_id = %s
    """

    is_match = fetch_one(query, (recommended_summoner_id, summoner_id))

    query = """
    INSERT INTO matches (summoner1_id, summoner2_id, match_date) VALUES (%s, %s, %s)
    """

    if is_match:
        match = True
        execute_query(
            query=query,
            params=(summoner_id, recommended_summoner_id, datetime.now()),
            commit=True,
        )

    return match
