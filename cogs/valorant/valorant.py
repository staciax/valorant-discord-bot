from __future__ import annotations

import io
import logging
import json
import random
import discord

from abc import ABC
from colorthief import ColorThief
from datetime import datetime, timezone
from functools import cache as functools_cache
from discord import app_commands, Interaction
from discord import utils
from discord.ext import commands
from discord.app_commands import Choice
from discord.app_commands.checks import dynamic_cooldown

from .events import Events
from .context_menu import ContextMenu
from .notify import Notify

from typing import Literal, List, TYPE_CHECKING

if TYPE_CHECKING:
    from bot import ValorantBot

_log = logging.getLogger('cogs.valorant')

MISSING = utils.MISSING

class CompositeMetaClass(type(commands.Cog), type(ABC)):
    """
    This allows the metaclass used for proper type detection to
    coexist with discord.py's metaclass
    """
    pass

class Valorant(
    Notify,
    Events,
    ContextMenu,
    commands.Cog,
    metaclass=CompositeMetaClass
):
    """Valorant API Commands"""

    def __init__(self, bot: ValorantBot) -> None:
        super().__init__()
        self.bot: ValorantBot = bot