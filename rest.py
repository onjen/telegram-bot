import json
import requests
import time

weather = 'd95b2187ecedb799b74c2697226b234e'
url = 'https://api.telegram.org/bot416506905:AAENuWPzS0qCFFHqtMM4pE3wQqSMg7hzDcU/'

def send_message(msg, chat_id):
    r = requests.post(url + 'sendMessage', data=dict(chat_id=chat_id,text=msg))

def get_messages(response):
    return [msg.get('message').get('text') for msg in response.get('result')]

def get_chat_id(response):
    return response.get('result')[0].get('message').get('chat').get('id')

def main():
    old_messages = []
    offset = 0 
    while True:
        # we have new messages
        response = requests.post(url + 'getUpdates', data=dict(offset=offset+1,timeout=60),timeout=None).json()
        if not response['ok']:
            continue
        offset = response.get('result')[-1].get('update_id')
        send_message('You said: {}'.format(get_messages(response)[-1]),get_chat_id(response))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
