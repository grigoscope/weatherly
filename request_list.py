import requests


class Requests:
    def __init__(self, appid):
        self.appid = appid
        self._url_find = 'http://api.openweathermap.org/data/2.5/find'
        self._url_weather = "http://api.openweathermap.org/data/2.5/weather"
        self._url_five_days = "http://api.openweathermap.org/data/2.5/forecast"

    def _wind_dir_calc(self, degrees):
        """ Calculates wind direction """
        directions = {
            "N_0": 0,
            "NE": 45,
            "E": 90,
            "SE": 135,
            "S": 180,
            "SW": 225,
            "W": 270,
            "NW": 315,
            "N_360": 360
        }
        return min(directions, key=lambda x: abs(directions[x] - degrees))

    def find_city(self, lat, lon, lang):
        """ Request to find current city """
        params = {
            'lat': lat,
            'lon': lon,
            'type': 'like',
            'units': 'metric',
            'lang': lang,
            'APPID': self.appid
        }
        try:
            res = requests.get(url=self._url_find, params=params)
            status = res.status_code
            return True
        except Exception as e:
            return False

    def current_weather(self, lon, lat, lang):
        """Requests current weather"""
        params = {
            'lat': lat,
            'lon': lon,
            'type': 'like',
            'units': 'metric',
            'lang': lang,
            'APPID': self.appid
        }
        try:
            res = requests.get(url=self._url_weather, params=params)
            d = res.json()
            current_weather = {
                'name': d['name'],
                'condition': d['weather'][0]['description'],
                'temp': round(d['main']['temp']),
                'feels_like': round(d['main']['feels_like']),
                'pressure': round(d['main']['pressure'] * 0.750062),
                'humidity': round(d['main']['humidity']),
                'wind_speed': round(d['wind']['speed']),
                'wind_dir': self._wind_dir_calc(round(d['wind']['deg'])),
                'icon': d['weather'][0]['icon']
            }
            return current_weather
        except Exception as e:
            return False

    def five_days_forecast(self, lat, lon, lang):
        """Responses five days forecast"""
        params = {
            'lat': lat,
            'lon': lon,
            'type': 'like',
            'units': 'metric',
            'lang': lang,
            'APPID': self.appid
        }
        try:
            res = requests.get(url=self._url_five_days, params=params)
            d = res.json()
            curr_list = []
            for i in d['list']:
                curr_list.append({
                    'datetime': i['dt_txt'],
                    'condition': i['weather'][0]['description'],
                    'temp': round(i['main']['temp']),
                    'feels_like': round(i['main']['feels_like']),
                    'pressure': round(i['main']['pressure'] * 0.750062),
                    'humidity': round(i['main']['humidity']),
                    'wind_speed': round(i['wind']['speed']),
                    'wind_dir': self._wind_dir_calc(round(i['wind']['deg'])),
                    'icon': i['weather'][0]['icon']
                })
            return curr_list
        except Exception as e:
            return False
