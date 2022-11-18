"""this module sets out to automate the fetching of fantasy premier league data
for specific leagues, and then send an automated update to a WhatsApp group"""

from datetime import datetime


class fetch_data:
    """class to fetch fpl data"""

    def __init__(self, league: str):
        self.league = league

    def get_league_standings(self, position: int) -> list[str]:
        """Get the league standings for league.

        Args:
            self: class params
            positions (int): number of positions to return

        Returns:
            array: array containing each player in the 1-positions places, indexed
            based on positions

        """

        print(self.league + " " + str(position) + " places in overall ranking")

    def get_manager_of_the_month(
        self, position: int, month: int = datetime.now().month
    ):
        """Get the league standings for league for month selected only.

        Args:
            self: class params
            positions (int): number of positions to return
            month (int): OPTIONAL month 1-12, if left blank, current month used

        Returns:
            array: array containing each player in the 1-positions places, indexed
            based on positions for this month

        """

        print(
            str(position)
            + " best managers for month "
            + str(month)
            + " in "
            + self.league
            + " is gwion"
        )


walrus_data = fetch_data("walrus united")

print(walrus_data.get_manager_of_the_month(4))
