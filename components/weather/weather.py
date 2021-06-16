import pyowm
import geocoder
import requests


class Weather:
    APIKEY = 'b7ef9a1647a36bdb99c857407dc5e116'

    def __init__(self):
        OpenWMap = pyowm.OWM(Weather.APIKEY)
        self.mgr = OpenWMap.weather_manager()

        self.get_loc()
        Weath = self.mgr.weather_at_place(self.city)
        self.data = Weath.weather

    def get_loc(self):
        g = geocoder.ip('me')
        json_file = g.geojson
        self.city = json_file.get("features")[0]['properties']['city']

    def get_temp(self, temp_type):
        self.type = temp_type
        return self.data.temperature(temp_type)['temp']

    @staticmethod
    def icon(icon_id):
        return f'http://openweathermap.org/img/wn/{icon_id}@4x.png'

    def get_icon(self):
        return self.icon(self.data.weather_icon_name)

    def get_min(self):
        return str(int(self.data.temperature(self.type)['temp_min'])) + "C°"

    def get_max(self):
        return str(int(self.data.temperature(self.type)['temp_max'])) + "C°"

    # Forecast

    def get_fc(self):
        api_call = 'https://api.openweathermap.org/data/2.5/forecast?appid=' + 'b7ef9a1647a36bdb99c857407dc5e116' + "&q=" + self.city

        json_data = requests.get(api_call).json()

        current_date = ''
        maxt = []
        mint = []
        icon_id = ''

        forecast_list = []

        # Iterates through the array of dictionaries named list in json_data
        for item in json_data['list']:
            time = item['dt_txt']
            next_date, hour = time.split(' ')

            if current_date != next_date:
                if current_date != '':
                    forecast = {"date": f"{day}.{month}", "max": max(maxt), "min": min(mint), "icon": item['weather'][0]['icon']}
                    forecast_list.append(forecast)
                    maxt = []
                    mint = []

                current_date = next_date
                year, month, day = current_date.split('-')

            maxt.append(int(item['main']['temp_max'] - 273.15))
            mint.append(int(item['main']['temp_min'] - 273.15))

        return forecast_list


w = Weather()
print("Now ", w.get_temp("celsius"))
print("Min ", w.get_min())
print("Max", w.get_max())
print(w.get_fc())
