<h1 align="center">
  <br>
  <a href="https://github.com/staciax/ValorantStoreChecker-discord-bot"></a>
  <br>
  Valorant Discord Bot
  <br>
</h1>

<h4 align="center">Store, Nightmarket, Battlepass, Mission, Bundle, Notify</h4>

<p align="center">
  <a href="https://discord.gg/RaCzsPnfNM">
      <img src="https://discordapp.com/api/guilds/887274968012955679/widget.png" alt="Support Server">
    </a>
  <a href="https://github.com/staciax/ValorantStoreChecker-discord-bot">
     <img src="https://img.shields.io/github/v/release/staciax/ValorantStoreChecker-discord-bot" alt="release">
  </a>
  <a href="https://github.com/Rapptz/discord.py/">
     <img src="https://img.shields.io/badge/discord-py-blue.svg" alt="discord.py">
  </a>
    <a title="Crowdin" target="_blank" href="https://crowdin.com/project/discord-bot-valorant"><img src="https://badges.crowdin.net/discord-bot-valorant/localized.svg">
 </a>
 <a href="https://github.com/staciax/ValorantStoreChecker-discord-bot/blob/master/LICENSE">
     <img src="https://img.shields.io/github/license/staciax/ValorantStoreChecker-discord-bot" alt="License">

</p>

<p align="center">
  <a href="#about">About</a>
  •
  <a href="#installations">Installations</a>
  •
  <a href="#screenshot">Screenshot</a>
  •
  <a href="#usage">Usage</a>
  •
  <a href="#translations">Translations</a>
  •
  <a href="#special-thanks">Special Thanks</a>
  •
  <a href="#support-me">Support</a>
</p>

<!-- Inspired by Red Discord Bot -->
<!-- https://github.com/Cog-Creators/Red-DiscordBot -->

# About

Discord bot that shows your infomation and more without open the VALORANT by using
the [In-game API.](https://github.com/HeyM1ke/ValorantClientAPI)
written using Python and the [Discord.py](https://github.com/Rapptz/discord.py) library <br>
For support using Valorant Bot, please join the [support server](https://discord.gg/RaCzsPnfNM)

## Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

- [Youtube Tutorial](https://youtu.be/5ZFsEcDT8e4)

## Screenshot

* Embed Design by [Giorgio](https://github.com/giorgi-o)

![image](https://i.imgur.com/uF9THEa.png)
![image](https://i.imgur.com/ijjvQV3.png)
<details>
<summary>See more screenshots</summary>
<img src="https://i.imgur.com/GhzLBSr.png" alt="battlepass">
<img src="https://i.imgur.com/f0gXUoo.png" alt="nightmarket">
<img src="https://i.imgur.com/Q7q6tUU.png" alt="missions">
<img src="https://i.imgur.com/5jEZt3Z.png" alt="points">
</details>

## Installations

* [Python 3.8+](https://www.python.org/downloads/)

* [Git](https://git-scm.com/downloads)

* Install requirements

* **Create** the [discord bot](https://discord.com/developers/applications) and **Enable Privileged Gateway
  Intents** [`MESSAGE CONTENT INTENT`](https://i.imgur.com/TiiaYR9.png) then invite bot to server with
  scope [`applications.commands`](https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png)

* Clone/[Download](https://github.com/staciax/ValorantStoreChecker-discord-bot/archive/refs/heads/master.zip)

```
pip install -r requirements.txt
```

```
# manual install package
pip install git+https://github.com/Rapptz/discord.py@master
pip install requests
pip install python-dotenv
```

* Store discord bot token and owner ID
  in [.env](https://github.com/staciax/ValorantStoreChecker-discord-bot/blob/master/.env)

```
TOKEN='INPUT DISCORD TOKEN HERE'
OWNER_ID='INPUT YOUR DISCORD ID'
```

* Run the bot

```
python bot.py
```

* Slash Command is automatic global commands `(takes 1 hour to process.)`
* If you want to use commands in server right now `-sync guild` to sync the commands in your server.
* if you want remove commands in your server `-unsync guild` to remove server commands.
* You can remove global command `-unsync global` to remove global commands.

## Usage

| Command                       | Action                                                                                                     |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `/store`  | Shows your daily store |
| `/point`  | Shows your valorant point |
| `/login`  | Log in with your Riot acoount |
| `/logout`  | Logout your Riot acoount |
| `/misson`  | View your daily/weekly mission progress |
| `/nightmarket`  | Shows your nightmarket |
| `/battlepass`  | View your battlepass' current tier |
| `/bundle`  | inspect a specific bundle `credit by Giorgio` |
| `/bundles`  | Show the current featured bundles `credit by Giorgio` |
| `/cookies`  | Login to your account with a cookie, [How to cookies](https://github.com/giorgi-o/SkinPeek/wiki/How-to-get-your-Riot-cookies) `credit by Giorgio`, [video](https://youtu.be/cFMNHEHEp2A) |
| `/notify add`  | Set a notification when a specific skin is available on your store |
| `/notify list`  | View skins you have set a notification for |
| `/notify mode`  | Change notification mode `Specified skin` or `all skin` |
| `/notify test`  | Testing notification |
| `/notify channel`  | Change notification channel `DM Message` or `Channel(in server)` |
| `/debug`  | command for debug `emoji`, `skin price`,`cache` is not loaded |

<!-- ## Translations (credit by [giorgio](https://github.com/giorgi-o) -->

## Translations

If you want to use your language and would like help translate the bot, please do!

- Option 1

1. You can translate my crowdin project [here.](https://crowdin.com/project/discord-bot-valorant)

- Option 2 (inspiration by [giorgio](https://github.com/giorgi-o))

1. [Fork the repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
2. Look up the language code for your language [here](https://discord.com/developers/docs/reference#locales)
3. In the `languages` folder of your forked repo, copy `en-US.json` and rename it to your language code
4. Open that file and do the thing
5. Open a pull request

- Alternatively, you can just send me the JSON on discord and I'll upload it for you.

## Special Thanks

This project wouldn't have happened without.

- [HeyM1ke/ValorantClientAPI](https://github.com/RumbleMike/ValorantClientAPI)
  for providing a great API about Valorant!

- [colinhartigan/valclient.py](https://github.com/colinhartigan/valclient.py)
  for beautiful client endpoint

- [techchrism/valorant-api-docs](https://github.com/techchrism/valorant-api-docs/)
  for API docs documentation

- [Valorant-API.com](https://valorant-api.com/)
  for every skin names and images!

- [github/giorgi-o](https://github.com/giorgi-o)
  for always helping me and more!. ValoBot in JS [SkinPeek](https://github.com/giorgi-o/SkinPeek/)

- [Discord - Valorant App Developer ](https://discord.gg/a9yzrw3KAm)
  developer community for valorant api

- [Contributors](https://github.com/staciax/ValorantStoreChecker-discord-bot/graphs/contributors) <3 <3

- Thank you very much <3

### Support Me

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/staciax)

<a href="https://tipme.in.th/renlyx">
<img link="https://ko-fi.com/staciax" src="https://static.tipme.in.th/img/logo.f8267020b29b.svg" width="170" />
</a>
