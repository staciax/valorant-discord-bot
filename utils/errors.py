from typing import Any, Union
from discord.ext import commands

class UserInputErrors(commands.UserInputError):
    def __init__(self, message: str, *arg: Any):
        super().__init__(message=message, *arg)