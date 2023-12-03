import requests


def get_summoner_info(summoner_name: str, API_KEY: str):
    summoner_endpoint = '/lol/summoner/v4/summoners/by-name/'
    summoner_api_url = f'https://eun1.api.riotgames.com{summoner_endpoint}{summoner_name}'

    params = {
        'api_key': API_KEY,
    }

    try:
        response = requests.get(url=summoner_api_url, params=params)
        response.raise_for_status()
        summoner = response.json()
        return summoner

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def get_summoner_puuid(summoner_name: str, API_KEY: str):
    return get_summoner_info(summoner_name, API_KEY)['puuid']


def get_list_of_match_ids(summoner_puuid: int, API_KEY: str):
    list_of_match_ids_endpoint = f'/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids'
    list_of_match_ids_api_url = f'https://europe.api.riotgames.com{list_of_match_ids_endpoint}'

    params = {
        'api_key': API_KEY,
    }

    try:
        response = requests.get(url=list_of_match_ids_api_url, params=params)
        response.raise_for_status()
        match_ids = response.json()
        return match_ids

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def get_match_info(match_id: str, API_KEY: str):
    match_endpoint = '/lol/match/v5/matches/'
    match_api_url = f'https://europe.api.riotgames.com{match_endpoint}{match_id}'

    params = {
        'api_key': API_KEY,
    }

    try:
        response = requests.get(url=match_api_url, params=params)
        response.raise_for_status()
        match_info = response.json()
        return match_info

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def get_champion_played_by_user(match_id: str, summoner_name: str, API_KEY: str):
    participants = get_match_info(match_id=match_id, API_KEY=API_KEY)['info']['participants']
    try:
        result = next(participant['championName'] for participant in participants if participant['summonerName'] == summoner_name)
        return result
    except StopIteration:
        return None


def get_champion_rotations(API_KEY: str):
    champion_rotations_endpoint = '/lol/platform/v3/champion-rotations'
    champion_rotations_api_url = f'https://eun1.api.riotgames.com{champion_rotations_endpoint}'

    params = {
        'api_key': API_KEY,
    }

    try:
        response = requests.get(url=champion_rotations_api_url, params=params)
        response.raise_for_status()
        champion_rotations = response.json()
        return champion_rotations

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def get_latest_version():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"

    try:
        response = requests.get(url)
        response.raise_for_status()

        versions = response.json()

        return versions

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def get_champions(version: str):
    url = f'https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json'

    try:
        response = requests.get(url)
        response.raise_for_status()

        champions = response.json()

        return champions

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def map_champion_id_to_name(champion_id):
    latest_version = get_latest_version()[0]
    champion_data = get_champions(latest_version)
    champion_id = str(champion_id)
    c = champion_data['data']
    for k, v in c.items():
        if v['key'] == champion_id:
            return v['name']

    return None
