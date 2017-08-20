import requests
import time
import yaml

REPEAT = False

with open('config.yaml','r') as yaml_file:
    cfg = yaml.load(yaml_file)
    
try:
    weather_key =  cfg['open_weather']['key']
    telegram_key = cfg['telegram']['key']
    bot_id = cfg['telegram']['bot_id']
    chat_id = cfg['telegram']['chat_id']
except KeyError:
    print('KeyError while reading config')

telegram_url = 'https://api.telegram.org/' + bot_id + ':' + telegram_key + '/'
weather_url = 'http://api.openweathermap.org/data/2.5/'

def send_message(msg, chat_id):
    r = requests.post(telegram_url + 'sendMessage', 
            data=dict(chat_id=chat_id,text=msg))

def get_response(offset, timeout):
    r = requests.post(telegram_url + 'getUpdates',
                data=dict(offset=offset,timeout=timeout),timeout=None).json()
    return r

def get_messages(response):
    return [msg.get('message').get('text') for msg in response.get('result')]

def get_chat_id(response):
    return response.get('result')[0].get('message').get('chat').get('id')

def weather_request(location):
    r = requests.post(weather_url + 'weather', 
            params=dict(q=location,appid=weather_key,units='metric',lang='de'))
    return r.json()

def format_weather(json_data):
    location = json_data['name']
    temp = json_data['main']['temp']
    desc = json_data['weather'][0]['description']
    answer = 'Wetter in {}\nTemperatur: {} C\n{}'.format(location, 
            temp, desc) 
    return answer

def main():
    offset = 0 
    while True:
        # we have new messages
        response = get_response(offset+1, 60)
        try:
            offset = response.get('result')[-1].get('update_id')
        except IndexError:
            # long polling timeout, try again
            continue
        answer = get_messages(response)[-1]
        if REPEAT:
            send_message('You said: {}'.format(answer), chat_id)
        if answer.lower() == "wetter":
            json_weather = weather_request('Essen,de')
            send_message(format_weather(json_weather),chat_id)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
