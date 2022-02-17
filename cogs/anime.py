import discord
from discord.ext import commands, tasks

import feedparser
import html
import calendar


class AnimeNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_updated_time = 0
        self._channel_id = 943212972308832256  # Need to remove this (hardcoded)
        self.anime_news.start()

    @staticmethod
    def __get_anime_entries():

        # all the RSS feeds you need
        urls = (
            "https://myanimelist.net/rss/news.xml",  # MyAnimeList.net
            "https://www.animenewsnetwork.com/all/rss.xml?ann-edition=w",  # Anime News Network
        )

        # get the RSS feeds from feedparser
        feeds = [feedparser.parse(url) for url in urls]
        all_entries = [feed.entries for feed in feeds]

        return all_entries

    @tasks.loop(minutes=10)
    async def anime_news(self):
        all_entries = AnimeNews.__get_anime_entries()

        self._channel = self.bot.get_channel(self._channel_id)

        # For every newsList from a specific RSS feed from all the entries
        for entries in all_entries:
            # For every news in the newsList
            for entry in entries:

                # Convert published_parsed from time.struct_time to seconds from epoch
                entry_time = calendar.timegm(entry.published_parsed)

                # if the current entry time is ahead of the last
                # update to latest time, post the news
                if entry_time > self._last_updated_time:
                    self._last_updated_time = entry_time

                    # If the feed is from MyAnimeList.net
                    if "myanimelist.net" in entry.id:

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

                    # If the feed is from Anime News Network
                    if "animenewsnetwork.com" in entry.id:
                        message = discord.Embed(
                            color=discord.Color.blue(),
                            title=entry.title,
                            url=entry.id,
                            description=html.unescape(entry.summary),
                        )
                        message.set_footer(
                            text="From Anime News Network",
                            icon_url="https://i.imgur.com/0Kus4ME.png",
                        )

                    await self._channel.send(embed=message)

    # This will exec before starting the anime_news() func
    @anime_news.before_loop
    async def before_anime_news(self):
        print("Starting Anime News...")
        await self.bot.wait_until_ready()

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
