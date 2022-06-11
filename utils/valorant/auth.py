import re
import ssl
import urllib3
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from requests.adapters import HTTPAdapter
from collections import OrderedDict

from .local import LocalErrorResponse, ResponseLanguage
from ..errors import AuthenticationError
from ..locale_v2 import ValorantTranslator

vlr_locale = ValorantTranslator()

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def _extract_tokens(data: str) -> str:
    """Extract tokens from data"""

    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response

def _extract_tokens_from_uri(URL: str) -> Optional[Tuple[str, Any]]:
    try:
        accessToken = URL.split("access_token=")[1].split("&scope")[0]
        tokenId = URL.split("id_token=")[1].split("&")[0]
        return accessToken, tokenId
    except IndexError:
        raise AuthenticationError('Cookies Invalid')

# ---------- CUSTOM SESSION ADAPTER ---------- #

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args: Any, **kwargs: Any) -> None:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

class Session(requests.Session):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Session, self).__init__(*args, **kwargs)
        self.mount('https://', TLSAdapter())
        self.headers = OrderedDict([('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'), ('Accept-Language', 'en-US,en;q=0.9'), ('Accept-Encoding', 'gzip, deflate, br')])

# -------------------- #

class Auth:

    def __init__(self) -> None:
        self.user_agent = 'RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)'
        
        self.locale_code = 'en-US' # default language
        self.response = {} # prepare response for local response

    def local_response(self) -> LocalErrorResponse:
        '''This function is used to check if the local response is enabled.'''
        self.response = LocalErrorResponse('AUTH', self.locale_code)
        return self.response

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """ This function is used to authenticate the user. """
        
        # language
        local_response = self.local_response()
        
        session = Session()

        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }
        
        headers = {'Content-Type': 'application/json', 'User-Agent': self.user_agent}
        
        r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
        
        cookies = {}
        cookies['cookie'] = r.cookies.get_dict()

        data = {"type": "auth", "username": username, "password": password, "remember": True}
    
        r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers) 
 
        # print('Response Status:', r.status)
        session.close()

        for cookie in r.cookies.items():
            cookies['cookie'][cookie[0]] = cookie[1]

        if r.json()['type'] == 'response':
            expiry_token = datetime.now() + timedelta(hours=1)

            response = _extract_tokens(r.json())
            access_token = response[0]
            token_id = response[1]

            expiry_token = datetime.now() + timedelta(minutes=59)
            cookies['expiry_token'] = int(datetime.timestamp(expiry_token))
            
            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}

        elif r.json()['type'] == 'multifactor':

            if r.status_code == 429:
                raise AuthenticationError(local_response.get('RATELIMIT', 'Please wait a few minutes and try again.'))
            
            label_modal = local_response.get('INPUT_2FA_CODE')
            WaitFor2FA = {"auth": "2fa", "cookie": cookies, 'label': label_modal}

            if r.json()['multifactor']['method'] == 'email':
                WaitFor2FA['message'] = f"{local_response.get('2FA_TO_EMAIL', 'Riot sent a code to')} {r.json()['multifactor']['email']}"
                return WaitFor2FA
            
            WaitFor2FA['message'] = local_response.get('2FA_ENABLE', 'You have 2FA enabled!')
            return WaitFor2FA

        raise AuthenticationError(local_response.get('INVALID_PASSWORD', 'Your username or password may be incorrect!'))

    def get_entitlements_token(self, access_token: str) -> Optional[str]:
        """ This function is used to get the entitlements token. """
        
        # language
        local_response = self.local_response()

        session = Session()
        
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
        
        session.close()
        try:
            entitlements_token = r.json()['entitlements_token']
        except KeyError:
            raise AuthenticationError(local_response.get('COOKIES_EXPIRED', 'Cookies is expired, plz /login again!'))
        else:
            return entitlements_token

    def get_userinfo(self, access_token: str) -> Tuple[str, str, str]:
        """ This function is used to get the user info. """

        # language
        local_response = self.local_response()

        session = Session()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
        
        session.close()
        try:
            puuid = r.json()['sub']
            name = r.json()['acct']['game_name']
            tag = r.json()['acct']['tag_line']
        except KeyError:
            raise AuthenticationError(local_response.get('NO_NAME_TAG', 'This user hasn\'t created a name or tagline yet.'))
        else:
            return puuid, name, tag
        
    def get_region(self, access_token: str, token_id: str) -> str:
        """ This function is used to get the region. """

        # language
        local_response = self.local_response()

        session = Session()
        
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        
        body = {"id_token": token_id}

        r = session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body)
        
        session.close()
        try:
            region = r.json()['affinities']['live']
        except KeyError:
            raise AuthenticationError(local_response.get('REGION_NOT_FOUND', 'An unknown error occurred, plz `/login` again'))
        else:
            return region 

    def give2facode(self, twoFAcode: str, cookies: Dict) -> Dict[str, Any]:
        """ This function is used to give the 2FA code. """

        # language
        local_response = self.local_response()
        
        session = Session()
        
        headers = {'Content-Type': 'application/json', 'User-Agent': self.user_agent}
        data = {"type": "multifactor", "code": twoFAcode, "rememberDevice": True}

        r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers, cookies=cookies['cookie'])
        
        session.close()
        if r.json()['type'] == 'response':
            cookies = {}
            cookies['cookie'] = r.cookies.get_dict()

            data = _extract_tokens(r.json())
            access_token = data[0]
            token_id = data[1]
            
            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}
        
        return {'auth': 'failed', 'error': local_response.get('2FA_INVALID_CODE')}

    def redeem_cookies(self, cookies: Dict) -> Tuple[Dict[str, Any], str, str]:
        """ This function is used to redeem the cookies. """

        # language
        local_response = self.local_response()

        # cookies = json.loads(cookies)

        session = Session()
        
        r = session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            cookies=cookies['cookie'],
            allow_redirects=False
        )

        if r.status_code != 303:
            raise AuthenticationError(local_response.get('COOKIES_EXPIRED'))
        
        if r.headers['Location'].startswith('/login'):
            raise AuthenticationError(local_response.get('COOKIES_EXPIRED'))

        old_cookie = cookies.copy()

        # NEW COOKIE
        cookies = {}
        cookies['cookie'] = old_cookie
        for cookie in r.cookies.items():
            cookies['cookie'][cookie[0]] = cookie[1]

        session.close()
        
        accessToken, tokenId = _extract_tokens_from_uri(r.json())
        entitlements_token = self.get_entitlements_token(accessToken)
                
        return cookies, accessToken, entitlements_token

    def temp_auth(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        
        authenticate = self.authenticate(username, password)
        if authenticate['auth'] == 'response':
            access_token = authenticate['data']['access_token']
            token_id = authenticate['data']['token_id']

            entitlements_token = self.get_entitlements_token(access_token)
            puuid, name, tag = self.get_userinfo(access_token)
            region = self.get_region(access_token, token_id)
            player_name = f'{name}#{tag}' if tag is not None and tag is not None else 'no_username'

            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}', 'X-Riot-Entitlements-JWT': entitlements_token}
            user_data = {'puuid': puuid, 'region': region, 'headers': headers, 'player_name': player_name}
            return user_data
        
        raise AuthenticationError(self.local_response().get('TEMP_LOGIN_NOT_SUPPORT_2FA'))

    # next update

    def login_with_cookie(self, cookies: Dict) -> Dict[str, Any]:
        """ This function is used to login with cookie. """

        # language
        local_response = ResponseLanguage('cookies', self.locale_code)
        
        session = Session()
        headers = {
            'cookie': cookies
        }
        r = session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            headers=headers,
            allow_redirects=False
        )
        if r.status_code != 303:
            raise AuthenticationError(local_response.get('FAILED'))

        session.close()
        
        # NEW COOKIE
        cookies = {}
        cookies['cookie'] = r.cookies.get_dict()
        accessToken, tokenID = _extract_tokens_from_uri(r.text)
        entitlements_token = self.get_entitlements_token(accessToken)

        data = {
            'cookies': cookies,
            'AccessToken': accessToken,
            'token_id': tokenID,
            'emt': entitlements_token
        }
        return data

    def refresh_token(self, cookies: Dict) -> Tuple[Dict[str, Any], str, str]:
        return self.redeem_cookies(cookies)
