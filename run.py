#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import yaml
import random

REPEAT = False
items = ['Was sopl das', 'Ohhhh gg', 'Du hast Masse am Ausgang',
        'Wie willst du das ohne TL subwoofer beurteilen?',
        'Bei Vapenation vielleicht, aber hier nicht',
        'Nur 128 kBit/s mp3...', 'Steffi approves', 'Many coins, much worth',
        'Was würde Elon Musk dazu sagen?',
        'Alles lösbar mit Elektromobilitaet',
        'lopl', 'Wann kaufst du dir ein neues Fully?',
        'Man kann auch ein Handy als Protector benutzen',
        'Kommst du ohne quadratischen Screen überhaupt klar?']

with open('config.yaml','r') as yaml_file:
    cfg = yaml.load(yaml_file)
    
try:
    weather_key =  cfg['open_weather']['key']
    telegram_key = cfg['telegram']['key']
    bot_id = cfg['telegram']['bot_id']
    chat_id = cfg['telegram']['chat_id']
except KeyError:
    print('KeyError while reading config')

telegram_url = 'https://api.telegram.org/bot' + bot_id + ':' + telegram_key + '/'
weather_url = 'http://api.openweathermap.org/data/2.5/'

def send_message(msg,parse_mode=None,reply_to_message_id=None):
    r = requests.post(telegram_url + 'sendMessage', 
            data=dict(chat_id=chat_id,text=msg,parse_mode=parse_mode,
                reply_to_message_id=reply_to_message_id))
    print(r.json())

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

def weather_request(location,mode=None):
    r = requests.post(weather_url + 'weather',
            params=dict(q=location,appid=weather_key,units='metric',
                mode=mode,lang='de'))
    print(r.content)
    if not mode:
        return r.json()
    else:
        return r.content

def get_last_msg_id(response):
    msg_id = response.get('result')[-1]['message']['message_id']
    print('msg_id: {}'.format(msg_id))
    return msg_id

def format_weather(json_data):
    location = json_data['name'].encode('utf-8')
    temp = json_data['main']['temp']
    desc = json_data['weather'][0]['description'].encode('utf-8')
    clouds = json_data['clouds']['all']
    humidity = json_data['main']['humidity']
    wind = json_data['wind']['speed']
    answer = ('<strong>{}</strong>\n' +
              '{} Grad\n' +
              '{}\n' +
              '<i>Wolken: {}%</i>\n' +
              '<i>Wind: {} m/s</i>\n' +
              '<i>Feuchtigkeit: {}%</i>').format(location, temp, desc,
                      clouds, wind, humidity)
    return answer

def get_weather_pic_url(location):
    json_data = weather_request(location)
    name = json_data['weather'][0]['icon']
    url = 'http://openweathermap.org/img/w/' + name + '.png'
    return url

def main():
    offset = 0 
    in_answer = False
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
            in_answer = True
            continue
        if in_answer:
            location = answer + ',de'
            json_weather = weather_request(location)
            send_picture(get_weather_pic_url(location))
            send_message(format_weather(json_weather),'HTML')
            in_answer = False
        msg_id = get_last_msg_id(response)
        if msg_id % random.randrange(4,8,1) == 0:
            send_message(items[random.randrange(len(items))],
                    reply_to_message_id=msg_id)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
