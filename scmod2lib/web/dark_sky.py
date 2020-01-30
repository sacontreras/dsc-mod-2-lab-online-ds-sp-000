import requests

class DSAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.darksky.net/forecast"

    def get_weather(self, lat, lon, sYYYY, sMM, sDD, sHH='12', smm='00', sSS='00'):
        #https://api.darksky.net/forecast/[key]/[latitude],[longitude],[time], where [time] is in format [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS][timezone]

        url = f"{self.base_url}/{self.api_key}/{lat},{lon},{sYYYY}-{sMM}-{sDD}T{sHH}:{smm}:{sSS}"
        #print(f"request: {url}")
        response = requests.get(url)
        #print(response)

        return response

    