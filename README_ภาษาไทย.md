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
  <a href="#about">เกี่ยวกับ</a>
  •
  <a href="#installations">วิธีติดตั่ง</a>
  •
  <a href="#screenshot">ภาพประกอบ</a>
  •
  <a href="#usage">คำสั่งและวิธีใช้งาน</a>
  •
  <a href="#translations">แปลภาษา</a>
  •
  <a href="#special-thanks">ขอบคุณ</a>
  •
  <a href="#support-me">สนับสนุนได้ที่</a>
</p>

<!-- Inspired by Red Discord Bot -->
<!-- https://github.com/Cog-Creators/Red-DiscordBot -->

# เกี่ยวกับ

ดิสคอร์ดบอทที่โชว์ข้อมูลภายในเกมโดยไม่ต้องเข้าเกม โดยใช้ [In-game API](https://github.com/HeyM1ke/ValorantClientAPI)
เขียนโดย Python และ ไลบรารี่ [Discord.py](https://github.com/Rapptz/discord.py) <br>
ต้องการความช่วยเหลือสามารถเข้ามาใน [เซิฟเวอร์ดิสคอร์ด](https://discord.gg/RaCzsPnfNM)

## Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

- [วีดีโอสอน](https://youtu.be/5ZFsEcDT8e4)

## ภาพประกอบ

* Embed Design by [Giorgio](https://github.com/giorgi-o)

![image](https://i.imgur.com/uF9THEa.png)
![image](https://i.imgur.com/ijjvQV3.png)
<details>
<summary>ภาพประกอบเพิ่มเติม</summary>
<img src="https://i.imgur.com/GhzLBSr.png" alt="battlepass">
<img src="https://i.imgur.com/f0gXUoo.png" alt="nightmarket">
<img src="https://i.imgur.com/Q7q6tUU.png" alt="missions">
<img src="https://i.imgur.com/5jEZt3Z.png" alt="points">
</details>

## วิธีติดตั่ง

* ดาวน์โหลด [Python 3.8+](https://www.python.org/downloads/)
  
* [**สร้างบอทดิสคอร์ด**](https://discord.com/developers/applications) และ เปิดใช้งาน **Privileged Gateway
  Intents** [`MESSAGE CONTENT INTENT`](https://i.imgur.com/TiiaYR9.png) จากนั้นเชิญบอทไปที่เซิร์ฟเวอร์ด้วย
  scope [`applications.commands`](https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png)

* [ดาวน์โหลดโปรเจคนี้](https://github.com/staciax/ValorantStoreChecker-discord-bot/archive/refs/heads/master.zip) และ
  รันสคริปตามข้างล่าง

```
pip install -r requirements.txt
```

```
# หรือจะติดตั่งแบบทีละอย่าง
pip install git+https://github.com/Rapptz/discord.py@master
pip install requests
pip install python-dotenv
```

* เก็บ Token และ Owner ID ในไฟล์  [.env](https://github.com/staciax/ValorantStoreChecker-discord-bot/blob/master/.env)
  และ กดบันทึกไฟล์ให้เรียบร้อย

```
TOKEN='ใส่โทเคนของบอท'
OWNER_ID='ใส่เลขไอดีของเรา'
```

* รันสคริปให้บอททำงาน

```
python bot.py
```

* คำสั่งทับ `/` จะใช้ได้ทุกเซิฟก็ต่อเมื่อรันบอทครบ 1 ชั่วโมง
* ถ้าหากต้องการใช้งานทันทีให้พิมพ์คำสั่ง `-sync guild` ในดิสคอร์ด
* หากต้องการลบคำสั่งให้พิมพ์คำสั่ง `-unsync guild` ในดิสคอร์ด (หรือกรณีคำสั่งซ้ำกัน 2 คำสั่ง)
* หรือต้องการลงคำสั่งทั่งหมด `-unsync global` และ `-unsync guild`

## คำสั่งและวิธีใช้งาน

| คำสั่ง                       | การทำงาน                                                                                                     |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `/store`  | ดูร้านค้ารายวัน |
| `/point`  | ดูจำนวนพอยท์ที่เหลือ |
| `/login`  | เข้าสู่ระบบด้วยบัญชี Riot |
| `/logout`  | ออกจากระบบและลบบัญชีของคุณจากฐานข้อมูล |
| `/misson`  | ดูความคืบหน้าเควสรายวัน/รายสัปดาห์ของคุณ |
| `/nightmarket`  | ดูตลาดกลางคืน |
| `/battlepass`  | ดูความคืบหน้าของ battlepass |
| `/bundle`  | ดูคอลเลคชั่นตามที่ระบุ `เครดิต Giorgio` |
| `/bundles`  | ดูคอลเลคชั่นพิเศษ `เครดิต Giorgio` |
| `/cookies`  | เข้าสู่ระบบด้วยคุกกี้ สำหรับบัญชีที่เชื่อม facebook/google [วิธีหาคุกกี้](https://github.com/giorgi-o/SkinPeek/wiki/How-to-get-your-Riot-cookies) `เครดิต Giorgio` |
| `/notify add`  | ตั้งค่าการแจ้งเตือนเมื่อมีสกินเข้ามาในร้านค้าของคุณ |
| `/notify list`  | ดูสกินที่คุณตั้งค่าไว้สำหรับการแจ้งเตือน |
| `/notify mode`  | เปลี่ยนโหมดแจ้งเตือน |
| `/notify test`  | ทดสอบแจ้งการเตือน |
| `/notify channel`  | เปลี่ยนแชแนลส่งแจ้งเตือน DM หรือ แชแนล(ในเซิฟเวอร์) |
| `/debug`  | คำสั่งแก้บัคต่างๆ เช่น `อีโมจิ`, `ราคาสกิน`,`แคช` ไม่โหลด |

<!-- ## Translations (credit by [giorgio](https://github.com/giorgi-o) -->

## แปลภาษา (บอทรองรับภษาไทยแล้ว)

ถ้าต้องการให้บอทรองรับภาษาอื่นทำตามขั้นตอนนี้

1. [Fork the repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
2. ค้นหารหัสภาษาสำหรับภาษาของคุณ [ที่นี่](https://discord.com/developers/docs/reference#locales)
3. ในโฟลเดอร์ "languages" ของ repo ที่ Fork ให้คัดลอก "en-US.json" และเปลี่ยนชื่อเป็นรหัสภาษาของคุณ
4. เปิดไฟล์นั้นและทำสิ่งนั้น
5. เปิด pull request หรือ สามารถส่งไฟล์มาที่ดิสคอร์ดส่วนตัวผมได้

หรือคุณสามารถส่ง JSON ผ่าน discord มาให้ผมได้นะครับ

หรือสามารถแปลได้ใน [Crowdin](https://crowdin.com/project/discord-bot-valorant)

## Special Thanks

- [Valorant Client API](https://github.com/RumbleMike/ValorantClientAPI) by [RumbleMike](https://github.com/RumbleMike)
  for providing a great API about Valorant!

- [Valorant-API.com](https://valorant-api.com/)
  for every skin names and images!

- [Giorgio](https://github.com/giorgi-o)
  for always helping me and more! <3

- [Discord - Valorant App Developer ](https://discord.gg/a9yzrw3KAm)
  by [MikeValorantLeaks](https://github.com/RumbleMike)
  developer community for valorant api

- [Contributors](https://github.com/staciax/ValorantStoreChecker-discord-bot/graphs/contributors) <3 <3

### สนับสนุนได้ที่

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/staciax)

<a href="https://tipme.in.th/renlyx">
<img link="https://ko-fi.com/staciax" src="https://static.tipme.in.th/img/logo.f8267020b29b.svg" width="170" />
</a>
