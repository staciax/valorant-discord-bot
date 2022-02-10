# Standard 
import discord
from io import BytesIO

# Third
import requests
from PIL import Image, ImageDraw, ImageFont

def generate_image(skin_list):
    try:
        # background
        background = Image.open('assets/images/background.png')
        draw = ImageDraw.Draw(background)

        # font
        font = "assets/font/LEMONMILK-RegularItalic.otf"
        test_font = ImageFont.FreeTypeFont(font, 55)
        font_medium = ImageFont.FreeTypeFont(font, 50)
        color_text = '#ffffff'

        def limit_text(text):
            if len(text) > 20:
                text = text[:20] + "..."
            return text

        # SKIN 1
        try:
            skin_1 = skin_list['skin1']
            skin1_tier = requests.get(skin_1['tier'])
            skin1_tier_png = Image.open(BytesIO(skin1_tier.content)).resize([90, 90])
            background.paste(skin1_tier_png,(10, 10), skin1_tier_png)
            
            skin1 = requests.get(skin_1['icon'])
            skin1_png = Image.open(BytesIO(skin1.content)).rotate(-25, expand=1)
            background.paste(skin1_png,(100, 30), skin1_png)
            draw.text((710, 20), str(skin_1['price']), font=font_medium, fill=color_text)

            draw.text((20, 280), limit_text(skin_1['name']), font=test_font, fill=color_text)
        except:
            pass
        
        # SKIN 2
        try:
            skin_2 = skin_list['skin2']

            skin2_tier = requests.get(skin_2['tier'])
            skin2_tier_png = Image.open(BytesIO(skin2_tier.content)).resize([90, 90])
            background.paste(skin2_tier_png,(855, 10), skin2_tier_png)
            skin2 = requests.get(skin_2['icon'])
            skin2_png = Image.open(BytesIO(skin2.content)).rotate(-25, expand=1)
            background.paste(skin2_png,(980, 30), skin2_png)
            draw.text((1560, 20), str(skin_2['price']), font=font_medium, fill=color_text)
            draw.text((870, 280), limit_text(skin_2['name']), font=test_font, fill=color_text)
        except:
            pass

        # SKIN 3
        try:
            skin_3 = skin_list['skin3']
            skin3_tier = requests.get(skin_3['tier'])
            skin3_tier_png = Image.open(BytesIO(skin3_tier.content)).resize([90, 90])
            background.paste(skin3_tier_png,(10, 360), skin3_tier_png)
            skin3 = requests.get(skin_3['icon'])
            skin3_png = Image.open(BytesIO(skin3.content)).rotate(-25, expand=1)
            background.paste(skin3_png,(100, 360), skin3_png)
            draw.text((710, 370), str(skin_3['price']), font=font_medium, fill=color_text)
            draw.text((20, 635), limit_text(skin_3['name']), font=test_font, fill=color_text)
        except:
            pass

        # SKIN 4
        try:
            skin_4 = skin_list['skin4']
            skin4_tier = requests.get(skin_4['tier'])
            skin4_tier_png = Image.open(BytesIO(skin4_tier.content)).resize([90, 90])
            background.paste(skin4_tier_png,(855, 360), skin4_tier_png)
            skin4 = requests.get(skin_4['icon'])
            skin4_png = Image.open(BytesIO(skin4.content)).rotate(-25, expand=1)
            background.paste(skin4_png,(980, 360), skin4_png)
            draw.text((1560, 370), str(skin_4['price']), font=font_medium, fill=color_text)
            draw.text((870, 635), limit_text(skin_4['name']), font=test_font, fill=color_text)
        except: 
            pass

        # save file
        buffer = BytesIO()
        background.save(buffer, 'png')
        # background.show()
        buffer.seek(0)
        file=discord.File(buffer, filename='store-offers.png')
        return file
    except:
        raise RuntimeError('Image creation failed.')