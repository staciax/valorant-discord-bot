# Standard 
import discord
from io import BytesIO

# Third
import requests
from PIL import Image, ImageDraw, ImageFont

def generate_image(skin):
    try:
        name, icon, price = skin

        # background
        background = Image.open('assets/images/background.png')
        draw = ImageDraw.Draw(background)

        # font
        font = "assets/font/LEMONMILK-RegularItalic.otf"
        font_small = ImageFont.FreeTypeFont(font, 30)
        font_medium = ImageFont.FreeTypeFont(font, 35)
        color_text = '#ffffff'

        # icon        
        skin1 = requests.get(icon[0])
        skin2 = requests.get(icon[1])
        skin3 = requests.get(icon[2])
        skin4 = requests.get(icon[3])

        # icon resize
        skin_length = 420
        skin_height = 120
        skin1_resize = Image.open(BytesIO(skin1.content)).resize((skin_length, skin_height))
        skin2_resize = Image.open(BytesIO(skin2.content)).resize((skin_length, skin_height))
        skin3_resize = Image.open(BytesIO(skin3.content)).resize((skin_length, skin_height))
        skin4_resize = Image.open(BytesIO(skin4.content)).resize((skin_length, skin_height))

        # icon paste and set position
        background.paste(skin1_resize,(25, 60), skin1_resize)
        background.paste(skin2_resize,(625, 60), skin2_resize)
        background.paste(skin3_resize,(25, 310), skin3_resize)
        background.paste(skin4_resize,(625, 310), skin4_resize)

        # price
        draw.text((500, 15), price[0], font=font_medium, fill=color_text)
        draw.text((1095, 15), price[1], font=font_medium, fill=color_text)
        draw.text((500, 263), price[2], font=font_medium, fill=color_text)
        draw.text((1095, 263), price[3], font=font_medium, fill=color_text)

        # name
        draw.text((15, 205), name[0], font=font_small, fill=color_text)
        draw.text((610, 205), name[1], font=font_small, fill=color_text)
        draw.text((15, 455), name[2], font=font_small, fill=color_text)
        draw.text((610, 455), name[3], font=font_small, fill=color_text)

        # save file
        buffer = BytesIO()
        background.save(buffer, 'png')
        # background.show()
        buffer.seek(0)
        file=discord.File(buffer, filename='store-offers.png')
        return file
    except:
        raise RuntimeError('Image creation failed.')