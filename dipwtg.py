from settings import FACEIT_HEADERS, STEAM_API_KEY
import requests
from main import MainDataCollector


class Player():
    def __init__(self):
        self.faceeit_nickname = input("Please, enter your name: ")
        self.match_id = input("Please, enter match_id: ")
    
    def get_current_players(self):
        current_match = MainDataCollector.current_match_data_collector(self.match_id)
        return current_match
    
    def get_match_history(self):
        user_faceit_id = (MainDataCollector.getter_controller(faceit_name=self.faceeit_nickname))["FACEITID"] #ПОД ВОПРОСОМ
        faceit_request_URL = "https://open.faceit.com/data/v4/players/" + user_faceit_id + "/history?game=csgo&offset=0&limit=20"
        faceit_request = requests.get(faceit_request_URL, headers=FACEIT_HEADERS).json()

        #Getting the match from matches, and check it for users from current match. Incomplite.