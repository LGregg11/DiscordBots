from bs4 import BeautifulSoup
import requests

CONFIGS = {
    "region": "euw"
}


class LoLWebScraper:
    def __init__(self, region=CONFIGS["region"]):
        self.address = f"https://{region}.op.gg/"

    def get_winloss(self, summoner_name):
        endpoint = self.address + f"summoner/userName={summoner_name}"
        try:
            response = requests.get(endpoint).text
            soup = BeautifulSoup(response, 'lxml')
            return {
                "wins": soup.find("span", class_="wins").text,
                "losses": soup.find("span", class_="losses").text,
                "ratio": soup.find("span", class_="winratio").text
            }

        except ConnectionError:
            raise RuntimeError(f"{summoner_name} - Could not get rank summary")
