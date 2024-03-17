import sys
import random
from pathlib import Path

from . import riot_api_functions
from .connect import get_db_connection


def prepare_db():

    current_dir = Path(__file__).parent.absolute()
    parent_dir = current_dir.parent
    sys.path.append(str(parent_dir))

    API_KEY = "RGAPI-1067e83c-cbbc-421d-bcd2-beefe1a0900c"

    # table containing summoners' ids and their personal data
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

    # table containing summoners' descriptions
    create_summoners_descriptions_table_query = """
        CREATE TABLE IF NOT EXISTS summoners_descriptions (
            id SERIAL PRIMARY KEY,
            summoner_id INT NOT NULL,
            description TEXT NOT NULL,
            short_description TEXT NOT NULL,
            FOREIGN KEY (summoner_id) REFERENCES summoners(id)
        )
        """

    # table containing summoners' ids and languages they speak
    create_summoners_languages_table_query = """
        CREATE TABLE IF NOT EXISTS languages_spoken (
            summoner_id INT NOT NULL,
            language VARCHAR(255) NOT NULL,
            FOREIGN KEY (summoner_id) REFERENCES summoners(id)
        )
        """

    # table containing summoners' ids and their preferred champions and lines
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

    # table containing summoners' accepted recommendations
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

    # table containing summoners' rejected recommendations
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
        INSERT INTO summoners (name, puuid, sex, country, level, tier, rank, wins, losses, age, favourite_line) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

    drop_table_summoners_query = """
        DROP TABLE IF EXISTS summoners
        """

    drop_table_summoners_descriptions_query = """
        DROP TABLE IF EXISTS summoners_descriptions
        """

    drop_table_summoners_languages_query = """  
        DROP TABLE IF EXISTS languages_spoken 
        """

    drop_table_summoners_preferred_champions_and_lines_query = """  
        DROP TABLE IF EXISTS preferred_champions_and_lines
        """

    drop_table_favorite_champions_query = """
        DROP TABLE IF EXISTS favourite_champions
        """

    drop_table_summoners_recommendations_query = """
        DROP TABLE IF EXISTS recommendations
        """

    drop_table_summoners_accepted_recommendations_query = """
        DROP TABLE IF EXISTS accepted_recommendations
        """

    drop_table_summoners_rejected_recommendations_query = """
        DROP TABLE IF EXISTS rejected_recommendations
        """

    drop_table_matches_query = """
        DROP TABLE IF EXISTS matches
        """

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(drop_table_matches_query)
    cursor.execute(drop_table_summoners_rejected_recommendations_query)
    cursor.execute(drop_table_summoners_accepted_recommendations_query)
    cursor.execute(drop_table_favorite_champions_query)
    cursor.execute(drop_table_summoners_recommendations_query)
    cursor.execute(drop_table_summoners_preferred_champions_and_lines_query)
    cursor.execute(drop_table_summoners_languages_query)
    cursor.execute(drop_table_summoners_descriptions_query)
    cursor.execute(drop_table_summoners_query)
    print("dropped tables")

    cursor.execute(create_summoners_table_query)
    cursor.execute(create_summoners_descriptions_table_query)
    cursor.execute(create_summoners_languages_table_query)
    cursor.execute(create_summoners_preferred_champions_and_lines_table_query)
    cursor.execute(create_favourite_champions_table_query)
    cursor.execute(create_summoners_accepted_recommendations_table_query)
    cursor.execute(create_summoners_rejected_recommendations_table_query)
    cursor.execute(create_matches_table_query)
    print("created tables")

    conn.commit()

    description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque enim sem, cursus at neque rutrum, viverra feugiat orci. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nam vitae magna vehicula, faucibus eros id, egestas mauris. Aenean mollis ac purus vitae mattis. Aenean eget porttitor turpis. Nam fermentum justo non quam tempus, nec interdum quam semper. Sed at faucibus ligula, facilisis congue libero. Suspendisse hendrerit varius augue, ut rutrum nulla condimentum nec. Nam nulla urna, placerat imperdiet vulputate ac, ullamcorper in magna. Duis vitae augue tincidunt, ultrices lorem eget, suscipit lorem. Sed quam nulla, fermentum sit amet ullamcorper id, dictum et sapien. Sed mollis nulla at nisl tincidunt lobortis. Maecenas lectus est, commodo a scelerisque a, semper in libero. Fusce vel accumsan neque."

    short_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    summoners = set()

    with open("static/summoners.txt", "r") as f:
        for line in f:
            summoner_name = line.split()[0]
            summoner_puuid = line.split()[1]
            summoner = (summoner_name, summoner_puuid)
            summoners.add(summoner)

    riot_api = riot_api_functions.RiotAPI(API_KEY)

    latest_version = riot_api.get_latest_version()[0]
    champions_json = riot_api.get_champions(latest_version)
    champions = list()

    for champion in champions_json["data"].values():
        champion_id = int(champion["key"])
        champion_name = champion["name"]

        c = (champion_id, champion_name)
        champions.append(c)

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

    for i, summoner in enumerate(summoners):
        print("Run:", i)
        if i == 10:
            break
        summoner_name = summoner[0]
        summoner_puuid = summoner[1]
        summoner_sex = random.choice(sexes)
        summoner_country = random.choice(countries)
        summoner_level = random.randint(1, 30)
        summoner_tier = random.choice(
            [
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
        )
        summoner_rank = random.choice(["I", "II", "III", "IV"])
        summoner_wins = random.randint(0, 1000)
        summoner_losses = random.randint(0, 1000)
        summoner_age = random.randint(18, 35)
        summoner_favourite_line = random.choice(roles)
        summoner_languages = random.sample(languages, random.randint(1, 5))
        preferred_champions = random.sample(champions, 3)
        preferred_lines = random.sample(roles, 3)

        cursor.execute(
            insert_into_summoners_table_query,
            (
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
            ),
        )

        print("added to summoners")

        cursor.execute("SELECT id FROM summoners WHERE name = %s", (summoner_name,))
        summoner_id = cursor.fetchone()[0]

        cursor.execute(
            insert_into_summoners_descriptions_table_query,
            (summoner_id, description, short_description),
        )

        for language in summoner_languages:
            cursor.execute(
                insert_into_summoners_languages_table_query, (summoner_id, language)
            )

        print("added languages")

        for champion in preferred_champions:
            cursor.execute(
                insert_into_summoners_preferred_champions_and_lines_table_query,
                (summoner_id, champion[0], champion[1], random.choice(preferred_lines)),
            )

        favourite_champion = random.choice(champions)
        cursor.execute(
            insert_into_favourite_champions_table_query,
            (
                summoner_id,
                favourite_champion[0],
                favourite_champion[1],
                random.choice(roles),
            ),
        )

    conn.commit()
