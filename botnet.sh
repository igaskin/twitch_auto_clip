#!/bin/sh

while read CHANNEL; do
  python chatbot.py fartbox $TWITCH_CLIENT_ID $OAUTH_TOKEN $CHANNEL &
done <top_channels.txt

