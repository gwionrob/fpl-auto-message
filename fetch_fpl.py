"""this module fetches fantasy premier league data for specific leagues"""

from datetime import datetime
from typing import Union
import json
import requests


class FetchData:
    """class to fetch fpl data"""

    def __init__(self, league: str):
        self.league_id = league

    def get_league_standings(self, position: int) -> str:
        """Get the league standings for league.

        Args:
            self: class params
            positions (int): number of positions to return

        Returns:
            array: array containing each player in the 1-positions places, indexed
            based on positions

        """

        fantasy_api = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{self.league_id}/standings/",
            timeout=10,
        )
        data = fantasy_api.text
        data_json = json.loads(data)
        standings_dict = data_json["standings"]["results"]

        def player_stats(player: dict) -> str:
            stat = f'{player["rank"]}. {player["player_name"]} ({player["entry_name"]}) - {player["total"]}'
            return stat

        standings = list(map(player_stats, standings_dict))

        return "\n".join(standings[:position])

    def get_manager_of_the_month(
        self,
        position: int,
        month: Union[int, str] = datetime.now().strftime("%m"),
    ) -> str:
        """Get the league standings for league for month selected only.

        Args:
            self: class params
            positions (int): number of positions to return
            month (int): OPTIONAL month 1-12, if left blank, current month used

        Returns:
            array: array containing each player in the 1-positions places, indexed
            based on positions for this month

        """

        return f"""top {str(position)} best managers for month
                 {str(month)} in {self.league_id} is gwion"""


league_id = input("What is the FPL League ID?\n")

while True:
    try:
        walrus_data = FetchData(league_id)
        print(walrus_data.get_league_standings(10))
    except (KeyError, json.JSONDecodeError):
        print("This League ID is invalid, please re-enter the ID: ")
        league_id = input()
        continue
    break
