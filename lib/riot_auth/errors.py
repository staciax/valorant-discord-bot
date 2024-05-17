# https://github.com/floxay/python-riot-auth

__all__ = (
    'RiotAuthenticationError',
    'RiotAuthError',
    'RiotMultifactorError',
    'RiotRatelimitError',
    'RiotUnknownErrorTypeError',
    'RiotUnknownResponseTypeError',
)


class RiotAuthError(Exception):
    """Base class for RiotAuth errors."""


class RiotAuthenticationError(RiotAuthError):
    """Failed to authenticate."""


class RiotRatelimitError(RiotAuthError):
    """Ratelimit error."""


class RiotMultifactorError(RiotAuthError):
    """Multi-factor failed."""


class RiotUnknownResponseTypeError(RiotAuthError):
    """Unknown response type."""


class RiotUnknownErrorTypeError(RiotAuthError):
    """Unknown response error type."""
