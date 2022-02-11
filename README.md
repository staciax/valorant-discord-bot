# Valorant store checker - Discord Bot (BETA)
Discord bot that shows your daily store offer without open the VALORANT by using the Ingame API.
written using Python and the [Pycord](https://github.com/Pycord-Development/pycord) library <br>

#### NEW UPDATE 
* `Notify skin, shows valorant point, Login, logout, more`
* [`Night Market (end 23/02/2022)`](https://i.imgur.com/n1KSay4.png)

## Screenshot

![image](https://i.imgur.com/I0rHtiM.png)
<br>
* Embed Design `-embed split` by [Giorgio#0609](https://github.com/giorgi-o)[`img`](https://i.imgur.com/qzrI0qF.png) | default : `-embed pillow` 

![image](https://i.imgur.com/J1Dptta.png)

* Notify skin

![image](https://i.imgur.com/ijjvQV3.png)

## Installations

* [Python 3.8+](https://www.python.org/downloads/)

* Install requirements

* Create the [discord bot](https://discord.com/developers/applications) and invite bot to server with scope `applications.commands`

* Clone/[Download](https://github.com/staciax/ValorantStoreChecker-discord-bot/archive/refs/heads/master.zip)

```
pip install -r requirements.txt
```

```
# manual install package

pip install pillow
pip install py-cord==2.0.0b4
pip install requests
```

* Store discord bot token in [config.json](https://github.com/staciax/ValorantStoreChecker-discord-bot/blob/master/config.json)
```
"TOKEN": "PUT YOUR DISCORD BOT TOKEN"
```
* Run the bot
```
python bot.py
```
* Slash Command in the global happens instantly `(takes 1 hour to process.)` | force global `-setup global`
* if you want use in server now `-setup guild` to setup the commands. | remove command `-unsetup guild`

## Usage

| Command                       | Action                                                                                                     |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `store`  | Shows your daily store |
| `point`  | Shows your valorant point |
| `login`  | Log in with your Riot acoount |
| `logout`  | Logout your Riot acoount |
| `2fa`  | Enter your 2FA Code |
| `notify`  | Set an notify for when a particular skin is in your store |
| `notifys`  | Shows all your skin notify |
| `notify_mode`  | Change notify mode `spectified skin` or `all skin` |
| `nightmarket`  | Shows your nightmarket |

## Special thanks

### [Valorant Client API](https://github.com/RumbleMike/ValorantClientAPI) by [RumbleMike](https://github.com/RumbleMike)
for providing a great API about Valorant!

### [Valorant-API.com](https://valorant-api.com/)
for every skin names and images!

### [Giorgio#0609](https://github.com/giorgi-o)
for embed design and helping me and more! <3

### [Discord - Valorant App Developer ](https://discord.gg/a9yzrw3KAm) by [MikeValorantLeaks](https://github.com/RumbleMike)
developer community for valorant api

### Support Me

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/staciax)