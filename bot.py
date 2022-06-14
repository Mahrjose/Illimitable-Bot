#!/usr/bin/python3

import os
import discord
from discord.ext import commands

from dotenv import load_dotenv
import server
import logging

logger = logging.getLogger(__name__)


def setup_logger() -> None:
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %I:%M:%S %p %Z")
    file_handler = logging.FileHandler("Logs/Bot.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class IllimitableBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.load_cogs()

    def load_cogs(self):
        for filename in os.listdir("cogs"):

            # Loop through the "cog" directory and load all the cogs
            if filename.endswith(".py"):
                extension = f"cogs.{filename[:-3]}"
                self.load_extension(extension)
                print(f"Extension {extension} Loaded Successfully.")

    async def on_message(self, message):
        if message.channel.type == discord.ChannelType.news:
            await message.publish()

        await self.process_commands(message)

    async def on_ready(self):
        await self.change_presence(
            status=discord.Status.online, activity=discord.Game("Game of Life")
        )
        print(f"Bot {self.user} is connected to Discord and ready to roll!")


def main():
    setup_logger()
    logger.debug("Illimitable Bot (Re)Started")
    bot = IllimitableBot(command_prefix=".")
    server.alive()

    load_dotenv()
    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
