# https://github.com/floxay/python-riot-auth

from .auth import RiotAuth as RiotAuth
from .errors import (
    RiotAuthenticationError as RiotAuthenticationError,
    RiotAuthError as RiotAuthError,
    RiotMultifactorError as RiotMultifactorError,
    RiotRatelimitError as RiotRatelimitError,
    RiotUnknownErrorTypeError as RiotUnknownErrorTypeError,
    RiotUnknownResponseTypeError as RiotUnknownResponseTypeError,
)
