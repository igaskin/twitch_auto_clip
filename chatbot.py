'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import sys
import requests
import json

import irc.bot
from influxdb import InfluxDBClient

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print 'Connecting to ' + server + ' on port ' + str(port) + '...'
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)

        # Initialize InfluxDb
        self.influx = self._influx_init()


    def on_welcome(self, c, e):
        print 'Joining ' + self.channel

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print 'Received command: ' + cmd
            self.do_command(e, cmd)
        if 'PogChamp' in e.arguments[0].split(' '):
            print 'Recieved Poggeers: \n' + e.arguments[0]
            json_body = [
                {
                    "measurement": "emotes",
                    "tags": {
                        "channel": self.channel[1:],
                        "emote": "PogChamp" # Make this dynamic
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

            # TODO tag the sub ones
        pass

    def _influx_init(self):
        db_name = "twitch"
        channel = self.channel[1:]
        client = InfluxDBClient('localhost', 8086, 'root', 'root')
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


def main():
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)

    username  = sys.argv[1]
    client_id = sys.argv[2]
    token     = sys.argv[3]
    channel   = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.get_top_games()
    # TODO poll for current top channels
    # with open('top_channels.txt', 'w') as f:
    #     for game in bot.top_games:
    #         print "Top channels for {}".format(game)
    #         channels = bot.get_top_channels(game)
    #         for channel in channels:
    #             f.write(channel + '\n')

    bot.start()

if __name__ == "__main__":
    main()
