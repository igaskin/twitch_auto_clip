'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import sys
import os
import requests
import json

import irc.bot
from influxdb import InfluxDBClient
from threading import Thread


emotes = ['VoteYea', 'NotATK', 'HassaanChop', 'PogChamp', 'DendiFace', 'ArigatoNas', 'RaccAttack', 'ArsonNoSexy', 'ShazBotstix', 'PermaSmug', 'Kreygasm', 'PJSalt', 'RedCoat', 'SoonerLater', 'StrawBeary', 'PanicVis', 'Kappa', 'DogFace', 'Kappu', 'MrDestructoid', 'OpieOP', 'UnSane', 'twitchRaid', 'copyThis', 'panicBasket', 'TBTacoProps', 'TBCrunchy', 'PipeHype', 'BigPhish', 'FailFish', 'TF2John', 'MVGame', 'KappaRoss', 'riPepperonis', 'TehePelo', 'HeyGuys', 'ResidentSleeper', 'TheThing', 'BloodTrail', 'CoolCat', 'DoritosChip', 'OSfrog', 'ArgieB8', 'ANELE', 'VaultBoy', 'SMOrc', 'WholeWheat', 'SuperVinlin', 'TTours', 'TwitchLit', 'PrimeMe', 'StoneLightning', 'BegWan', 'PRChase', 'BrokeBack', 'UWot', 'JonCarnage', 'YouWHY', 'BudStar', 'MikeHogu', 'InuyoFace', 'SeemsGood', 'ThankEgg', '4Head', 'GingerPower', 'EleGiggle', 'TwitchUnity', 'mcaT', 'StinkyCheese', 'DatSheffy', 'cmonBruh', 'PicoMause', 'CorgiDerp', 'TriHard', 'ItsBoshyTime', 'MingLee', 'PraiseIt', 'PJSugar', 'ShadyLulu', 'TBAngel', 'Keepo', 'OSsloth', 'WutFace', 'FunRun', 'OhMyDog', 'BJBlazkowicz', 'PMSTwin', 'JKanStyle', 'CrreamAwk', 'BuddhaBar', 'BlargNaut', 'AMPTropPunch', 'RlyTho', 'FrankerZ', 'SabaPing', 'PunOko', 'TinyFace', 'bleedPurple', 'BCWarrior', 'TheRinger', 'SSSsss', 'MorphinTime', 'TwitchRPG', 'KappaPride', 'imGlitch', 'SoBayed', 'OptimizePrime', 'KevinTurtle', 'TakeNRG', 'duDudu', 'DAESuppy', 'Mau5', 'BibleThump', 'CarlSmile', 'QuadDamage', 'KappaClaus', 'AsianGlow', 'GrammarKing', 'Jebaited', 'ChefFrank', 'VoteNay', 'NotLikeThis', 'CurseLit', 'DansGame', 'GivePLZ', 'NomNom', 'TheIlluminati', 'HumbleLife', 'BabyRage', 'Squid4', 'Squid1', 'Squid2', 'Squid3', 'FutureMan', 'FreakinStinkin', 'RalpherZ', 'WTRuck', 'HotPokket', 'VoHiYo', 'UncleNox', 'OSblob', 'PartyTime', 'YouDontSay', 'DBstyle', 'DxCat', 'BrainSlug', 'PeoplesChamp', 'BatChest', 'NinjaGrumpy', 'Poooound', 'KappaWealth', 'SmoocherZ', 'OSkomodo', 'OneHand', 'TheTarFu', 'GOWSkull', 'BigBrother', 'CoolStoryBob', 'TooSpicy', 'pastaThat', 'RitzMitz', 'SwiftRage', 'FUNgineer', 'TBTacoBag', 'RuleFive', 'BlessRNG', 'KAPOW', 'KonCha', 'PunchTrees', 'TearGlove', 'HassanChop', 'Kippa', 'ThunBeast']

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# print color.BOLD + 'Hello World !' + color.END


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.influx_host = 'influxdb'
        self.influx_user = 'root'
        self.influx_pass = 'root'

        # Initialize InfluxDb
        self.influx = self._influx_init()

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print 'Connecting to ' + color.BOLD + server + color.END + ' on port ' + str(port) + '...'
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)


    def on_welcome(self, c, e):
        print 'Joining ' + color.BOLD + self.channel + color.END

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        for emote in emotes:
            if emote in e.arguments[0].split(' '):
                print 'Recieved ' + emote + ': ' + color.BOLD + self.channel + color.END
                json_body = [
                    {
                        "measurement": "emotes",
                        "tags": {
                            "channel": self.channel[1:],
                            "emote": emote
                        },
                        "fields": {
                            "value": 1.0
                        }
                    }
                ]
                self.influx.write_points(json_body)
        return

    def _get_emotes(self):
            # TODO grab those emotes
            # https://twitchemotes.com/api_cache/v3/global.json

            # TODO tag the sub ones
        pass

    def _influx_init(self):
        db_name = "twitch"
        channel = self.channel[1:]
        client = InfluxDBClient(self.influx_host, 8086, self.influx_user, self.influx_pass)
        dbs = client.get_list_database()
        dbs = [ name['name'] for name in dbs ]
        # Create the database if it doesn't exist
        if not db_name in dbs:
            client.create_database(db_name)
        client.switch_database(db_name)
        return client

        pass

    def get_top_games(self):
        url = "https://api.twitch.tv/kraken/games/top"

        headers = {
        'client-id': self.client_id,
        'accept': "application/vnd.twitchtv.v5+json",
        }

        response = requests.request("GET", url, headers=headers)
        response = json.loads(response.text)
        self.top_games = [ data['game']['name'] for data in response['top'] ]
        print self.top_games

    def get_top_channels(self, game):
        url = "https://api.twitch.tv/kraken/streams"

        querystring = {"game":game}

        headers = {
        'client-id': self.client_id,
        'accept': "application/vnd.twitchtv.v5+json",
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response = json.loads(response.text)
        top_channels = [ data['channel']['name'] for data in response['streams'] ]
        return top_channels


    def influx_write(self, body):
        pass

    def do_command(self, e, cmd):
        c = self.connection

        # Poll the API to get current game.
        # if cmd == "game":
        #     url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
        #     headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        #     r = requests.get(url, headers=headers).json()
        #     c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])
        #
        # # Poll the API the get the current status of the stream
        # elif cmd == "title":
        #     url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
        #     headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        #     r = requests.get(url, headers=headers).json()
        #     c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])

def get_top_games(client_id):
    url = "https://api.twitch.tv/kraken/games/top"

    headers = {
    'client-id': client_id,
    'accept': "application/vnd.twitchtv.v5+json",
    }

    response = requests.request("GET", url, headers=headers)
    response = json.loads(response.text)
    top_games = [ data['game']['name'] for data in response['top'] ]
    return top_games

def get_top_channels(client_id, game):
    url = "https://api.twitch.tv/kraken/streams"

    querystring = {"game":game}

    headers = {
    'client-id': client_id,
    'accept': "application/vnd.twitchtv.v5+json",
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response = json.loads(response.text)
    top_channels = [ data['channel']['name'] for data in response['streams'] ]
    return top_channels

def main():
    # if len(sys.argv) != 5:
    #     print("Usage: twitchbot <username> <client id> <token> <channel>")
    #     sys.exit(1)

    username = 'emote_listener'
    client_id = os.getenv('TWITCH_CLIENT_ID')
    token = os.getenv('OAUTH_TOKEN')
    # username  = sys.argv[1]
    # client_id = sys.argv[2]
    # token     = sys.argv[3]
    # channel   = sys.argv[4]

    # bot = TwitchBot(username, client_id, token, channel)
    top_games = get_top_games(client_id)
    for game in top_games:
        print "Getting channels for {}".format(game)
        channels = get_top_channels(client_id, game)
        for channel in channels:
            Thread(target = TwitchBot(username, client_id, token, channel).start).start()

    # bot.start()

if __name__ == "__main__":
    main()
