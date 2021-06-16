from bs4 import BeautifulSoup
import requests
import pandas as pd

CONFIGS = {
    "region": "euw"
}


class LoLWebScraper:
    def __init__(self, region=CONFIGS["region"]):
        self.address = f"https://{region}.op.gg"

    @staticmethod
    def get_beautiful_soup_response(endpoint):
        response = requests.get(endpoint).text
        return BeautifulSoup(response, 'lxml')

    def get_winloss(self, summoner_name):
        endpoint = self.address + f"/summoner/userName={summoner_name}"
        try:
            soup = self.get_beautiful_soup_response(endpoint)
            return {
                "wins": soup.find("span", class_="wins").text,
                "losses": soup.find("span", class_="losses").text,
                "ratio": soup.find("span", class_="winratio").text
            }

        except Exception:
            raise RuntimeError(f"{summoner_name} - Could not get rank summary")

    def get_most_played_champs(self, season, summoner_name):
        """
        Access summoner's played champion data for a particular season from the web scraper address and
        return the info as a pandas table

        :param season: The ranked season
        :param summoner_name: The summoner name
        :return: Summoner's ranked played champs data as Pandas table
        """

        seasons = {
            "2021": "season-17",
            "2020": "season-15",
            "9": "season-13",
            "8": "season-11",
            "7": "season-7",
            "6": "season-6",
            "5": "season-5",
            "4": "season-4",
            "3": "season-3",
            "2": "season-2",
            "1": "season-1",
            "normal": "season-normal"
        }

        if season not in seasons.keys():
            raise RuntimeError(f"{season} is not an expected season number")

        endpoint = self.address + f"/summoner/champions/userName={summoner_name}"
        try:
            soup = self.get_beautiful_soup_response(endpoint)
            if season != "2021":
                endpoint = self.address + soup.find("div", class_=f"tabItem {seasons[season]}")["data-tab-data-url"]
                soup = self.get_beautiful_soup_response(endpoint)

        except Exception:
            raise RuntimeError(f"{summoner_name} - Could not get data")

        table = soup.find("table")
        if table:
            return pd.read_html(str(table))[0]
        raise RuntimeError("No data")
