import requests
import time
import yaml

with open('config.yaml','r') as yaml_file:
    cfg = yaml.load(yaml_file)
    
try:
    weather_key =  cfg['open_weather']['key']
    telegram_key = cfg['telegram']['key']
    bot_id = cfg['telegram']['bot_id']
except KeyError:
    print('KeyError while reading config')

telegram_url = 'https://api.telegram.org/' + bot_id + ':' + telegram_key + '/'

def send_message(msg, chat_id):
    r = requests.post(telegram_url + 'sendMessage', 
            data=dict(chat_id=chat_id,text=msg))

def get_messages(response):
    return [msg.get('message').get('text') for msg in response.get('result')]

def get_chat_id(response):
    return response.get('result')[0].get('message').get('chat').get('id')

def main():
    offset = 0 
    while True:
        # we have new messages
        response = requests.post(telegram_url + 'getUpdates',
                data=dict(offset=offset+1,timeout=60),timeout=None).json()
        offset = response.get('result')[-1].get('update_id')
        send_message('You said: {}'.format(get_messages(response)[-1]),
                get_chat_id(response))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
