import urllib.request,json

API_URL = 'https://api.weather.gov/points/42.3489,-71.0465'

def load_url(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read())

def save_data(data, filename):
    print(filename)
    with open(filename,'w') as f:
        json.dump(data,f)  

def build_test_data():
    weather_content = load_url(API_URL)
    save_data(weather_content, 'weather_content.json')

    forecast_url = weather_content['properties']['forecast']
    forecast_content = load_url(forecast_url)
    save_data(forecast_content, 'forecast_content.json')

    hourly_url = weather_content['properties']['forecastHourly']
    hourly_content = load_url(hourly_url)
    save_data(hourly_content, 'hourly_content.json')

if __name__ == '__main__':
    print(API_URL)
    build_test_data()




