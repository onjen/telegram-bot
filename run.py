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

def send_message(msg):
    r = requests.post(telegram_url + 'sendMessage', 
            data=dict(chat_id=chat_id,text=msg))
    print r.json()

def send_picture(url):
    r = requests.post(telegram_url + 'sendPhoto', 
            data=dict(chat_id=chat_id,photo=url))

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
    if r.ok:
        return r.json()
    else:
        print('Request not successful with {}'.format(r.url))
        return None

def format_weather(json_data):
    location = json_data['name'].encode('utf-8')
    temp = json_data['main']['temp']
    desc = json_data['weather'][0]['description'].encode('utf-8')
    answer = 'Wetter in {}\nTemperatur: {} Grad\n{}'.format(location,
            temp, desc)
    return answer

def get_weather_pic_url(json_data):
    name = json_data['weather'][0]['icon']
    url = 'http://openweathermap.org/img/w/' + name + '.png'
    return url

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
        print(answer)
        if REPEAT:
            send_message('You said: {}'.format(answer))
        if answer.lower() == "wetter":
            send_message('An welchem Ort?')
            continue
        json_weather = weather_request(answer + ',de')
        send_picture(get_weather_pic_url(json_weather))
        send_message(format_weather(json_weather))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
