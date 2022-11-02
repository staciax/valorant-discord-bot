# from __future__ import annotations

# Standard
import json
import re
import ssl
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

# Third
import aiohttp
import urllib3
from multidict import MultiDict

from ..errors import AuthenticationError
from ..locale_v2 import ValorantTranslator

# Local
from .local import LocalErrorResponse, ResponseLanguage

vlr_locale = ValorantTranslator()

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _extract_tokens(data: str) -> str:
    """Extract tokens from data"""

    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response


def _extract_tokens_from_uri(url: str) -> Optional[Tuple[str, Any]]:
    try:
        access_token = url.split("access_token=")[1].split("&scope")[0]
        token_id = url.split("id_token=")[1].split("&")[0]
        return access_token, token_id
    except IndexError:
        raise AuthenticationError('Cookies Invalid')


# https://developers.cloudflare.com/ssl/ssl-tls/cipher-suites/

FORCED_CIPHERS = [
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-SHA256',
    'ECDHE-RSA-AES128-SHA',
    'ECDHE-RSA-AES256-SHA',
    'ECDHE-ECDSA-AES128-SHA256',
    'ECDHE-ECDSA-AES128-SHA',
    'ECDHE-ECDSA-AES256-SHA',
    'ECDHE+AES128',
    'ECDHE+AES256',
    'ECDHE+3DES',
    'RSA+AES128',
    'RSA+AES256',
    'RSA+3DES',
]


class ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.set_ciphers(':'.join(FORCED_CIPHERS))
        super().__init__(*args, **kwargs, cookie_jar=aiohttp.CookieJar(), connector=aiohttp.TCPConnector(ssl=ctx))


