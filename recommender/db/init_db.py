from ..db.database import get_db_connection, execute_query
from ..services.front_api_helpers import get_summoner_id
from ..services import riot_api_functions
import os
import random

API_KEY = "RGAPI-eea7cd80-2a38-4a4d-b0a5-f73c65e35194"

create_summoners_table_query = """
    CREATE TABLE IF NOT EXISTS summoners (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        puuid VARCHAR(255) NOT NULL,
        sex VARCHAR(1) NOT NULL,
        country VARCHAR(255) NOT NULL,
        level INT NOT NULL,
        tier VARCHAR(255) NOT NULL, 
        rank VARCHAR(255) NOT NULL,
        wins INT NOT NULL,
        losses INT NOT NULL,
        age INT NOT NULL,
        favourite_line VARCHAR(255)
        )
    """

create_summoners_descriptions_table_query = """
    CREATE TABLE IF NOT EXISTS summoners_descriptions (
        id SERIAL PRIMARY KEY,
        summoner_id INT NOT NULL,
        description TEXT NOT NULL,
        short_description TEXT NOT NULL,
        FOREIGN KEY (summoner_id) REFERENCES summoners(id)
    )
    """

create_summoners_languages_table_query = """
    CREATE TABLE IF NOT EXISTS languages_spoken (
        summoner_id INT NOT NULL,
        language VARCHAR(255) NOT NULL,
        FOREIGN KEY (summoner_id) REFERENCES summoners(id)
    )
    """

create_summoners_preferred_champions_and_lines_table_query = """
    CREATE TABLE IF NOT EXISTS preferred_champions_and_lines (
        summoner_id INT NOT NULL,
        champion_id INT NOT NULL,
        champion_name VARCHAR(255) NOT NULL,
        line VARCHAR(255) NOT NULL,
        FOREIGN KEY (summoner_id) REFERENCES summoners(id)
    )
    """

create_favourite_champions_table_query = """
    CREATE TABLE IF NOT EXISTS favourite_champions (
        summoner_id INT NOT NULL,
        champion_id INT NOT NULL,
        champion_name VARCHAR(255) NOT NULL,
        line VARCHAR(255) NOT NULL,
        FOREIGN KEY (summoner_id) REFERENCES summoners(id)
    )
    """

create_summoners_accepted_recommendations_table_query = """
    CREATE TABLE IF NOT EXISTS accepted_recommendations (
        id SERIAL PRIMARY KEY,
        summoner_id INT NOT NULL,
        recommended_summoner_id INT NOT NULL,
        recommendation_date DATE NOT NULL,
        FOREIGN KEY (summoner_id) REFERENCES summoners(id),
        FOREIGN KEY (recommended_summoner_id) REFERENCES summoners(id)
    )
    """

create_summoners_rejected_recommendations_table_query = """
    CREATE TABLE IF NOT EXISTS rejected_recommendations (
        id SERIAL PRIMARY KEY,
        summoner_id INT NOT NULL,
        recommended_summoner_id INT NOT NULL,
        recommendation_date DATE NOT NULL,
        FOREIGN KEY (summoner_id) REFERENCES summoners(id),
        FOREIGN KEY (recommended_summoner_id) REFERENCES summoners(id)
    )
    """

create_matches_table_query = """
    CREATE TABLE IF NOT EXISTS matches (
        id SERIAL PRIMARY KEY,
        summoner1_id INT NOT NULL,
        summoner2_id INT NOT NULL,
        match_date DATE NOT NULL,
        FOREIGN KEY (summoner1_id) REFERENCES summoners(id),
        FOREIGN KEY (summoner2_id) REFERENCES summoners(id)
    )
    """

