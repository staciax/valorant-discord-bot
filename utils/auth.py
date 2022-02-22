# Standard
import urllib3
from datetime import datetime

# Third
import aiohttp

# Local
from utils.useful import _extract_tokens, extract_tokens_from_url, _token_exp
from utils.json_loader import data_read, data_save, config_read
from datetime import datetime, timedelta

User_agent = 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)'

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Auth:
    def __init__(self, username=None, password=None, user_id=None):
        self.username = username
        self.password = password
        self.user_id = str(user_id)

    async def get_users(self):

        try:
            data = data_read('users')
            userdata = data[self.user_id]
        except (FileNotFoundError, KeyError):
            raise RuntimeError(f"you're not registered!, plz `/login` to register!") 
                
        return userdata

    async def remove_account(self):
        data = data_read('users')
        del data[self.user_id]
        data_save('users', data)

    async def authenticate(self):
        session = aiohttp.ClientSession()
        database = data_read('users')
        
        # prepare cookies for auth request    
        
        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': User_agent
        }
        
        r = await session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

        cookies = {}
        cookies['cookie'] = {}
        for cookie in r.cookies.items():
            cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        # get access token
        data = {"type": "auth", "username": self.username, "password": self.password}

        async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers) as r:
            for cookie in r.cookies.items():
                cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]
            data = await r.json()

        await session.close()
        
        if data['type'] == 'response':
            expiry_token = datetime.now() + timedelta(hours=1)

            response = _extract_tokens(data)
            cookies['rso'] = response[0]
            cookies['idt'] = response[1]

            expiry_token = datetime.now() + timedelta(minutes=59)
            cookies['expiry_token'] = int(datetime.timestamp(expiry_token))
            
            database[self.user_id] = cookies

            data_save('users', database)
            return {'auth': 'response'}
    
        elif data['type'] == 'multifactor':
            if r.status == 429:
                raise RuntimeError(f'Please wait a few minutes and try again.')
            
            database[self.user_id] = cookies
            database[self.user_id]['WaitFor2FA'] = int(datetime.timestamp(datetime.now()))
            data_save('users', database)
            if data['multifactor']['method'] == 'email':
                raise RuntimeError(f"**Riot sent a code to {data['multifactor']['email']}** `/2fa` to complete your login.")
            raise RuntimeError('**You have 2FA enabled!** use `/2fa` to enter your code.')
        raise RuntimeError('Your username or password may be incorrect!')

    async def get_entitlements_token(self):
        session = aiohttp.ClientSession()
        
        database = data_read('users')
        
        access_token = database[self.user_id]['rso']

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
            data = await r.json()
        
        try:
            entitlements_token = data['entitlements_token']
            database[self.user_id]['emt'] = entitlements_token
            data_save('users', database)
        except KeyError:
            raise RuntimeError(f'Cookies is expired, plz /login again!')  #{r.json()["message"]}

        await session.close()

    async def get_userinfo(self):
        session = aiohttp.ClientSession()
        database = data_read('users')
        
        access_token = database[self.user_id]['rso']
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
            data = await r.json()
        
        try:
            database[self.user_id]['puuid'] = data['sub']
            database[self.user_id]['IGN'] = data['acct']['game_name'] + '#' + data['acct']['tag_line']
            data_save('users', database)
        except KeyError:
            raise RuntimeError(f'An unknown error occurred, plz /login again')
        
        await session.close()

    async def get_region(self) -> str:
        session = aiohttp.ClientSession()
        database = data_read('users')
        access_token = database[self.user_id]['rso']
        token_id = database[self.user_id]['idt']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        body = {"id_token": token_id}

        async with session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body) as r:
            data = await r.json()
        
        try:
            database[self.user_id]['region'] = data['affinities']['live']
            data_save('users', database)
        except KeyError:
            raise RuntimeError(f'An unknown error occurred, plz /login again')
        await session.close()

    async def give2facode(self, twoFAcode):
        session = aiohttp.ClientSession()
        database = data_read('users')
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': User_agent
        }

        data = {
            "type": "multifactor",
            "code": twoFAcode,
            "rememberDevice": False
        }

        async with session.put('https://auth.riotgames.com/api/v1/authorization', headers=headers, json=data, cookies=database[self.user_id]['cookie']) as r:
            data = await r.json()
        await session.close()

        if data['type'] == 'response':
            for cookie in r.cookies.items():
                database[self.user_id]['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]
            
            del database[self.user_id]['WaitFor2FA']
            data_save('users', database)
            
            response = _extract_tokens(data)
            database[self.user_id]['rso'] = response[0]
            database[self.user_id]['idt'] = response[1]

            expiry_token = datetime.now() + timedelta(minutes=59)
            database[self.user_id]['expiry_token'] = int(datetime.timestamp(expiry_token))
            
            data_save('users', database)
            
            await self.get_entitlements_token()
            await self.get_userinfo()
            await self.get_region()
            return True
        return False

    async def redeem_cookies(self):
        session = aiohttp.ClientSession()
        database = data_read('users')
        
        async with session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            cookies=database[self.user_id]['cookie'],
            allow_redirects=False
        ) as r:
            data = await r.text()
        await session.close()
        accessToken = extract_tokens_from_url(data)
                
        database[self.user_id]["rso"] = accessToken
        expiry_token = datetime.now() + timedelta(minutes=59)
        database[self.user_id]['expiry_token'] = int(datetime.timestamp(expiry_token))

        data_save('users', database) 
        await self.get_entitlements_token()

    async def temp_auth(self):
        session = aiohttp.ClientSession()
        data = {
            'client_id': 'play-valorant-web-prod',
            'nonce': '1',
            'redirect_uri': 'https://playvalorant.com/opt_in',
            'response_type': 'token id_token',
            'scope': 'account openid',
        }
    
        headers = {'Content-Type': 'application/json', 'User-Agent': User_agent }
    
        await session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
    
        data = {
            'type': 'auth',
            'username': self.username,
            'password': self.password
        }
    
        async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers) as r:
            data = await r.json()
            
        response = _extract_tokens(data)
        
        access_token = response[0]
        id_token = response[1]
        expires_in = response[2]
    
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': User_agent 
        }
        async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
            data = await r.json()
        
        entitlements_token = data['entitlements_token']
    
        async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
            data = await r.json()
        
        user_id = data['sub']
        name = data['acct']['game_name']
        tagline = data['acct']['tag_line']
        IGN = f"{name}#{tagline}"
        headers['X-Riot-Entitlements-JWT'] = entitlements_token
    
        body = {"id_token": id_token}
    
        async with session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body) as r:
            data = await r.json()  
            region = data['affinities']['live']
        
        await session.close()
        return user_id, headers, region, IGN
        
    async def start(self):
        await self.authenticate()
        await self.get_entitlements_token()
        await self.get_userinfo()
        await self.get_region()