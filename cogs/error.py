import discord
from discord.ext import commands


class on_error(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
