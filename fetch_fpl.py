"""this module fetches fantasy premier league data for specific leagues"""

from datetime import datetime
from typing import Union
import json
from dateutil.parser import isoparse
import requests


class FetchData:
    """class to fetch fpl data"""

    def __init__(self, league: str):
        self.league_id = league

    def get_league_standings(self, position: int = 10) -> str:
        """Get the league standings for league.

        Args:
            self
            positions (int): number of positions to return

        Returns:
            array: array of length position containing the top players of the league, indexed
            based on positions

        """

        fantasy_api = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{self.league_id}/standings/",
            timeout=10,
        )
        data = fantasy_api.text
        data_json = json.loads(data)
        standings_full = data_json["standings"]["results"]
        league_name = data_json["league"]["name"]

        def player_stats(player: dict) -> str:
            stat = (
                f'{player["rank"]}. {player["player_name"]} '
                f'({player["entry_name"]}) - {player["total"]}'
            )
            return stat

        standings = list(map(player_stats, standings_full))

        return f"\n\033[1;4m{league_name} Current Standings:\033[0m\n\n" + "\n".join(
            standings[:position]
        )

    def get_manager_of_the_month(
        self,
        position: int = 10,
        month: Union[int, str] = datetime.now().strftime("%m"),
        year: Union[int, str] = datetime.now().strftime("%Y"),
    ) -> str:
        """Get the league standings for league for month selected only.

        Args:
            self: class params
            positions (int): number of positions to return
            month (int/date): OPTIONAL month 1-12, if left blank, current month used
            year (int/str): OPTIONAL year, if left blank, current year used

        Returns:
            array: array containing each player in the 1-positions places, indexed
            based on positions for this month

        """

        player_info = self.get_players_in_league()
        gameweek_dates_for_month = self.get_gameweeks_for_month(month, year)

        for _info in player_info:
            player_month_points = self.get_gameweek_points(
                _info["entry"], gameweek_dates_for_month
            )
            _info["month_points"] = str(player_month_points)

        player_info = sorted(
            player_info, key=lambda d: int(d["month_points"]), reverse=True
        )

        def player_string(player: dict) -> str:
            stat = (
                f'{player_info.index(player) + 1}. {player["player_name"]} '
                f'({player["entry_name"]}) - {player["month_points"]}'
            )
            return stat

        standings = list(map(player_string, player_info))

        return (
            f'\n\033[1;4m{player_info[0]["league_name"]} MoM Standings:\033[0m\n\n'
            + "\n".join(standings[:position])
        )

        return player_info

    def get_players_in_league(self) -> list[dict[str, str]]:
        """Get the league standings for league for month selected only.

        Args:
            self: class params

        Returns:
            array: array containing each player id in the league_id class param

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
            self: class params
            player_id (str): player fpl id
            gameweek (list): list of integers representing fpl gameweeks

        Returns:
            int: sum of passed gameweek points

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
            self: class params
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


league_id = input("What is the FPL League ID?\n")

while True:
    try:
        walrus_data = FetchData(league_id)

        print(walrus_data.get_manager_of_the_month(10, 11, 2022))
    except (KeyError, json.JSONDecodeError):
        print("This League ID is invalid, please re-enter the ID: ")
        league_id = input()
        continue
    break
