# Standard
import discord
from discord.commands import slash_command, Option
from discord.ext import commands
from difflib import get_close_matches
from datetime import datetime, timedelta

# Local
from utils.auth import Auth
from utils.store import VALORANT_API
from utils.json_loader import data_read, data_save, config_read, config_save
from utils.useful import *
from utils.pillow import generate_image
from utils.view_notify import Notify, Notify_list

class valorant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
         
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'-{self.__class__.__name__}')

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        embed = discord.Embed(color=0xfe676e)
        
        if isinstance(error, discord.ApplicationCommandInvokeError):
            error = error.original
        else:
            error = f"An unknown error occurred, sorry"
        
        embed.description = f'{error}'
        await ctx.respond(embed=embed, ephemeral=True)
            
    @slash_command(description="Shows your daily store in your accounts")
    async def store(self, ctx, username: Option(str, "Input username (temp login)", required=False), password: Option(str, "Input password (temp login)", required=False)):
        
        is_private = False
        if username is not None or password is not None:
            is_private = True

        await ctx.defer(ephemeral=is_private)

        if username and password:
            puuid, headers, region, ign = Auth(username, password).temp_auth()

            # fetch_skin_for_quick_check
            try:
                skin_data = data_read('skins')
                if skin_data['prices']["version"] != self.bot.game_version:
                    fetch_price(region=region, headers=headers)
            except KeyError:
                fetch_price(region=region, headers=headers)

            skin_list = VALORANT_API().temp_store(puuid, headers, region)
            riot_name = ign

        elif username or password:
            raise commands.CommandError("An unknown error occurred, sorry")
        else:
            data = Auth(user_id=ctx.author.id).get_users()
            try:
                skin_data = data_read('skins')
                if skin_data['prices']["version"] != self.bot.game_version:
                    fetch_price(user_id=ctx.author.id)
            except KeyError:
                fetch_price(user_id=ctx.author.id)
            
            skin_list = VALORANT_API(str(ctx.author.id)).get_store_offer()

            riot_name = data['IGN']

        config = config_read()
        design = config['embed_design']
            
        if design == 'ꜱᴛᴀᴄɪᴀ.#7475':
            embed = pillow_embed(riot_name, ctx.author, skin_list['duration'])
            file = generate_image(skin_list)

            await ctx.respond(embed=embed, file=file)

        elif design == 'Giorgio#0609': # https://github.com/giorgi-o/
            try:
                embed = discord.Embed(color=0xfd4554)
                embed.description = f"Daily store for **{riot_name}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=skin_list['duration'])), 'R')}"

                skin1 = skin_list['skin1']
                skin2 = skin_list['skin2']
                skin3 = skin_list['skin3']
                skin4 = skin_list['skin4']

                embed1 = await embed_design_giorgio(ctx, skin1['uuid'], skin1['name'], skin1['price'], skin1['icon'])
                embed2 = await embed_design_giorgio(ctx, skin2['uuid'], skin2['name'], skin2['price'], skin2['icon'])
                embed3 = await embed_design_giorgio(ctx, skin3['uuid'], skin3['name'], skin3['price'], skin3['icon'])
                embed4 = await embed_design_giorgio(ctx, skin4['uuid'], skin4['name'], skin4['price'], skin4['icon'])

                await ctx.respond(embeds=[embed, embed1, embed2, embed3, embed4])
            except Exception as e:
                print(e)
                raise commands.CommandError("An unknown error occurred, sorry")
   
    @slash_command(description="Log in with your Riot acoount")
    async def login(self, ctx, username: Option(str, "Input username"), password: Option(str, "Input password")):
        await ctx.defer(ephemeral=True)
        
        create_json('users', {})

        auth = Auth(username, password, str(ctx.author.id))
        login = auth.authenticate()
        
        if login['auth'] == 'response':
            auth.get_entitlements_token()
            auth.get_userinfo()
            auth.get_region()

            data = data_read('users')
            embed = discord.Embed(color=0xfd4554, description='Successfully logged in as **{}**!'.format(data[str(ctx.author.id)]['IGN']))
            await ctx.respond(embed=embed)
        else:
            raise commands.UserInputError('Your username or password may be incorrect!')
                
    @slash_command(name='2fa', description="Enter your 2FA Code")
    async def twofa(self, ctx, code: Option(str, "Input 2FA Code ")):
        await ctx.defer(ephemeral=True)
        if len(code) > 6 or len(code) < 6:
            raise commands.UserInputError('You entered the code with more than 6 or less 6.')
    
        try:
            data = data_read('users')
            twoFA_timeout = data[str(ctx.author.id)]['WaitFor2FA'] 
            future = datetime.fromtimestamp(twoFA_timeout) + timedelta(minutes=5)
            if datetime.now() > future:
                remove_user(ctx.author.id)
                raise commands.UserInputError("**2FA Timeout!**, plz `/login` again")
        except (KeyError, FileNotFoundError):
            raise commands.UserInputError("if you're not registered! plz, `/login` to register")
    
        auth = Auth(user_id=str(ctx.author.id)).give2facode(str(code))
        
        if auth:
            data = data_read('users')
            embed = discord.Embed(description='Successfully logged in as **{}**!'.format(data[str(ctx.author.id)]['IGN']), color=0xfd4554)
            return await ctx.respond(embed=embed, ephemeral=True)
        raise commands.UserInputError('Invalid 2FA code!')
    
    @slash_command(name='logout', description="Logout and delete your accounts")
    async def logout(self, ctx):
        await ctx.defer(ephemeral=True)
        try:
            data = data_read('users')
            del data[str(ctx.author.id)]
            data_save('users', data)
            embed = discord.Embed(description='You have been logged out bot', color=0xfd4554)
            return await ctx.respond(embed=embed, ephemeral=True)
        except KeyError:
            raise commands.UserInputError("I can't logout you if you're not registered!")
        except Exception:
            raise commands.UserInputError("I can't logout you")
            
    @slash_command(description="Set an notify for when a particular skin is in your store")
    async def notify(self, ctx, skin: Option(str, "The name of the skin you want to notify")):
        await ctx.defer() 
        # get_user

        data = Auth(user_id=ctx.author.id).get_users()

        # check same skin

        #setup emoji
        await setup_emoji(ctx)

        create_json('notifys', [])

        skindata = data_read('skins')
        skindata['skins'].pop('version')
        name_list = [skindata['skins'][x]['name'] for x in skindata['skins']]
        
        skin_name = get_close_matches(skin, name_list, 1)

        if skin_name:
            notify_data = data_read('notifys')

            find_skin = [x for x in skindata['skins'] if skindata['skins'][x]['name'] == skin_name[0]]
            skin_uuid = find_skin[0]

            skin_source = skindata['skins'][skin_uuid]

            data_add = {
                "id": str(ctx.author.id),
                "uuid": skin_uuid,
                "channel_id": ctx.channel.id
            }

            notify_data.append(data_add)

            data_save('notifys', notify_data)

            emoji = get_tier_emoji(skin_uuid, self.bot)
            name = skin_source['name']
            icon = skin_source['icon']
            uuid = skin_source['uuid']

            embed = discord.Embed(description=f'Successfully set an notify for the {emoji} **{name}**', color=0xfd4554)
            embed.set_thumbnail(url=icon)
            
            view = Notify(ctx.author.id, uuid, name)
            view.message = await ctx.respond(embed=embed, view=view)
            return
        
        raise commands.UserInputError("Not found skin")

    @slash_command(description="Shows all your skin notify")
    async def notifys(self, ctx):
        await ctx.defer(ephemeral=True)
        
        Auth(user_id=ctx.author.id).get_users()
        
        try:
            skin_data = data_read('skins')
            if skin_data['prices']["version"] != self.bot.game_version:
                fetch_price(user_id=ctx.author.id)
        except KeyError:
            fetch_price(user_id=ctx.author.id)

        view = Notify_list(ctx)
        await view.start()
    
    @slash_command(description="Change notify mode")
    async def notify_mode(self, ctx, mode: Option(str, "Choose notify mode (default = Spectified)", choices=['Spectified Skin','All Skin','Off'])):
        
        await ctx.defer(ephemeral=True)

        Auth(user_id=ctx.author.id).get_users()
        data = data_read('users')

        try:
            skin_data = data_read('skins')
            if skin_data['prices']["version"] != self.bot.game_version:
                fetch_price(user_id=ctx.author.id)
        except KeyError:
            fetch_price(user_id=ctx.author.id)
        
        embed = discord.Embed(color=0xfd4554)
        if mode == 'Spectified Skin':
            config = config_read()
            config["notify_mode"] = 'Spectified'
            config_save(config)

            embed.title = "**Changed notify mode** - Spectified"
            embed.description = "Use `/notify` to add skins to the notify list."
            embed.set_image(url='https://i.imgur.com/RF6fHRY.png')

            await ctx.respond(embed=embed)
        
        elif mode == 'All Skin':
            config = config_read()
            config["notify_mode"] = 'All'
            config_save(config)

            config_save(config)
            data[str(ctx.author.id)]['channel'] = ctx.channel.id
            data_save('users', data)

            embed.title = "**Changed notify mode** - All"
            embed.description = f"**Set Channel:** {ctx.channel.mention} for all notify"
            embed.set_image(url='https://i.imgur.com/Gedqlzc.png')

            await ctx.respond(embed=embed)

        else:
            config = config_read()
            config["notify_mode"] = False
            config_save(config)
            embed.title = "**Changed notify mode** - Off"
            embed.description = 'turn off notify'

            await ctx.respond(embed=embed)

    @slash_command(description="Shows your valorant point in your accounts")
    async def point(self, ctx):

        await ctx.defer()
        
        data = Auth(user_id=ctx.author.id).get_users()
        user_id = str(ctx.author.id)

        balances = get_valorant_point(user_id)

        try:
            balances = get_valorant_point(user_id)
            vp = balances["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            rad = balances["e59aa87c-4cbf-517a-5983-6e81511be9b7"]            
        except:
            raise commands.UserInputError("Can't fetch point")

        embed = discord.Embed(title=f"{data['IGN']} Points:",color=0xfd4554)
        embed.add_field(name='Valorant Points',value=f"{await get_emoji_point(ctx, 'vp')} {vp}", inline=True)
        embed.add_field(name='Radianite points',value=f"{await get_emoji_point(ctx, 'rad')} {rad}", inline=True)

        await ctx.respond(embed=embed)

    @slash_command(name="nightmarket", description="Shows your nightmarket in your account")
    async def night(self, ctx, username: Option(str, "Input username (temp login)", required=False), password: Option(str, "Input password (temp login)", required=False)):
        
        is_private = False
        if username is not None or password is not None:
            is_private = True
        await ctx.defer(ephemeral=is_private)

        if username and password:
            puuid, headers, region, ign = Auth(username, password).temp_auth()

            # fetch_skin_for_quick_check
            try:
                skin_data = data_read('skins')
                if skin_data['prices']["version"] != self.bot.game_version:
                    fetch_price(region=region, headers=headers)
            except KeyError:
                fetch_price(region=region, headers=headers)

            nightmarket, duration = VALORANT_API().temp_night(puuid, headers, region)
            riot_name = ign
        elif username or password:
            raise commands.CommandError("An unknown error occurred, sorry")
        else:
            data = Auth(user_id=ctx.author.id).get_users()
            riot_name = data['IGN']
            nightmarket, duration = VALORANT_API(str(ctx.author.id)).store_fetch_nightmarket()
        
        async def night_embed(uuid, name, price, dpice):
            embed = discord.Embed(color=0x0F1923)
            embed.description = f"{await get_emoji_tier(ctx, uuid)} **{name}**\n{await get_emoji_point(ctx, 'vp')} {dpice} ~~{price}~~"
            embed.set_thumbnail(url=get_skin_icon(uuid))
            return embed
        
        try:
            embed = discord.Embed(color=0xfd4554)
            embed.description = f"**NightMarket for {riot_name}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=duration)), 'R')}"

            skin1 = nightmarket['skin1']
            skin2 = nightmarket['skin2']
            skin3 = nightmarket['skin3']
            skin4 = nightmarket['skin4']
            skin5 = nightmarket['skin5']
            skin6 = nightmarket['skin6']
            
            embed1 = await night_embed(skin1['uuid'],skin1['name'], skin1['price'], skin1['disprice'])
            embed2 = await night_embed(skin2['uuid'],skin2['name'], skin2['price'], skin2['disprice'])
            embed3 = await night_embed(skin3['uuid'],skin3['name'], skin3['price'], skin3['disprice'])
            embed4 = await night_embed(skin4['uuid'],skin4['name'], skin4['price'], skin4['disprice'])
            embed5 = await night_embed(skin5['uuid'],skin5['name'], skin5['price'], skin5['disprice'])
            embed6 = await night_embed(skin6['uuid'],skin6['name'], skin6['price'], skin6['disprice'])
            
            await ctx.respond(embeds=[embed, embed1, embed2, embed3, embed4, embed5, embed6])
        except Exception as e:
            print(e)
            raise commands.CommandError("An unknown error occurred, sorry")
    
def setup(bot):
    bot.add_cog(valorant(bot))