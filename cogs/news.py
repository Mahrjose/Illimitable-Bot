from discord.ext import commands, tasks
import discord

from bs4 import BeautifulSoup
import feedparser
import html
import calendar
import requests
import json


def update_NewsTime(News: str, new_value: int) -> None:
    with open("TimeInfo.json", "r+") as file:
        data: json = json.load(file)
        data["Latest_NewsTime"][f"{News}"] = new_value
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def read_NewsTime(News: str) -> int:
    with open("TimeInfo.json") as file:
        data: json = json.load(file)
        return data["Latest_NewsTime"][f"{News}"]


def scrape_metaImage(url) -> str:
    html_contents = requests.get(url).text
    soup = BeautifulSoup(html_contents, features="html.parser")
    image = soup.find("meta", attrs={"property": "og:image"})
    return image["content"] if image is not None else None


class AnimeNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._channel_id = 943212972308832256  # Need to remove this (hardcoded)
        self._last_updated_time = read_NewsTime("AnimeNews")
        self.anime_news.start()

    @staticmethod
    def _get_anime_entries() -> list:

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
        all_entries = AnimeNews._get_anime_entries()

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
                    update_NewsTime("AnimeNews", entry_time)

                    # If the feed is from MyAnimeList.net
                    if "myanimelist.net" in entry.id:

                        # Create the Embed message for discord
                        message = discord.Embed(
                            color=discord.Color.blue(),
                            title=f"📰  {entry.title}",
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

                        image_link = scrape_metaImage(entry.id)

                        message = discord.Embed(
                            color=discord.Color.blue(),
                            title=f"📰  {entry.title}",
                            url=entry.id,
                            description=html.unescape(entry.summary),
                        )
                        message.set_footer(
                            text="From Anime News Network",
                            icon_url="https://i.imgur.com/0Kus4ME.png",
                        )
                        if image_link is not None:
                            message.set_image(url=image_link)
                        else:
                            continue

                    await self._channel.send(embed=message)

    # This will exec before starting the anime_news() func
    @anime_news.before_loop
    async def before_anime_news(self):
        print("Starting Anime News...")
        await self.bot.wait_until_ready()

    # Command for setting the channel for messages to send
    @commands.command(name="set-animenews-channel", hidden=True)
    @commands.is_owner()
    async def set_animenews_channel(self, ctx, *, channel_id):
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


class TechNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._channel_id = 947191180268015756
        self._last_updated_time = read_NewsTime("TechNews")
        self.tech_news.start()

    @staticmethod
    def _get_techNews_entries() -> list:

        # RSS feeds
        urls: tuple = (
            # "https://www.reddit.com/user/mahrjose/m/tech_news/top/.rss?t=today&limit=25", # TechNews Custom Feed
            "https://www.reddit.com/r/gamernews/top.rss?t=today&limit=25",  # r/gamernews
            "https://www.reddit.com/r/technology/top.rss?t=today&limit=25",  # r/technology
        )

        # Get full feed data with feedparser
        feeds: list = [feedparser.parse(url) for url in urls]
        # Get only the entries of all the feeds combined in a list
        all_entries: list = [feed.entries for feed in feeds]
        return all_entries

    @tasks.loop(minutes=10)
    async def tech_news(self):
        all_entries: list = TechNews._get_techNews_entries()
        self._channel = self.bot.get_channel(self._channel_id)

        # Entries of a single RSS feed from the combined list of all rss feed
        for entries in all_entries:
            # Specific entry from all the entries
            for entry in entries:

                # Time when this entry was updated or Posted
                entry_time = calendar.timegm(entry.published_parsed)

                if entry_time > self._last_updated_time:
                    self._last_updated_time = entry_time
                    update_NewsTime("TechNews", entry_time)

                    summary = html.unescape(entry.summary)
                    soup = BeautifulSoup(summary, "html.parser")
                    all_links = soup.findAll("a")
                    # From all the links present, get the Direct News Link
                    for link in all_links:
                        if str(link.string) == "[link]":
                            news_link = link["href"]

                    image_url = entry.get("media_thumbnail")
                    reddit_link = entry["links"][0]["href"]

                    message = discord.Embed(
                        color=discord.Color.orange(),
                        title=f"📰  {html.unescape(entry.title)}",
                        url=news_link,
                    )
                    message.add_field(
                        name="\u200B",
                        value=f"🔗 Disscussion on [Reddit]({reddit_link})",
                    )
                    message.set_footer(
                        text="From Reddit", icon_url="https://i.imgur.com/Oj5KugT.png"
                    )
                    if image_url is not None:
                        message.set_image(url=image_url[0]["url"])
                    else:
                        image_url = scrape_metaImage(news_link)
                        if image_url is not None:
                            message.set_image(url=image_url)
                        else:
                            continue

                    await self._channel.send(embed=message)

    # This will exec before starting the tech_news() func
    @tech_news.before_loop
    async def before_tech_news(self):
        print("Starting Tech News...")
        await self.bot.wait_until_ready()

    # Command for setting the channel for messages to send
    @commands.command(name="set-technews-channel", hidden=True)
    @commands.is_owner()
    async def set_technews_channel(self, ctx, *, channel_id):
        self._channel_id = int(channel_id)

    @commands.command(name="technews-start", hidden=True)
    @commands.is_owner()
    async def news_start(self, ctx):
        self.tech_news.start()

    @commands.command(name="technews-stop", hidden=True)
    @commands.is_owner()
    async def news_stop(self, ctx):
        self.tech_news.stop()


def setup(bot):
    bot.add_cog(AnimeNews(bot))
    bot.add_cog(TechNews(bot))
