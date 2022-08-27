from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from ..errors import DatabaseError
from .auth import Auth
from .cache import fetch_price
from .local import LocalErrorResponse
from .useful import JSON


def timestamp_utc() -> datetime:
    return datetime.timestamp(datetime.utcnow())


class DATABASE:
    _version = 1

    def __init__(self) -> None:
        """Initialize database"""
        self.auth = Auth()

    def insert_user(self, data: Dict) -> None:
        """Insert user"""
        JSON.save('users', data)

    def read_db(self) -> Dict:
        """Read database"""
        data = JSON.read('users')
        return data

    def read_cache(self) -> Dict:
        """Read database"""
        data = JSON.read('cache')
        return data

    def insert_cache(self, data: Dict) -> None:
        """Insert cache"""
        JSON.save('cache', data)

    async def is_login(self, user_id: int, response: Dict) -> Optional[Dict[str, Any]]:
        """Check if user is logged in"""

        db = self.read_db()
        data = db.get(str(user_id), None)

        login = False

        if data is None:
            raise DatabaseError(response.get('NOT_LOGIN'))
        elif login:
            return False
        return data

    async def login(self, user_id: int, data: dict, locale_code: str) -> Optional[Dict[str, Any]]:
        """Login to database"""

        # language
        response = LocalErrorResponse('DATABASE', locale_code)

        db = self.read_db()
        auth = self.auth

        auth_data = data['data']
        cookie = auth_data['cookie']['cookie']
        access_token = auth_data['access_token']
        token_id = auth_data['token_id']

        try:
            entitlements_token = await auth.get_entitlements_token(access_token)
            puuid, name, tag = await auth.get_userinfo(access_token)
            region = await auth.get_region(access_token, token_id)
            player_name = f'{name}#{tag}' if tag is not None and tag is not None else 'no_username'

            expiry_token = datetime.timestamp(datetime.utcnow() + timedelta(minutes=59))

            data = dict(
                cookie=cookie,
                access_token=access_token,
                token_id=token_id,
                emt=entitlements_token,
                puuid=puuid,
                username=player_name,
                region=region,
                expiry_token=expiry_token,
                notify_mode=None,
                DM_Message=True,
            )

            db[str(user_id)] = data

            self.insert_user(db)

        except Exception as e:
            print(e)
            raise DatabaseError(response.get('LOGIN_ERROR'))
        else:
            return {'auth': True, 'player': player_name}

    def logout(self, user_id: int, locale_code: str) -> Optional[bool]:
        """Logout from database"""

        # language
        response = LocalErrorResponse('DATABASE', locale_code)

        try:
            db = self.read_db()
            del db[str(user_id)]
            self.insert_user(db)
        except KeyError:
            raise DatabaseError(response.get('LOGOUT_ERROR'))
        except Exception as e:
            print(e)
            raise DatabaseError(response.get('LOGOUT_EXCEPT'))
        else:
            return True

    async def is_data(self, user_id: int, locale_code: str = 'en-US') -> Optional[Dict[str, Any]]:
        """Check if user is registered"""

        response = LocalErrorResponse('DATABASE', locale_code)

        auth = await self.is_login(user_id, response)
        puuid = auth['puuid']
        region = auth['region']
        username = auth['username']
        access_token = auth['access_token']
        entitlements_token = auth['emt']
        notify_mode = auth['notify_mode']
        expiry_token = auth['expiry_token']
        cookie = auth['cookie']
        notify_channel = auth.get('notify_channel', None)
        dm_message = auth.get('DM_Message', None)

        if timestamp_utc() > expiry_token:
            access_token, entitlements_token = await self.refresh_token(user_id, auth)

        headers = {'Authorization': f'Bearer {access_token}', 'X-Riot-Entitlements-JWT': entitlements_token}

        data = dict(
            puuid=puuid,
            region=region,
            headers=headers,
            player_name=username,
            notify_mode=notify_mode,
            cookie=cookie,
            notify_channel=notify_channel,
            dm_message=dm_message,
        )
        return data

    async def refresh_token(self, user_id: int, data: Dict) -> Optional[Dict]:
        """Refresh token"""

        auth = self.auth

        cookies, access_token, entitlements_token = await auth.redeem_cookies(data['cookie'])

        expired_cookie = datetime.timestamp(datetime.utcnow() + timedelta(minutes=59))

        db = self.read_db()
        db[str(user_id)]['cookie'] = cookies['cookie']
        db[str(user_id)]['access_token'] = access_token
        db[str(user_id)]['emt'] = entitlements_token
        db[str(user_id)]['expiry_token'] = expired_cookie

        self.insert_user(db)

        return access_token, entitlements_token

    def change_notify_mode(self, user_id: int, mode: str = None) -> None:
        """Change notify mode"""

        db = self.read_db()

        overite_mode = {'All Skin': 'All', 'Specified Skin': 'Specified', 'Off': None}
        db[str(user_id)]['notify_mode'] = overite_mode[mode]

        self.insert_user(db)

    def change_notify_channel(self, user_id: int, channel: str, channel_id: int = None) -> None:
        """Change notify mode"""

        db = self.read_db()

        if channel == 'DM Message':
            db[str(user_id)]['DM_Message'] = True
            db[str(user_id)].pop('notify_channel', None)
        elif channel == 'Channel':
            db[str(user_id)]['DM_Message'] = False
            db[str(user_id)]['notify_channel'] = channel_id

        self.insert_user(db)

    def check_notify_list(self, user_id: int) -> None:
        database = JSON.read('notifys')
        notify_skin = [x for x in database if x['id'] == str(user_id)]
        if len(notify_skin) == 0:
            raise DatabaseError("You're notification list is empty!")

    def get_user_is_notify(self) -> Dict[str, Any]:
        """Get user is notify"""

        database = JSON.read('users')
        notifys = [user_id for user_id in database if database[user_id]['notify_mode'] is not None]
        return notifys

    def insert_skin_price(self, skin_price: Dict, force=False) -> None:
        """Insert skin price to cache"""

        cache = self.read_cache()
        price = cache['prices']
        check_price = price.get('is_price', None)
        if check_price is False or force:
            fetch_price(skin_price)

    async def cookie_login(self, user_id: int, cookie: Optional[str], locale_code: str) -> Optional[Dict[str, Any]]:
        """Login with cookie"""

        db = self.read_db()
        auth = self.auth
        auth.locale_code = locale_code

        data = await auth.login_with_cookie(cookie)

        cookie = data['cookies']
        access_token = data['AccessToken']
        token_id = data['token_id']
        entitlements_token = data['emt']

        puuid, name, tag = await auth.get_userinfo(access_token)
        region = await auth.get_region(access_token, token_id)
        player_name = f'{name}#{tag}' if tag is not None and tag is not None else 'no_username'

        expiry_token = datetime.timestamp(datetime.utcnow() + timedelta(minutes=59))

        try:
            data = dict(
                cookie=cookie,
                access_token=access_token,
                token_id=token_id,
                emt=entitlements_token,
                puuid=puuid,
                username=player_name,
                region=region,
                expiry_token=expiry_token,
                notify_mode=None,
                DM_Message=True,
            )

            db[str(user_id)] = data
            self.insert_user(db)

        except Exception as e:
            print(e)
            return {'auth': False}
        else:
            return {'auth': True, 'player': player_name}
