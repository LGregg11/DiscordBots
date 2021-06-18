import json
import requests
import pandas as pd


class ProClubsWebScraper:
    def __init__(self):
        self.address = f"https://proclubs.ea.com/api/fifa"

    @staticmethod
    def get_response(endpoint, headers=None):
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status_code" : response.status_code,
                "body": response.content.decode("utf-8")
            }

    def get_club(self, team_name):
        endpoint = self.address + f"/clubs/search?platform=pc&clubName={team_name}"
        try:
            headers = {

                "Referer": "https://www.ea.com/"
            }
            response = self.get_response(endpoint, headers)

        except Exception:
            raise RuntimeError(f"{team_name} - Could not get data")

        return response

    def get_members(self, team_name):
        club_id = list(self.get_club(team_name).keys())[0]

        endpoint = self.address + f"/members/stats?platform=pc&clubId={club_id}"
        try:
            headers = {

                "Referer": "https://www.ea.com/"
            }
            response = self.get_response(endpoint, headers)

        except Exception:
            raise RuntimeError(f"{team_name} - Could not get data")

        return response
