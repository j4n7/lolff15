import os
import sys
import requests
import urllib3
import json
import time
import random
import string
import ctypes


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Windows title for pyinstaller
ctypes.windll.kernel32.SetConsoleTitleW("LOLFF15")

# Disable insecure https warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Open Telegram token
with open(resource_path('telegram_bot_token')) as file:
    telegram_bot_token = file.read()


TELEGRAM_BOT_TOKEN = telegram_bot_token
TELEGRAM_BOT_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'
TELEGRAM_BOT_UPDATES_URL = f'{TELEGRAM_BOT_URL}/getUpdates'

LOL_LIVE_URL = 'https://127.0.0.1:2999/liveclientdata'
# LOL_LIVE_PLAYER_URL = f'{LOL_LIVE_URL}/activeplayername'
LOL_LIVE_EVENTS_URL = f'{LOL_LIVE_URL}/eventdata'
LOL_LIVE_GAME_URL = f'{LOL_LIVE_URL}/gamestats'

APP_CONFIGURED = True
SUMMONER_NAME = ''
TELEGRAM_ID = ''


def print_logo():
    logo = r'''
  _      ____  _        ______ ______   __ _____ 
 | |    / __ \| |      |  ____|  ____| /_ | ____|
 | |   | |  | | |      | |__  | |__     | | |__  
 | |   | |  | | |      |  __| |  __|    | |___ \ 
 | |___| |__| | |____  | |    | |       | |___) |
 |______\____/|______| |_|    |_|       |_|____/ 
                                                                                                 
'''
    github = 'https://github.com/j4n7/lolff15'

    print(logo + '\n' + github + '\n\n')


def get_random_string(length):
    ramdom_string = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return ramdom_string


def telegram_send(telegram_id, message):
    send_url = f'{TELEGRAM_BOT_URL}/sendMessage?chat_id={str(telegram_id)}&parse_mode=Markdown&text={message}'
    response = requests.get(send_url)

    return response.json()


def telegram_send_id(SUMMONER_NAME):
    summoner_name = ''
    messages = requests.get(TELEGRAM_BOT_UPDATES_URL)
    for message in json.loads(messages.text)['result']:
        if 'entities' in message['message']:
            command = message['message']['text']
            if command.startswith('/summoner'):
                try:
                    summoner_name = message['message']['text'].split()[1]
                    telegram_id = message['message']['from']['id']
                except IndexError:
                    pass

    if SUMMONER_NAME == summoner_name:
        message = telegram_send(telegram_id, telegram_id)
        return True
    
    return False


def configure_user():
    global APP_CONFIGURED
    global SUMMONER_NAME
    global TELEGRAM_ID

    def instructions():
        print('\nWrite the following command in the LOLFF15 Telegram bot:')
        print('/summoner <player name>')
        input('\nPress <enter key> once you have written the command using the LOLFF15 Telegram bot')

    if not os.path.exists('summoner.txt'):
        with open('summoner.txt', 'w'): 
            pass
    with open('summoner.txt') as file:
        lines = [line.rstrip() for line in file.readlines()]

    if len(lines) != 2:
        APP_CONFIGURED = False

    if APP_CONFIGURED:
        SUMMONER_NAME = lines[0]
        TELEGRAM_ID = lines[1]
    else:
        SUMMONER_NAME = input('Write your LOL summoner name: ')
        instructions()
        telegram_sent = telegram_send_id(SUMMONER_NAME)
        while not telegram_sent:
            print('\nWrong command sent or invalid summoner name!!!')
            instructions()
            telegram_sent = telegram_send_id(SUMMONER_NAME)
        TELEGRAM_ID = input('\nWrite here the code that was sent to you by the LOLFF15 Telegram bot: ')
        APP_CONFIGURED = True

        with open('summoner.txt', 'w') as file:
            file.writelines([SUMMONER_NAME, '\n', TELEGRAM_ID])

    print('\nLOL FF 15 is correctly configured\n')
    print(f'Summonner name: {SUMMONER_NAME}')
    print(f'Telegram ID: {TELEGRAM_ID}\n')


def lol_get_events():
    return requests.get(LOL_LIVE_EVENTS_URL, verify=False)


def lol_get_game():
    return requests.get(LOL_LIVE_GAME_URL, verify=False)

def lol_game_telegram(message):
    global TELEGRAM_ID
    telegram_send(TELEGRAM_ID, message)

def lol_main_loop():

    LOL_LIVE_GAME_TIME_CURRENT = 0.0
    LOL_LIVE_GAME_TIME_START = 0.0
    LOL_LIVE_GAME_TIME_START_THRESHOLD = 20.0

    LOL_LIVE_WAITING_MESSAGE = True

    interval_time = 60.0  #Seconds

    while True:
        try:
            lol_get_game()
            status_code = lol_get_game().status_code
            if status_code == 200:
                game_time = float(json.loads(lol_get_game().text)['gameTime'])
                if LOL_LIVE_GAME_TIME_CURRENT == 0.0 and game_time <= LOL_LIVE_GAME_TIME_START_THRESHOLD:
                    LOL_LIVE_GAME_TIME_START = time.time()
                    lol_game_telegram(f'\U0001F9D9 Game started! \U000026A0 ({get_random_string(6)})')
                    # Python unicodes: replace “+” with “000” till 9 characters and add \
                    print(f'\n[{time.strftime("%H:%M:%S")}] Game started!')
                else:
                    print(f'[{time.strftime("%H:%M:%S")}] Game live!')
                LOL_LIVE_GAME_TIME_CURRENT = game_time
                LOL_LIVE_WAITING_MESSAGE = True
                time.sleep(interval_time - ((time.time() - LOL_LIVE_GAME_TIME_START) % interval_time))
        except requests.exceptions.ConnectionError:
            LOL_LIVE_GAME_TIME_CURRENT = 0.0
            LOL_LIVE_GAME_TIME_START = 0.0
            if LOL_LIVE_WAITING_MESSAGE:
                print('\nWaiting for game...')
            LOL_LIVE_WAITING_MESSAGE = False
            

if __name__ == '__main__':
    print_logo()
    configure_user()
    lol_main_loop()
