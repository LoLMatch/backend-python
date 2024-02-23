import requests

class RiotAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://eun1.api.riotgames.com'
        self.europe_url = 'https://europe.api.riotgames.com'
        self.ddragon_url = 'https://ddragon.leagueoflegends.com'

    def _request(self, url: str, params: dict = None):
        """General request handler."""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def get_summoner_info_by_name(self, summoner_name: str):
        url = f'{self.base_url}/lol/summoner/v4/summoners/by-name/{summoner_name}'
        return self._request(url)

    def get_summoner_info_by_puuid(self, summoner_puuid: str):
        url = f'{self.base_url}/lol/summoner/v4/summoners/by-puuid/{summoner_puuid}'
        return self._request(url)

    def get_summoner_entries(self, summoner_puuid: str):
        summoner_info = self.get_summoner_info_by_puuid(summoner_puuid)
        if summoner_info:
            url = f'{self.base_url}/lol/league/v4/entries/by-summoner/{summoner_info["id"]}'
            entries = self._request(url)
            return entries[0] if entries else None

    def get_list_of_match_ids(self, summoner_puuid: str):
        url = f'{self.europe_url}/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids'
        return self._request(url)

    def get_match_info(self, match_id: str):
        url = f'{self.europe_url}/lol/match/v5/matches/{match_id}'
        return self._request(url)

    def get_champion_played_by_user(self, match_id: str, summoner_name: str):
        match_info = self.get_match_info(match_id)
        if match_info:
            participants = match_info['info']['participants']
            for participant in participants:
                if participant['summonerName'] == summoner_name:
                    return participant['championName']
        return None

    def get_champion_rotations(self):
        url = f'{self.base_url}/lol/platform/v3/champion-rotations'
        return self._request(url)

    def get_latest_version(self):
        url = f"{self.ddragon_url}/api/versions.json"
        return self._request(url)

    def get_champions(self, version: str):
        url = f'{self.ddragon_url}/cdn/{version}/data/en_US/champion.json'
        return self._request(url)

    def map_champion_id_to_name(self, champion_id: int):
        latest_version = self.get_latest_version()[0]
        champions_data = self.get_champions(latest_version)
        for champion in champions_data['data'].values():
            if str(champion_id) == champion.get('key'):
                return champion['name']
        return None