class Auth:
    RIOT_CLIENT_USER_AGENT = "RiotClient/60.0.6.4770705.4749685 rso-auth (Windows;10;;Professional, x64)"
    
    def __init__(self) -> None:
        self._headers: Dict = {
            'Content-Type': 'application/json',
            'User-Agent': Auth.RIOT_CLIENT_USER_AGENT,
            'Accept': 'application/json, text/plain, */*',
        }
        self.user_agent = Auth.RIOT_CLIENT_USER_AGENT

        self.locale_code = 'en-US'  # default language
        self.response = {}  # prepare response for local response

    def local_response(self) -> LocalErrorResponse:
        """This function is used to check if the local response is enabled."""
        self.response = LocalErrorResponse('AUTH', self.locale_code)
        return self.response

    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """This function is used to authenticate the user."""

        # language
        local_response = self.local_response()

        session = ClientSession()

        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }

        # headers = {'Content-Type': 'application/json', 'User-Agent': self.user_agent}

        r = await session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=self._headers)

        # prepare cookies for auth request
        cookies = {'cookie': {}}
        for cookie in r.cookies.items():
            cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        data = {"type": "auth", "username": username, "password": password, "remember": True}

        async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=self._headers) as r:
            data = await r.json()
            for cookie in r.cookies.items():
                cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        # print('Response Status:', r.status)
        await session.close()

        if data['type'] == 'response':
            expiry_token = datetime.now() + timedelta(hours=1)

            response = _extract_tokens(data)
            access_token = response[0]
            token_id = response[1]

            expiry_token = datetime.now() + timedelta(minutes=59)
            cookies['expiry_token'] = int(datetime.timestamp(expiry_token))

            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}

        elif data['type'] == 'multifactor':

            if r.status == 429:
                raise AuthenticationError(local_response.get('RATELIMIT', 'Please wait a few minutes and try again.'))

            label_modal = local_response.get('INPUT_2FA_CODE')
            WaitFor2FA = {"auth": "2fa", "cookie": cookies, 'label': label_modal}

            if data['multifactor']['method'] == 'email':
                WaitFor2FA[
                    'message'
                ] = f"{local_response.get('2FA_TO_EMAIL', 'Riot sent a code to')} {data['multifactor']['email']}"
                return WaitFor2FA

            WaitFor2FA['message'] = local_response.get('2FA_ENABLE', 'You have 2FA enabled!')
            return WaitFor2FA

        raise AuthenticationError(local_response.get('INVALID_PASSWORD', 'Your username or password may be incorrect!'))

    async def get_entitlements_token(self, access_token: str) -> Optional[str]:
        """This function is used to get the entitlements token."""

        # language
        local_response = self.local_response()

        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
            data = await r.json()

        await session.close()
        try:
            entitlements_token = data['entitlements_token']
        except KeyError:
            raise AuthenticationError(local_response.get('COOKIES_EXPIRED', 'Cookies is expired, plz /login again!'))
        else:
            return entitlements_token

    async def get_userinfo(self, access_token: str) -> Tuple[str, str, str]:
        """This function is used to get the user info."""

        # language
        local_response = self.local_response()

        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
            data = await r.json()

        await session.close()
        try:
            puuid = data['sub']
            name = data['acct']['game_name']
            tag = data['acct']['tag_line']
        except KeyError:
            raise AuthenticationError(local_response.get('NO_NAME_TAG', 'This user hasn\'t created a name or tagline yet.'))
        else:
            return puuid, name, tag

    async def get_region(self, access_token: str, token_id: str) -> str:
        """This function is used to get the region."""

        # language
        local_response = self.local_response()

        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        body = {"id_token": token_id}

        async with session.put(
            'https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body
        ) as r:
            data = await r.json()

        await session.close()
        try:
            region = data['affinities']['live']
        except KeyError:
            raise AuthenticationError(
                local_response.get('REGION_NOT_FOUND', 'An unknown error occurred, plz `/login` again')
            )
        else:
            return region

    async def give2facode(self, code: str, cookies: Dict) -> Dict[str, Any]:
        """This function is used to give the 2FA code."""

        # language
        local_response = self.local_response()

        session = ClientSession()

        # headers = {'Content-Type': 'application/json', 'User-Agent': self.user_agent}

        data = {"type": "multifactor", "code": code, "rememberDevice": True}

        async with session.put(
            'https://auth.riotgames.com/api/v1/authorization', headers=self._headers, json=data, cookies=cookies['cookie']
        ) as r:
            data = await r.json()

        await session.close()
        if data['type'] == 'response':
            cookies = {'cookie': {}}
            for cookie in r.cookies.items():
                cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

            uri = data['response']['parameters']['uri']
            access_token, token_id = _extract_tokens_from_uri(uri)

            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}

        return {'auth': 'failed', 'error': local_response.get('2FA_INVALID_CODE')}

    async def redeem_cookies(self, cookies: Dict) -> Tuple[Dict[str, Any], str, str]:
        """This function is used to redeem the cookies."""

        # language
        local_response = self.local_response()

        if isinstance(cookies, str):
            cookies = json.loads(cookies)

        session = ClientSession()

        if 'cookie' in cookies:
            cookies = cookies['cookie']

        async with session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play"
            "-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            cookies=cookies,
            allow_redirects=False,
        ) as r:
            data = await r.text()

        if r.status != 303:
            raise AuthenticationError(local_response.get('COOKIES_EXPIRED'))

        if r.headers['Location'].startswith('/login'):
            raise AuthenticationError(local_response.get('COOKIES_EXPIRED'))

        old_cookie = cookies.copy()

        new_cookies = {'cookie': old_cookie}
        for cookie in r.cookies.items():
            new_cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        await session.close()

        accessToken, tokenId = _extract_tokens_from_uri(data)
        entitlements_token = await self.get_entitlements_token(accessToken)

        return new_cookies, accessToken, entitlements_token

    async def temp_auth(self, username: str, password: str) -> Optional[Dict[str, Any]]:

        authenticate = await self.authenticate(username, password)
        if authenticate['auth'] == 'response':
            access_token = authenticate['data']['access_token']
            token_id = authenticate['data']['token_id']

            entitlements_token = await self.get_entitlements_token(access_token)
            puuid, name, tag = await self.get_userinfo(access_token)
            region = await self.get_region(access_token, token_id)
            player_name = f'{name}#{tag}' if tag is not None and tag is not None else 'no_username'

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-Riot-Entitlements-JWT': entitlements_token,
            }
            user_data = {'puuid': puuid, 'region': region, 'headers': headers, 'player_name': player_name}
            return user_data

        raise AuthenticationError(self.local_response().get('TEMP_LOGIN_NOT_SUPPORT_2FA'))

    # next update

    async def login_with_cookie(self, cookies: Dict) -> Dict[str, Any]:
        """This function is used to log in with cookie."""

        # language
        local_response = ResponseLanguage('cookies', self.locale_code)

        cookie_payload = f'ssid={cookies};' if cookies.startswith('e') else cookies

        self._headers['cookie'] = cookie_payload

        session = ClientSession()

        r = await session.get(
            "https://auth.riotgames.com/authorize"
            "?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in"
            "&client_id=play-valorant-web-prod"
            "&response_type=token%20id_token"
            "&scope=account%20openid"
            "&nonce=1",
            allow_redirects=False,
            headers=self._headers,
        )

        # pop cookie
        self._headers.pop('cookie')

        if r.status != 303:
            raise AuthenticationError(local_response.get('FAILED'))

        await session.close()

        # NEW COOKIE
        new_cookies = {'cookie': {}}
        for cookie in r.cookies.items():
            new_cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        accessToken, tokenID = _extract_tokens_from_uri(await r.text())
        entitlements_token = await self.get_entitlements_token(accessToken)

        data = {'cookies': new_cookies, 'AccessToken': accessToken, 'token_id': tokenID, 'emt': entitlements_token}
        return data

    async def refresh_token(self, cookies: Dict) -> Tuple[Dict[str, Any], str, str]:
        return await self.redeem_cookies(cookies)
