# Valorant store checker - Discord Bot
Discord bot that shows valorant your daily store by using the Ingame API.
written using Python and the [Pycord](https://github.com/Pycord-Development/pycord) library <br>

Tutorial : [Youtube](https://youtu.be/gYjzEuJh3Ms)

* [Support  2 factor authentication](https://i.imgur.com/3Rr6p3e.gif)

## Screenshot

![image](https://i.imgur.com/xPZ5vAu.gif)
![image](https://i.imgur.com/AV6Pj5d.png)
<br>

## Usage

| Command                       | Action                                                                                                     |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `store`  | Shows my daily store |

## Prerequisites

* [Python 3.6+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/download)

## Installations

* Install requirements
```
pip install -r requirements.txt
```
* Store discord bot token in .env and server id for slash command (if private server)
```
TOKEN=<bot token>
SERVER_ID=<your_server_id>
REGION=<your_region>
CHANNEL_LOOP= <channel_id> (if you want to loop)
```
* Run the bot
```
python bot.py
```

## Special thanks

### [Valorant Client API](https://github.com/RumbleMike/ValorantClientAPI) by [RumbleMike](https://github.com/RumbleMike)
for providing a great API about Valorant!

### [Valorant-API.com](https://valorant-api.com/)
for every skin names and images!