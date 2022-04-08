# Standard
import discord
from discord.commands import slash_command, Option
from discord.ext import commands
from difflib import get_close_matches
from datetime import datetime, timedelta

# Local
from utils.json_loader import *
from utils.view import *
from utils.cache import *
from utils.emoji import *
from utils.auth import Auth
from utils.api_endpoint import VALORANT_API
from utils.embed import embed_design_giorgio, night_embed
from utils.useful import get_item_battlepass, calculate_level_xp

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
        
        embed.description = f'{str(error)[:2000]}'
        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(description="See what's on your daily store")
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
        
        embed = discord.Embed(color=0xfd4554)
        embed.description = f"Daily store for **{riot_name}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=skin_list['duration'])), 'R')}"

        embed1 = embed_design_giorgio(skin_list['skin1'])
        embed2 = embed_design_giorgio(skin_list['skin2'])
        embed3 = embed_design_giorgio(skin_list['skin3'])
        embed4 = embed_design_giorgio(skin_list['skin4'])

        await ctx.respond(embeds=[embed, embed1, embed2, embed3, embed4])

    @slash_command(description="Log in with your Riot acoount")
    async def login(self, ctx, username: Option(str, "Input username"), password: Option(str, "Input password")):        
        create_json('users', {})

        auth = Auth(username, password, str(ctx.author.id))
        login = auth.authenticate()
        
        if login['auth'] == 'response':
            await ctx.defer(ephemeral=True)

            auth.get_entitlements_token()
            auth.get_userinfo()
            auth.get_region()

            data = data_read('users')
            embed = discord.Embed(color=0xfd4554, description='Successfully logged in as **{}**!'.format(data[str(ctx.author.id)]['IGN']))
            await ctx.respond(embed=embed)
        
        elif login['auth'] == '2fa':
            error = login['error']
            modal = TwoFA_UI(ctx, error)
            await ctx.send_modal(modal)
        else:
            raise commands.UserInputError('Your username or password may be incorrect!')
                    
    @slash_command(name='logout', description="Logout and Delete your account")
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
            
    @slash_command(description="Set a notification when a specific skin is available on your store")
    async def notify(self, ctx, skin: Option(str, "The name of the skin you want to notify")):
        await ctx.defer()
        # get_user

        user_id = ctx.author.id
        Auth(user_id=user_id).get_users()

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
            name = skin_source['name']
            icon = skin_source['icon']
            uuid = skin_source['uuid']
            
            emoji = get_emoji_tier(skin_uuid)

            for skin in notify_data:
                author = skin['id']
                uuid = skin['uuid']
                if author == str(user_id) and uuid == skin_uuid:
                    raise RuntimeError(f'{emoji} **{name}** is already in your Notify')

            data_add = {
                "id": str(ctx.author.id),
                "uuid": skin_uuid,
                "channel_id": ctx.channel.id
            }

            notify_data.append(data_add)

            data_save('notifys', notify_data)

            embed = discord.Embed(description=f'Successfully set an notify for the {emoji} **{name}**', color=0xfd4554)
            embed.set_thumbnail(url=icon)
            
            view = Notify(ctx.author.id, uuid, name)
            view.message = await ctx.respond(embed=embed, view=view)
            return
        
        raise RuntimeError("Not found skin")

    @slash_command(description="View skins you have set a notification for")
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
    
    @slash_command(description="Change notification mode")
    async def notify_mode(self, ctx, mode: Option(str, "Choose notify mode (default = Specified)", choices=['Specified Skin','All Skin','Off'])):
        
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
        
        if mode == 'Specified Skin':
            config = config_read()
            config["notify_mode"] = 'Specified'
            config_save(config)

            embed.title = "**Changed notify mode** - Specified"
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

    @slash_command(description="View your remaining Valorant and Riot Points (VP/RP)")
    async def point(self, ctx):

        await ctx.defer()
        user_id = ctx.author.id
        data = Auth(user_id=user_id).get_users()

        balances = get_valorant_point(str(user_id))

        try:
            balances = get_valorant_point(str(user_id))
            vp = balances["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            rad = balances["e59aa87c-4cbf-517a-5983-6e81511be9b7"]            
        except:
            raise commands.UserInputError("Can't fetch point")

        embed = discord.Embed(title=f"{data['IGN']} Points:",color=0xfd4554)
        embed.add_field(name='Valorant Points',value=f"{points['vp']} {vp}", inline=True)
        embed.add_field(name='Radianite points',value=f"{points['rad']} {rad}", inline=True)

        await ctx.respond(embed=embed)

    @slash_command(description="View your daily/weekly mission progress")
    async def mission(self, ctx):
        await ctx.defer()

        user = Auth(user_id=ctx.author.id).get_users()

        data = VALORANT_API(str(ctx.author.id)).fetch_contracts()
        mission = data["Missions"]

        def iso_to_time(iso):
            timestamp = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S%z").timestamp()
            time = datetime.utcfromtimestamp(timestamp)
            return time

        weekly = []
        daily = []
        daily_end = ''

        weekly_end = data['MissionMetadata']['WeeklyRefillTime']

        def get_mission_by_id(ID):
            data = data_read('missions')
            mission = data['missions'][ID]
            return mission
        
        for m in mission:
            mission = get_mission_by_id(m['ID'])
            *complete, = m['Objectives'].values()
            title = mission['title']
            progress = mission['progress']
            xp = mission['xp']
    
            format_m = f"\n{title} | + {xp:,} XP\n- {complete[0]}/{progress}"

            if mission['type'] == 'EAresMissionType::Weekly':
                weekly.append(format_m)
            if mission['type'] == 'EAresMissionType::Daily':
                daily_end = m['ExpirationTime']
                daily.append(format_m)

        daily_format = ''.join(daily)
        weekly_format = ''.join(weekly)
        embed = discord.Embed(title=f"**Missions** | {user['IGN']}", color=0xfd4554)
        embed.add_field(name='**Daily Missions**', value=f"{daily_format}\nEnd(s) at {format_dt(iso_to_time(daily_end), 'R')}", inline=False)
        embed.add_field(name='**Weekly Missions**', value=f"{weekly_format}\nRefills {format_dt(iso_to_time(weekly_end), 'R')}", inline=False)

        await ctx.respond(embed=embed)

    @slash_command(name="nightmarket", description="See what's on your Night.Market")
    async def night(self, ctx, username: Option(str, "Input username (temp login)", required=False), password: Option(str, "Input password (temp login)", required=False)):
        
        is_private = False
        if username is not None or password is not None:
            is_private = True
        await ctx.defer(ephemeral=is_private)
        
        try:
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
            
            data = Auth(user_id=ctx.author.id).get_users()
            riot_name = data['IGN']
            nightmarket, duration = VALORANT_API(str(ctx.author.id)).store_fetch_nightmarket()
                
            embed = discord.Embed(color=0xfd4554)
            embed.description = f"**NightMarket for {riot_name}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=duration)), 'R')}"

            skin1 = nightmarket['skin1']
            skin2 = nightmarket['skin2']
            skin3 = nightmarket['skin3']
            skin4 = nightmarket['skin4']
            skin5 = nightmarket['skin5']
            skin6 = nightmarket['skin6']
            
            embed1 = night_embed(skin1['uuid'], skin1['name'], skin1['price'], skin1['disprice'])
            embed2 = night_embed(skin2['uuid'], skin2['name'], skin2['price'], skin2['disprice'])
            embed3 = night_embed(skin3['uuid'], skin3['name'], skin3['price'], skin3['disprice'])
            embed4 = night_embed(skin4['uuid'], skin4['name'], skin4['price'], skin4['disprice'])
            embed5 = night_embed(skin5['uuid'], skin5['name'], skin5['price'], skin5['disprice'])
            embed6 = night_embed(skin6['uuid'], skin6['name'], skin6['price'], skin6['disprice'])
            
            await ctx.respond(embeds=[embed, embed1, embed2, embed3, embed4, embed5, embed6])
        except:
            raise RuntimeError("._. NO NIGHT MARKET")

    @slash_command(description="View your battlepass' current tier")
    async def battlepass(self, ctx):
        await ctx.defer()

        user = Auth(user_id=ctx.author.id).get_users()
        api = VALORANT_API(str(ctx.author.id))

        data_contracts = data_read('contracts')
        data_contracts['contracts'].pop('version')
        user_contracts = api.fetch_contracts()
        season = api.get_active_season()
        season_id = season['data']

        uuid = [x for x in data_contracts['contracts'] if data_contracts['contracts'][x]['reward']['relationUuid'] == season_id] #if data_contracts['contracts'][x]['reward']['relationUuid'] == season_id
        
        if uuid:
            battlepass = [x for x in user_contracts['Contracts'] if x['ContractDefinitionID'] == uuid[0]]
            level = battlepass[0]['ProgressionLevelReached']
            TOTAL_XP = battlepass[0]['ProgressionTowardsNextLevel']
            REWARD = data_contracts['contracts'][uuid[0]]['reward']['chapters']
            ACT_NAME = data_contracts['contracts'][uuid[0]]['name']

            BTP_level = {}

            count = 0
            for lvl in REWARD:
                for rw in lvl["levels"]:
                    count += 1
                    BTP_level[count] = rw['reward']
            
            next_reward = level + 1
            if level == 55: next_reward = 55

            current = BTP_level[next_reward]
            
            item = get_item_battlepass(current['type'], current['uuid'])
            if item["success"]:
                item_name = item['data']['name']
                item_type = item['data']['type']
                embed = discord.Embed(
                    title=f"BATTLE PASS | {user['IGN']}",
                    description = f"**Next Reward:** {item_name}\n**Type:** {item_type}\n**XP:** {TOTAL_XP:,}/{calculate_level_xp(level + 1):,}",
                    color=0xfd4554
                )    
    
                if item['data']['icon']:
                    if item['data']['type'] in ['Player Card', 'Skin', 'Spray']:
                        embed.set_image(url=item['data']['icon'])
                    else:
                        embed.set_thumbnail(url=item['data']['icon'])
                
                if level >= 50:
                    embed.color = 0xf1b82d

                if level == 55:
                    embed.description = f'{item_name}'

                embed.set_footer(text=f'TIER {level} | {ACT_NAME}')
            
            await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(valorant(bot))