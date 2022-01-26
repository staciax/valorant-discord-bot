# Standard 
import re
import asyncio

# Third
import requests

# reference by https://github.com/iancdev

class Auth:
    def __init__(self, username, password, message=None, interaction=None, bot=None):
        self.username = username
        self.password = password
        
        #for 2 factor authentication
        self.message = message
        self.interaction = interaction
        self.bot = bot

    async def authenticate(self):
        
        auth_error = 'An unknown error occurred, sorry'  
        
        try:
            session = requests.session()
            data = {
                'client_id': 'play-valorant-web-prod',
                'nonce': '1',
                'redirect_uri': 'https://playvalorant.com/opt_in',
                'response_type': 'token id_token',
            }

            headers = {
                'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)'
            }

            r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

            data = {
                'type': 'auth',
                'username': self.username,
                'password': self.password,
            }
                    
            r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

            # auth error handler
            if r.json()['type'] == 'auth':
                auth_error = 'Your username or password may be incorrect!'
            elif r.json()['type'] == 'multifactor':
                if self.message is not None and self.bot is not None and self.interaction is not None:
                    # 2fa error
                    auth_error = '2FA verify code may be incorrect!'
                    await self.message.edit('**Enter the 2FA verify code**')

                    try:
                        respond_message = await self.bot.wait_for("message", check=lambda msg: msg.author == self.interaction.user and msg.channel == self.interaction.channel, timeout=90)
                    except asyncio.TimeoutError:
                        auth_error = '2 factor authentication is Timeout.'
                    data = {
                        "type": "multifactor",
                        "code": respond_message.content,
                        "rememberDevice": False
                    }
                    await self.message.edit('\u200B')
                    await respond_message.delete()
                    r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
            
            pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
            data = pattern.findall(r.json()['response']['parameters']['uri'])[0] 
            access_token = data[0]
            # print('Access Token: ' + access_token)

            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
            entitlements_token = r.json()['entitlements_token']
            # print('Entitlements Token: ' + entitlements_token)

            r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})            
            user_id = r.json()['sub']
            # print('User ID: ' + user_id)
            headers['X-Riot-Entitlements-JWT'] = entitlements_token
            session.close()

            return user_id, headers
        except:
            raise RuntimeError(auth_error)