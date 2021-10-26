from settings import FACEIT_HEADERS, STEAM_API_KEY
import requests
import re
import xml.etree.ElementTree as et
import json
import logging
import datetime


logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


class InputLinter():
    def __init__(self):
        self.user_input_data = input("Faceit name | Steam URL | Match ID: ")
        tim = (datetime.datetime.now()).time()
        logging.info(f'ПРИНЯЛ ИНПУТ {tim}')

    def returner(self):
        if self.user_input_data.startswith('steamcommunity.com/id/') or self.user_input_data.startswith('https://steamcommunity.com/id/'):
            input_data = {'steam_url': self.user_input_data}
        elif re.fullmatch(r'1-[a-zA-z0-9]{8}-[a-zA-z0-9]{4}-[a-zA-z0-9]{4}-[a-zA-z0-9]{4}-[a-zA-z0-9]{12}', self.user_input_data):
            input_data = {'match_id': self.user_input_data}
        else:
            input_data = {'faceit_name': self.user_input_data}
        return input_data


class MainDataCollector(InputLinter):
    def data_analyzer(self):
        input_data = self.returner()
        if 'steam_url' in input_data:
            self.getter_controller(steam_url=input_data['steam_url'])
        elif 'faceit_name' in input_data:
            self.getter_controller(faceit_name=input_data['faceit_name'])
        elif 'match_id' in input_data:
            self.getter_controller(faceit_name=input_data['match_id'])
        else:
            print('Data not found.')
    
    def getter_controller(self, steam_url=None, faceit_name=None, match_id=None):
        tim = (datetime.datetime.now()).time()        
        logging.info(f'ИНПУТ ДАТА ПОПАДАЕТ НА КОНТРОЛЛЕР {tim}')
        if steam_url:
            self.data_collector(steam_url)
        elif faceit_name:
            faceit_request_url = 'https://open.faceit.com/data/v4/players?nickname='+ faceit_name +'&game=csgo'
            faceit_response = requests.get(faceit_request_url, headers=FACEIT_HEADERS).json()
            steam_response_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key="+STEAM_API_KEY+"&steamids="+faceit_response["steam_id_64"]
            steam_response = requests.get(steam_response_url).json()
            steam_url = steam_response["response"]["players"][0]["profileurl"]
            self.data_collector(steam_url)
        elif match_id:
            pass

    def data_collector(self, steam_url):
        #Getting steam info
        tim = (datetime.datetime.now()).time()
        logging.info(f'СОБИРАЕМ ИНФУ СТИМ {tim}')
        steam_user_url_xml = steam_url + "?xml=1"
        root = et.fromstring(requests.get(steam_user_url_xml).content)
        steamid64 = root.find("steamID64").text #steamid
        steam_name = root.find("steamID").text #steamname
        vac = root.find("vacBanned").text #number of VAC blocks
        json_url = "http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key=" + STEAM_API_KEY + "&steamids=" + steamid64
        result = requests.get(json_url, params={"format": "json",})
        steam_json_data = result.json()
        #Getting info about VAC blocks on account
        if "players" in steam_json_data:
            try:
                last_vac = steam_json_data["players"][0]["DaysSinceLastBan"] #days sine last vac
            except(IndexError, TypeError):
                last_vac = "No Data"

        #Getting Faceit info
        tim = (datetime.datetime.now()).time()
        logging.info(f'СОБИРАЕМ ИНФУ ФЕСИТ {tim}')
        first_faceit_url = "https://open.faceit.com/data/v4/players?game=csgo&game_player_id="+steamid64
        faceit_info = requests.get(first_faceit_url, headers=FACEIT_HEADERS).json()

        faceit_id = faceit_info["player_id"]
        faceit_name = faceit_info["nickname"]
        faceit_level = faceit_info["games"]["csgo"]["skill_level_label"]
        faceit_elo = faceit_info["games"]["csgo"]["faceit_elo"]

        user_info = {
            "steamID64": steamid64, 
            "steamname": steam_name, 
            "VAC": vac, 
            "DaysSinceLastBan": last_vac,
            "FACEITID": faceit_id,
            "FACEIT_NAME": faceit_name,
            "FACEIT_LEVEL": faceit_level,
            "FACEIT_ELO": faceit_elo,
            }
       
        print(user_info)
        tim = (datetime.datetime.now()).time()
        logging.info(f'Готово {tim}')


if __name__ == '__main__':
    a = MainDataCollector()
    a.data_analyzer()
