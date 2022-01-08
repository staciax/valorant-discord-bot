# Valorant store checker - Discord Bot
Discord bot that shows valorant your daily store by using the Ingame API.
written using Python and the [Pycord](https://github.com/Pycord-Development/pycord) library


## Screenshot

![image](https://i.imgur.com/gj5usTI.gif)
![image](https://i.imgur.com/RLMarRk.png)

## Usage

| Command                       | Action                                                                                                     |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `store`  | Shows my daily store |

## Prerequisites

* Python 3.6+

## Installations

* Install requirements
```
pip install -r requirements.txt
```
* Store discord bot token in .env and server id for slash command (if private server)
```
TOKEN=<bot token>
SLASH_SERVER_ID=<your_server_id>
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