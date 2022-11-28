"""this module fetches fantasy premier league data for specific leagues"""

from datetime import datetime
from typing import Union
import json
from dateutil.parser import isoparse
import requests


class League:
    """class representing fpl league data"""

    def __init__(self, league: str):
        self.league_id = league

    def get_league_standings(self, position: int = 10) -> str:
        """Get the league standings for league.

        Args:
            positions (int): number of positions to return

        Returns:
            list[dict]: list containing the top players of the league as a
            dict containing rank, player_name, entry_name and total. listed
            based on positions

        """

        fantasy_api = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{self.league_id}/standings/",
            timeout=10,
        )
        data = fantasy_api.text
        data_json = json.loads(data)
        standings_full = data_json["standings"]["results"][:position]
        wanted_keys = ["rank", "player_name", "entry_name", "total"]

        def player_stats(player: dict) -> dict:
            return {key: player[key] for key in wanted_keys}

        standings = list(map(player_stats, standings_full))
        return standings

    def get_manager_of_the_month(
        self,
        position: int = 10,
        month: Union[int, str] = datetime.now().strftime("%m"),
        year: Union[int, str] = datetime.now().strftime("%Y"),
    ) -> str:
        """Get the league standings for league for month selected only.

        Args:
            positions (int): number of positions to return
            month (int/date): OPTIONAL month 1-12, if left blank, current month used
            year (int/str): OPTIONAL year, if left blank, current year used

        Returns:
            list[dict]: list containing the top players of the league for the month provided.
            These entries are dicts containing rank, player_name, entry_name and total. listed
            based on positions

        """

        player_info = self.get_players_in_league()[:position]
        gameweek_dates_for_month = self.get_gameweeks_for_month(month, year)

        for _info in player_info:
            player_month_points = self.get_gameweek_points(
                _info["entry"], gameweek_dates_for_month
            )
            _info["month_points"] = player_month_points

        player_info = sorted(player_info, key=lambda d: d["month_points"], reverse=True)

        for _info in player_info:
            _info["rank"] = player_info.index(_info) + 1

        wanted_keys = ["rank", "player_name", "entry_name", "month_points"]

        def player_stats(player: dict) -> dict:
            return {key: player[key] for key in wanted_keys}

        standings = list(map(player_stats, player_info))
        return standings

    def get_players_in_league(self) -> list[dict[str, str]]:
        """Get the league standings for league for month selected only.

        Returns:
            list: list containing each player id in the league_id class param

        """

        fantasy_api = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{self.league_id}/standings/",
            timeout=10,
        )
        data = fantasy_api.text
        data_json = json.loads(data)
        standings_full = data_json["standings"]["results"]
        league_name = data_json["league"]["name"]

        def player_info(player: dict) -> dict[str, str]:
            info = {
                k: v
                for k, v in player.items()
                if k in ["entry", "player_name", "entry_name"]
            }
            info["league_name"] = league_name
            return info

        player_info_arr = list(map(player_info, standings_full))

        return player_info_arr

    def get_gameweek_points(self, player_id: str, gameweek: list[int] = [0]) -> int:
        """Get the sum of passed gameweeks. If gameweek not passed, return total points.

        Args:
            player_id (str): player fpl id
            gameweek (list): list of integers representing fpl gameweeks

        Returns:
            int: sum of gameweek points

        """

        fantasy_api = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{player_id}/history/",
            timeout=10,
        )
        data = fantasy_api.text
        data_json = json.loads(data)
        all_gameweek_results = data_json["current"]

        if gameweek == [0]:
            total_points = all_gameweek_results[-1]["total_points"]
            return total_points

        gameweek_results = [
            int(e["points"]) for e in all_gameweek_results if e["event"] in gameweek
        ]

        return sum(gameweek_results)

    def get_gameweeks_for_month(
        self,
        month: Union[int, str] = datetime.now().strftime("%m"),
        year: Union[int, str] = datetime.now().strftime("%Y"),
    ):
        """Get the date of each gameweek.

        Args:
            month (int/str): OPTIONAL month 1-12, if left blank, current month used
            year (int/str): OPTIONAL year, if left blank, current year used

        Returns:
            dict: dict containing the gameweek number and date

        """

        fantasy_api = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=10,
        )
        data = fantasy_api.text
        data_json = json.loads(data)
        events_full = data_json["events"]

        def gameweek_dates(gameweek: dict) -> datetime:
            date = f'{gameweek["deadline_time"]}'
            return isoparse(date)

        dates = list(map(gameweek_dates, events_full))
        dates_dict = {k: dates[k - 1] for k in range(1, len(dates) + 1)}
        gameweeks_for_month = list(
            {
                k: v
                for k, v in dates_dict.items()
                if v.month == int(month) and v.year == int(year)
            }.keys()
        )

        return gameweeks_for_month


# league_id = input("What is the FPL League ID?\n")
#
# while True:
#     try:
#         walrus_data = FetchData(league_id)
#
#         USER_CHOICE = ""
#         options = ["Current league standings", "Manager of the Month (MoM)"]
#         INPUT_MESSAGE = "Choose option?\n"
#         for index, item in enumerate(options):
#             INPUT_MESSAGE += f"{index+1}) {item}\n"
#
#         while USER_CHOICE not in map(str, range(1, len(options) + 1)):
#             if USER_CHOICE != "":
#                 print(f"Please select one of the options (1-{len(options)}):")
#             USER_CHOICE = input(INPUT_MESSAGE)
#
#         if USER_CHOICE == "1":
#             print(walrus_data.get_league_standings(10))
#         elif USER_CHOICE == "2":
#             print(walrus_data.get_manager_of_the_month(10, 11, 2022))
#
#     except (KeyError, json.JSONDecodeError):
#         print("This League ID is invalid, please re-enter the ID: ")
#         league_id = input()
#         continue
#     break
