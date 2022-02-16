import discord
from discord.ext import tasks
from discord.ext import commands

import feedparser
import html
import calendar


class AnimeNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_updated_time = 0
        self._channel_id = 943212972308832256

    @staticmethod
    def __get_anime_entries():

        # get the RSS feed
        url = "https://myanimelist.net/rss/news.xml"
        feed = feedparser.parse(url)

        # get the entries as a reversed list
        # this way the oldest posts would in the first index
        entries = feed.entries
        entries.reverse()

        return entries

    @tasks.loop(minutes=60)
    async def anime_news(self):
        entries = AnimeNews.__get_anime_entries()

        self._channel = self.bot.get_channel(self._channel_id)

        # For every news in the newsList
        for entry in entries:

            # Convert published_parsed from time.struct_time to seconds from epoch
            entry_time = calendar.timegm(entry.published_parsed)

            # if the current entry time is ahead of the last
            # updated time, post the news
            if entry_time > self._last_updated_time:
                self._last_updated_time = entry_time

                # Create the Embed message for discord
                message = discord.Embed(
                    color=discord.Color.blue(),
                    title=entry.title,
                    url=entry.id,
                    # html.unescape converts html special characters
                    # to string. for example "&pound;682m" to "£682m"
                    description=html.unescape(entry.summary),
                )
                message.set_thumbnail(url=entry.href)
                message.set_footer(
                    text="From MyAnimeList.net",
                    icon_url="https://i.imgur.com/gpXMxYl.png",
                )

                await self._channel.send(embed=message)

    # Command for setting the channel for messages to send
    @commands.command(name="animenews-channel", hidden=True)
    @commands.is_owner()
    async def animenews_channel(self, ctx, *, channel_id):
        self._channel_id = int(channel_id)

    # Command for Starting the animenews alert
    @commands.command(name="animenews-start", hidden=True)
    @commands.is_owner()
    async def news_start(self, ctx):
        self.anime_news.start()

    # Command for Stopping the animenews alert
    @commands.command(name="animenews-stop", hidden=True)
    @commands.is_owner()
    async def news_stop(self, ctx):
        self.anime_news.stop()


def setup(bot):
    bot.add_cog(AnimeNews(bot))
