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
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
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
                logger.debug(f"Extension {extension} Loaded Successfully")
                print(f"Extension {extension} Loaded Successfully.")

    async def on_message(self, message):
        if message.channel.type == discord.ChannelType.news:
            await message.publish()

        await self.process_commands(message)

    async def on_ready(self):
        await self.change_presence(
            status=discord.Status.online, activity=discord.Game("Game of Life")
        )
        logger.debug(f"Bot {self.user} is connected to Discord and ready to roll!")
        print(f"Bot {self.user} is connected to Discord and ready to roll!")


def main():
    setup_logger()
    logger.debug("Starting Illimitable-Bot.....")
    bot = IllimitableBot(command_prefix=".")
    logger.debug("--------------------------------------------")
    server.alive()

    load_dotenv()
    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
