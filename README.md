# twitch_auto_clip
(Eventually) Automatically generates twitch clips

Currently this is a stupid monitoring stack to measure the rate of PogChamps in popular channels.  


# Requirements
- Docker
- python

# Usage

1) Start monitoring channels

```
$ export TWITCH_CLIENT_ID=<your-twitch-client-id>
$ export OAUTH_TOKEN=<your-oauth-token>
$ docker-compose up -d
$ ./botnet.sh
```

2) Open up grafana in a browser: http://localhost:3000/

3) Import the templated dashboard into grafana.  The JSON for the dashboard is in `grafana/emote_rate.json`

4) Profit
