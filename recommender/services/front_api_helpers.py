from ..db.database import get_db_connection, execute_query, fetch_one, fetch_all
from ..db.init_db import (
    insert_into_summoners_table_query,
    insert_into_summoners_preferred_champions_and_lines_table_query,
    insert_into_summoners_languages_table_query,
    insert_into_summoners_descriptions_table_query,
    insert_into_favourite_champions_table_query,
)
from .riot_api_functions import RiotAPI
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


def summoner_entries(riot_api, summoner_puuid):
    summoner_info = riot_api.get_summoner_info_by_puuid(summoner_puuid)
    summoner_entries = riot_api.get_summoner_entries(summoner_puuid)

    return (
        summoner_info["summonerLevel"],
        summoner_entries["tier"],
        summoner_entries["rank"],
        summoner_entries["wins"],
        summoner_entries["losses"],
    )


def champion_id_to_name(champion_id, api_key):
    riot_api = RiotAPI(api_key=api_key)

    return {
        "champion_id": champion_id,
        "champion_name": riot_api.map_champion_id_to_name(champion_id),
    }


def save_summoner_profile(
    api_key,
    summoner_name,
    summoner_sex,
    summoner_country,
    summoner_languages,
    summoner_age,
    preferred_champions_ids_and_lines,
    favourite_champion_id,
    favourite_line,
    description,
    short_description,
    icon_id,
):
    connection = get_db_connection()
    riot_api = RiotAPI(api_key=api_key)
    summoner_puuid = riot_api.get_summoner_info_by_name(summoner_name)["puuid"]
    languages = [language for language in summoner_languages]

    summoner_level, summoner_tier, summoner_rank, summoner_wins, summoner_losses = (
        summoner_entries(riot_api, summoner_puuid)
    )

    execute_query(
        query=insert_into_summoners_table_query,
        conn=connection,
        params=(
            summoner_name,
            summoner_puuid,
            summoner_sex,
            summoner_country,
            summoner_level,
            summoner_tier,
            summoner_rank,
            summoner_wins,
            summoner_losses,
            summoner_age,
            favourite_line,
            icon_id,
        ),
        commit=True,
    )

    summoner_id = get_summoner_id(summoner_name)
    execute_query(
        query=insert_into_summoners_descriptions_table_query,
        conn=connection,
        params=(summoner_id, description, short_description),
        commit=True,
    )

    for language in languages:
        execute_query(
            query=insert_into_summoners_languages_table_query,
            conn=connection,
            params=(summoner_id, language),
            commit=True,
        )

    for champion in preferred_champions_ids_and_lines:
        execute_query(
            query=insert_into_summoners_preferred_champions_and_lines_table_query,
            conn=connection,
            params=(summoner_id, champion["champion_id"], champion["line"]),
            commit=True,
        )

    execute_query(
        query=insert_into_favourite_champions_table_query,
        conn=connection,
        params=(summoner_id, favourite_champion_id, favourite_line),
        commit=True,
    )
