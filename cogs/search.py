import wikipediaapi as wikiapi
import wikipedia as wiki

import discord
from discord.ext import commands


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._wiki_api = wikiapi.Wikipedia("en")

    # This method is for extracting Wikipedia page summaries in 5 or less sentences
    @staticmethod
    def _wiki_summary(page, sentences=5):
        summ = page.summary.split(". ")
        summ = ". ".join(summ[:sentences])
        return summ

    @commands.command(
        brief="Look something up on Wikipedia",
        description="Search anything on Wikipedia to make your life easy! ",
    )
    async def wiki(self, ctx, *, query):
        wiki_search = wiki.search(query)

        try:
            page = self._wiki_api.page(wiki_search[0])

        # Raise this error if wikipedia doesn't return any search result (This page doesn't exist in Wikipedia)
        except IndexError as err:
            self._embed = discord.Embed(
                description="Sorry! I couldn't come up with anything 😔. Check for spelling errors and seach again. Or, most likely, the page you're searching for isn't on Wikipedia.",
                color=discord.Colour.red(),
            )
            await ctx.send(embed=self._embed)

        else:
            self._embed = discord.Embed(
                title=page.title,
                description=f"{Search._wiki_summary(page)}",
                color=discord.Colour.blue(),
            )

            # image_link = wiki.page(str(page.fullurl)[31:-1]).images[0]
            self._embed.set_thumbnail(url="https://i.imgur.com/IcBvA0p.png")
            self._embed.add_field(
                name="\u200B",
                value=f"For more information [click here]({page.fullurl})",
            )
            await ctx.send(embed=self._embed)


def setup(bot):
    bot.add_cog(Search(bot))
