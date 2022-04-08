# Standard
import urllib3
from datetime import datetime

# Third
import requests

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

    def get_users(self):
        try:
            data = data_read('users')
            userdata = data[self.user_id]
        except (FileNotFoundError, KeyError):
            raise RuntimeError(f"you're not registered!, plz `/login` to register!") 
        

        config = config_read()
        if config['refresh_token'] is True:
            try:
                token_exp = userdata['expiry_token']
                if datetime.now() > datetime.fromtimestamp(token_exp):
                    self.refresh_token(userdata)
            except (FileNotFoundError, KeyError):
                raise RuntimeError(f"you're not registered!, plz `/login` to register!") 
    
        return userdata

    def refresh_token(self, userdata):
        try:
            self.redeem_cookies()
        except RuntimeError as e:
            if 'username' and 'password' in userdata:
                self.username = userdata['username']
                self.password = userdata['password']
                self.start()
                return
            self.remove_account()
            raise RuntimeError(f'{e}')

    def remove_account(self):
        data = data_read('users')
        del data[self.user_id]
        data_save('users', data)

    def authenticate(self):
        session = requests.session()
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
        
        r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

        cookies = {}
        cookies['cookie'] = r.cookies.get_dict()

        config = config_read()
        if config['store_password'] is True:
            cookies['username'] = self.username
            cookies['password'] = self.password

        # get access token
        data = {"type": "auth", "username": self.username, "password": self.password}
        r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
    
        for cookie in r.cookies.items():
            cookies['cookie'][cookie[0]] = cookie[1]
        
        session.close()
        
        if r.json()['type'] == 'response':
            expiry_token = datetime.now() + timedelta(hours=1)

            response = _extract_tokens(r.json())
            cookies['rso'] = response[0]
            cookies['idt'] = response[1]

            expiry_token = datetime.now() + timedelta(minutes=59)
            cookies['expiry_token'] = int(datetime.timestamp(expiry_token))
            
            database[self.user_id] = cookies

            data_save('users', database)
            return {'auth': 'response'}
    
        elif r.json()['type'] == 'multifactor':
            if r.status_code == 429:
                raise RuntimeError(f'Please wait a few minutes and try again.')
            
            database[self.user_id] = cookies
            database[self.user_id]['WaitFor2FA'] = int(datetime.timestamp(datetime.now()))
            data_save('users', database)

            WaitFor2FA = {"auth": "2fa"}
            if r.json()['multifactor']['method'] == 'email':
                WaitFor2FA['error'] = f"Riot sent a code to {r.json()['multifactor']['email']}"
                return WaitFor2FA
            WaitFor2FA['error'] = 'You have 2FA enabled!'
            return WaitFor2FA
        raise RuntimeError('Your username or password may be incorrect!')

    def get_entitlements_token(self):
        session = requests.session()
        database = data_read('users')
        
        access_token = database[self.user_id]['rso']

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
        
        try:
            entitlements_token = r.json()['entitlements_token']
            database[self.user_id]['emt'] = entitlements_token
            data_save('users', database)
        except KeyError:
            raise RuntimeError(f'Cookies is expired, plz /login again!')  #{r.json()["message"]}

        session.close()

    def get_userinfo(self):
        session = requests.session()
        database = data_read('users')
        
        access_token = database[self.user_id]['rso']
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})  
        try:
            database[self.user_id]['puuid'] = r.json()['sub']
            database[self.user_id]['IGN'] = r.json()['acct']['game_name'] + '#' + r.json()['acct']['tag_line']
            data_save('users', database)
        except KeyError:
            raise RuntimeError(f'An unknown error occurred, plz /login again')
        
        session.close()

    def get_region(self) -> str:
        session = requests.session()
        database = data_read('users')
        access_token = database[self.user_id]['rso']
        token_id = database[self.user_id]['idt']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        body = {"id_token": token_id}
        r = session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body)
        try:
            region = r.json()['affinities']['live']
            if region in ['latam','br']: region = 'na'
            database[self.user_id]['region'] = region
            data_save('users', database)
        except KeyError:
            raise RuntimeError(f'An unknown error occurred, plz /login again')
        session.close()

    def give2facode(self, twoFAcode):
        session = requests.session()
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

        r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers, cookies=database[self.user_id]['cookie'])
        session.close()
        
        if r.json()['type'] == 'response':
            for cookie in r.cookies.items():
                database[self.user_id]['cookie'][cookie[0]] = cookie[1]
            
            del database[self.user_id]['WaitFor2FA']
            data_save('users', database)
            
            response = _extract_tokens(r.json())
            database[self.user_id]['rso'] = response[0]
            database[self.user_id]['idt'] = response[1]

            expiry_token = datetime.now() + timedelta(minutes=59)
            database[self.user_id]['expiry_token'] = int(datetime.timestamp(expiry_token))
            
            data_save('users', database)
            
            self.get_entitlements_token()
            self.get_userinfo()
            self.get_region()

            data = data_read('users')
            player_name = data[self.user_id]['IGN']
        
            return {'auth': 'response', 'player': player_name}
        
        return {'auth': 'failed', 'error': 'Code is valid. Please login again'}

    def redeem_cookies(self):
        session = requests.session()
        database = data_read('users')
        r = session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            cookies=database[self.user_id]['cookie'],
            allow_redirects=False
        )

        accessToken = extract_tokens_from_url(r.text)
                
        database[self.user_id]["rso"] = accessToken
        expiry_token = datetime.now() + timedelta(minutes=59)
        database[self.user_id]['expiry_token'] = int(datetime.timestamp(expiry_token))

        data_save('users', database) 
        self.get_entitlements_token()

    def temp_auth(self):
        session = requests.session()
          
        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }
        
        headers = {'Content-Type': 'application/json', 'User-Agent': User_agent }
        
        r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

        data = {"type": "auth", "username": self.username, "password": self.password}
        r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
        
        if r.json()['type'] == 'response':
            data = r.json()
        elif r.json()['type'] == 'multifactor':
            raise RuntimeError("Quick check is not support 2FA, Please `/login` first !")
        else:
            raise RuntimeError('Your username or password may be incorrect!')

        response = _extract_tokens(data)

        headers = {'Authorization': f'Bearer {response[0]}'}
        r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
        entitlements_token = r.json()['entitlements_token']

        r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})            
        user_id = r.json()['sub']
        ign = r.json()['acct']['game_name'] + '#' + r.json()['acct']['tag_line']

        headers['X-Riot-Entitlements-JWT'] = entitlements_token
        
        body = {"id_token": response[1]}
        r = session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body)
    
        region = r.json()['affinities']['live']
        if region in ['latam','br']: region = 'na'

        session.close()
        return user_id, headers, region, ign
        
    def start(self):
        self.authenticate()
        self.get_entitlements_token()
        self.get_userinfo()
        self.get_region()