# https://github.com/floxay/python-riot-auth

import contextlib
import ctypes
import json
import ssl
import sys
import warnings
from base64 import urlsafe_b64decode
from collections.abc import Sequence
from secrets import token_urlsafe
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import aiohttp
import yarl

from .errors import (
    RiotAuthenticationError,
    RiotAuthError,
    RiotMultifactorError,
    RiotRatelimitError,
    RiotUnknownErrorTypeError,
    RiotUnknownResponseTypeError,
)

__all__ = (
    'RiotAuthenticationError',
    'RiotAuthError',
    'RiotMultifactorError',
    'RiotRatelimitError',
    'RiotUnknownErrorTypeError',
    'RiotUnknownResponseTypeError',
    'RiotAuth',
)


class RiotAuth:
    RIOT_CLIENT_USER_AGENT = token_urlsafe(111)
    CIPHERS13 = ':'.join(  # https://docs.python.org/3/library/ssl.html#tls-1-3
        (
            'TLS_CHACHA20_POLY1305_SHA256',
            'TLS_AES_128_GCM_SHA256',
            'TLS_AES_256_GCM_SHA384',
        )
    )
    CIPHERS = ':'.join((
        'ECDHE-ECDSA-CHACHA20-POLY1305',
        'ECDHE-RSA-CHACHA20-POLY1305',
        'ECDHE-ECDSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES128-GCM-SHA256',
        'ECDHE-ECDSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-ECDSA-AES128-SHA',
        'ECDHE-RSA-AES128-SHA',
        'ECDHE-ECDSA-AES256-SHA',
        'ECDHE-RSA-AES256-SHA',
        'AES128-GCM-SHA256',
        'AES256-GCM-SHA384',
        'AES128-SHA',
        'AES256-SHA',
        'DES-CBC3-SHA',  # most likely not available
    ))
    SIGALGS = ':'.join((
        'ecdsa_secp256r1_sha256',
        'rsa_pss_rsae_sha256',
        'rsa_pkcs1_sha256',
        'ecdsa_secp384r1_sha384',
        'rsa_pss_rsae_sha384',
        'rsa_pkcs1_sha384',
        'rsa_pss_rsae_sha512',
        'rsa_pkcs1_sha512',
        'rsa_pkcs1_sha1',  # will get ignored and won't be negotiated
    ))

    def __init__(self) -> None:
        self._auth_ssl_ctx = RiotAuth.create_riot_auth_ssl_ctx()
        self._cookie_jar = aiohttp.CookieJar()
        self.access_token: str | None = None
        self.scope: str | None = None
        self.id_token: str | None = None
        self.token_type: str | None = None
        self.expires_at: int = 0
        self.user_id: str | None = None
        self.entitlements_token: str | None = None

    @staticmethod
    def create_riot_auth_ssl_ctx() -> ssl.SSLContext:
        ssl_ctx = ssl.create_default_context()

        # https://github.com/python/cpython/issues/88068
        addr = id(ssl_ctx) + sys.getsizeof(object())
        ssl_ctx_addr = ctypes.cast(addr, ctypes.POINTER(ctypes.c_void_p)).contents

        libssl: ctypes.CDLL | None = None
        if sys.platform.startswith('win32'):
            for dll_name in (
                'libssl-3.dll',
                'libssl-3-x64.dll',
                'libssl-1_1.dll',
                'libssl-1_1-x64.dll',
            ):
                with contextlib.suppress(FileNotFoundError, OSError):
                    libssl = ctypes.CDLL(dll_name)
                    break
        elif sys.platform.startswith(('linux', 'darwin')):
            libssl = ctypes.CDLL(ssl._ssl.__file__)  # type: ignore

        if libssl is None:
            raise NotImplementedError(
                'Failed to load libssl. Your platform or distribution might be unsupported, please open an issue.'
            )

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1  # deprecated since 3.10
        ssl_ctx.set_alpn_protocols(['http/1.1'])
        ssl_ctx.options |= 1 << 19  # SSL_OP_NO_ENCRYPT_THEN_MAC
        libssl.SSL_CTX_set_ciphersuites(ssl_ctx_addr, RiotAuth.CIPHERS13.encode())
        libssl.SSL_CTX_set_cipher_list(ssl_ctx_addr, RiotAuth.CIPHERS.encode())
        # setting SSL_CTRL_SET_SIGALGS_LIST
        libssl.SSL_CTX_ctrl(ssl_ctx_addr, 98, 0, RiotAuth.SIGALGS.encode())

        # print([cipher["name"] for cipher in ssl_ctx.get_ciphers()])
        return ssl_ctx

    def __update(
        self,
        extract_jwt: bool = False,
        key_attr_pairs: Sequence[tuple[str, str]] = (
            ('sub', 'user_id'),
            ('exp', 'expires_at'),
        ),
        **kwargs: Any,
    ) -> None:
        # ONLY PREDEFINED PUBLIC KEYS ARE SET, rest is silently ignored!
        predefined_keys = [key for key in self.__dict__.keys() if key[0] != '_']

        self.__dict__.update((key, val) for key, val in kwargs.items() if key in predefined_keys)

        if extract_jwt:  # extract additional data from access JWT
            additional_data = self.__get_keys_from_access_token(key_attr_pairs)
            self.__dict__.update((key, val) for key, val in additional_data if key in predefined_keys)

    def __get_keys_from_access_token(
        self, key_attr_pairs: Sequence[tuple[str, str]]
    ) -> list[tuple[str, str | int | list[Any] | dict[str, Any] | None]]:  # List[Tuple[str, JSONType]]
        assert self.access_token is not None
        payload = self.access_token.split('.')[1]
        decoded = urlsafe_b64decode(f'{payload}===')
        temp_dict: dict[str, Any] = json.loads(decoded)
        return [(attr, temp_dict.get(key)) for key, attr in key_attr_pairs]

    def __set_tokens_from_uri(self, data: dict[str, Any]) -> None:
        mode = data['response']['mode']
        uri = data['response']['parameters']['uri']

        result = getattr(urlsplit(uri), mode)
        data = dict(parse_qsl(result))
        self.__update(extract_jwt=True, **data)

    async def __fetch_access_token(
        self,
        session: aiohttp.ClientSession,
        body: dict[str, Any],
        headers: dict[str, Any],
        data: dict[str, Any],
    ) -> bool:
        multifactor_status = False
        resp_type = data['type']

        if resp_type != 'response':  # not reauth
            async with session.put(
                'https://auth.riotgames.com/api/v1/authorization',
                json=body,
                headers=headers,
            ) as r:
                data = await r.json()
                resp_type = data['type']
                if resp_type == 'response':
                    ...
                elif resp_type == 'auth':
                    err = data.get('error')
                    if err == 'auth_failure':
                        raise RiotAuthenticationError(
                            f'Failed to authenticate. Make sure username and password are correct. `{err}`.'
                        )
                    elif err == 'rate_limited':
                        raise RiotRatelimitError()
                    else:
                        raise RiotUnknownErrorTypeError(f'Got unknown error `{err}` during authentication.')
                elif resp_type == 'multifactor':
                    multifactor_status = True
                else:
                    raise RiotUnknownResponseTypeError(
                        f'Got unknown response type `{resp_type}` during authentication.'
                    )

        self._cookie_jar = session.cookie_jar

        if not multifactor_status:
            self.__set_tokens_from_uri(data)
            await self.__fetch_entitlements_token(session)

        return multifactor_status

    async def __fetch_entitlements_token(self, session: aiohttp.ClientSession) -> None:
        headers = {
            'Accept-Encoding': 'deflate, gzip, zstd',
            # "user-agent": RiotAuth.RIOT_CLIENT_USER_AGENT % "entitlements",
            'user-agent': RiotAuth.RIOT_CLIENT_USER_AGENT,
            'Cache-Control': 'no-cache',
            'Accept': 'application/json',
            'Authorization': f'{self.token_type} {self.access_token}',
        }

        async with session.post(
            'https://entitlements.auth.riotgames.com/api/token/v1',
            headers=headers,
            json={},
            # json={"urn": "urn:entitlement:%"},
        ) as r:
            self.entitlements_token = (await r.json())['entitlements_token']

    async def authorize(self, username: str, password: str, use_query_response_mode: bool = False) -> bool:
        """
        Authenticate using username and password.
        """
        if username and password:
            self._cookie_jar.clear()

        conn = aiohttp.TCPConnector(ssl=self._auth_ssl_ctx)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=True, cookie_jar=self._cookie_jar) as session:
            headers = {
                'Accept-Encoding': 'deflate, gzip, zstd',
                # "user-agent": RiotAuth.RIOT_CLIENT_USER_AGENT % "rso-auth",
                'user-agent': RiotAuth.RIOT_CLIENT_USER_AGENT,
                'Cache-Control': 'no-cache',
                'Accept': 'application/json',
            }

            # region Begin auth/Reauth
            body = {
                'acr_values': '',
                'claims': '',
                'client_id': 'riot-client',
                'code_challenge': '',
                'code_challenge_method': '',
                'nonce': token_urlsafe(16),
                'redirect_uri': 'http://localhost/redirect',
                'response_type': 'token id_token',
                'scope': 'openid link ban lol_region account',
            }
            if use_query_response_mode:
                body['response_mode'] = 'query'
            async with session.post(
                'https://auth.riotgames.com/api/v1/authorization',
                json=body,
                headers=headers,
            ) as r:
                data: dict[str, Any] = await r.json()
            # endregion

            body = {
                'language': 'en_US',
                'password': password,
                'region': None,
                'remember': False,
                'type': 'auth',
                'username': username,
            }
            return await self.__fetch_access_token(session, body, headers, data)

    async def authorize_mfa(self, code: str) -> None:
        """
        Send the 2FA and finish authentication.
        """
        conn = aiohttp.TCPConnector(ssl=self._auth_ssl_ctx)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=True, cookie_jar=self._cookie_jar) as session:
            headers = {
                'Accept-Encoding': 'deflate, gzip, zstd',
                # "user-agent": RiotAuth.RIOT_CLIENT_USER_AGENT % "rso-auth",
                'user-agent': RiotAuth.RIOT_CLIENT_USER_AGENT,
                'Cache-Control': 'no-cache',
                'Accept': 'application/json',
            }
            body = {
                'type': 'multifactor',
                'rememberDevice': 'false',
                'code': code,
            }
            if await self.__fetch_access_token(session, body, headers, data={'type': 'multifactor'}):
                raise RiotMultifactorError('Auth with Multi-factor failed. Make sure 2FA code is correct.')

    async def reauthorize(self) -> bool:
        """
        Reauthenticate using cookies.

        Returns a ``bool`` indicating success or failure.
        """
        try:
            await self.authorize('', '')
            return True
        except RiotAuthenticationError:  # because credentials are empty
            return False

    # custom

    def get_ssid(self) -> str | None:
        url = yarl.URL('https://auth.riotgames.com')
        riot_cookies = self._cookie_jar.filter_cookies(url)
        if 'ssid' not in riot_cookies:
            return None
        return riot_cookies['ssid'].value