insert_into_summoners_table_query = """
    INSERT INTO summoners (id, name, puuid, sex, country, level, tier, rank, wins, losses, age, favourite_line) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

insert_into_summoners_descriptions_table_query = """
    INSERT INTO summoners_descriptions (summoner_id, description, short_description) VALUES (%s, %s, %s)
    """

insert_into_summoners_languages_table_query = """
    INSERT INTO languages_spoken (summoner_id, language) VALUES (%s, %s)
    """

insert_into_summoners_preferred_champions_and_lines_table_query = """
    INSERT INTO preferred_champions_and_lines (summoner_id, champion_id, champion_name, line) VALUES (%s, %s, %s, %s)
    """

insert_into_favourite_champions_table_query = """
    INSERT INTO favourite_champions (summoner_id, champion_id, champion_name, line) VALUES (%s, %s, %s, %s)
    """


def drop_tables(conn):
    commands = [
        """DROP TABLE IF EXISTS matches""",
        """DROP TABLE IF EXISTS rejected_recommendations""",
        """DROP TABLE IF EXISTS accepted_recommendations""",
        """DROP TABLE IF EXISTS recommendations""",
        """DROP TABLE IF EXISTS favourite_champions""",
        """DROP TABLE IF EXISTS preferred_champions_and_lines""",
        """DROP TABLE IF EXISTS languages_spoken""",
        """DROP TABLE IF EXISTS summoners_descriptions""",
        """DROP TABLE IF EXISTS summoners""",
    ]
    for command in commands:
        execute_query(command, conn, commit=True)


def create_tables(conn):
    commands = [
        create_summoners_table_query,
        create_summoners_descriptions_table_query,
        create_summoners_languages_table_query,
        create_summoners_preferred_champions_and_lines_table_query,
        create_favourite_champions_table_query,
        create_summoners_accepted_recommendations_table_query,
        create_summoners_rejected_recommendations_table_query,
        create_matches_table_query,
    ]
    for command in commands:
        execute_query(command, conn, commit=True)


def prepare_summoners_set():
    summoners = set()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    summoners_file_path = os.path.join(current_dir, "..", "static", "summoners.txt")

    with open(summoners_file_path, "r") as f:
        for line in f:
            summoner_name = line.split()[0]
            summoner_puuid = line.split()[1]
            summoner = (summoner_name, summoner_puuid)
            summoners.add(summoner)

    return summoners


def prepare_champions_list(champions_json):
    champions = list()
    for champion in champions_json["data"].values():
        champion_id = int(champion["key"])
        champion_name = champion["name"]
        champions.append((champion_id, champion_name))

    return champions


def generate_summoner_details(summoner, champions_json):
    description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque enim sem, cursus at neque rutrum, viverra feugiat orci. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nam vitae magna vehicula, faucibus eros id, egestas mauris. Aenean mollis ac purus vitae mattis. Aenean eget porttitor turpis. Nam fermentum justo non quam tempus, nec interdum quam semper. Sed at faucibus ligula, facilisis congue libero. Suspendisse hendrerit varius augue, ut rutrum nulla condimentum nec. Nam nulla urna, placerat imperdiet vulputate ac, ullamcorper in magna. Duis vitae augue tincidunt, ultrices lorem eget, suscipit lorem. Sed quam nulla, fermentum sit amet ullamcorper id, dictum et sapien. Sed mollis nulla at nisl tincidunt lobortis. Maecenas lectus est, commodo a scelerisque a, semper in libero. Fusce vel accumsan neque."
    short_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    sexes = ["M", "W"]
    countries = [
        "Poland",
        "Spain",
        "Germany",
        "Netherlands",
        "France",
        "Norway",
        "Sweden",
        "Finland",
        "Slovakia",
        "Ukraine",
        "Russia",
        "Latvia",
        "Hungary",
        "Croatia",
        "UK",
        "Italy",
    ]
    languages = [
        "polish",
        "spanish",
        "german",
        "dutch",
        "french",
        "norwegian",
        "swedish",
        "finnish",
        "slovakian",
        "ukrainian",
        "russian",
        "latvian",
        "hungarian",
        "croatian",
        "english",
        "italian",
    ]
    roles = ["Top Lane", "Jungle", "Mid Lane", "Bot Lane", "Support"]
    tiers = [
        "Iron",
        "Bronze",
        "Silver",
        "Gold",
        "Platinum",
        "Diamond",
        "Master",
        "Grandmaster",
        "Challenger",
    ]
    ranks = ["I", "II", "III", "IV"]
    champions = prepare_champions_list(champions_json)

    summoner_name = summoner[0]
    summoner_puuid = summoner[1]
    summoner_sex = random.choice(sexes)
    summoner_country = random.choice(countries)
    summoner_level = random.randint(1, 30)
    summoner_tier = random.choice(tiers)
    summoner_rank = random.choice(ranks)
    summoner_wins = random.randint(0, 1000)
    summoner_losses = random.randint(0, 1000)
    summoner_age = random.randint(18, 35)
    summoner_favourite_line = random.choice(roles)
    summoner_languages = random.sample(languages, random.randint(1, 5))
    summoner_preferred_champions = random.sample(champions, 3)
    summoner_preferred_lines = random.sample(roles, 3)

    return [
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
        summoner_favourite_line,
        description,
        short_description,
        summoner_languages,
        summoner_preferred_champions,
        summoner_preferred_lines,
    ]


def init_db():
    print("Initializing database...")
    conn = get_db_connection()

    drop_tables(conn)
    create_tables(conn)

    summoners = prepare_summoners_set()

    riot_api = riot_api_functions.RiotAPI(API_KEY)
    latest_version = riot_api.get_latest_version()[0]
    champions_json = riot_api.get_champions(latest_version)

    for summoner_id, summoner in enumerate(summoners):
        summoner_details = generate_summoner_details(summoner, champions_json)
        execute_query(
            insert_into_summoners_table_query,
            conn,
            (
                summoner_id,
                summoner_details[0],
                summoner_details[1],
                summoner_details[2],
                summoner_details[3],
                summoner_details[4],
                summoner_details[5],
                summoner_details[6],
                summoner_details[7],
                summoner_details[8],
                summoner_details[9],
                summoner_details[10],
            ),
        )
        execute_query(
            insert_into_summoners_descriptions_table_query,
            conn,
            (summoner_id, summoner_details[-5], summoner_details[-4]),
        )
        for language in summoner_details[-3]:
            execute_query(
                insert_into_summoners_languages_table_query,
                conn,
                (summoner_id, language),
            )
        for champion in summoner_details[-2]:
            execute_query(
                insert_into_summoners_preferred_champions_and_lines_table_query,
                conn,
                (
                    summoner_id,
                    champion[0],
                    champion[1],
                    random.choice(summoner_details[-1]),
                ),
                commit=True,
            )
        execute_query(
            insert_into_favourite_champions_table_query,
            conn,
            (
                summoner_id,
                random.choice(summoner_details[-2])[0],
                random.choice(summoner_details[-2])[1],
                random.choice(summoner_details[-1]),
            ),
            commit=True,
        )

    print("Database initialized.")
