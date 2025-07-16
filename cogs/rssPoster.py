import discord
from discord.ext import commands, tasks
import feedparser
import asyncio
import json
import os

RSS_URL = "https://www.starwarsnewsnet.com/feed"
JSON_FILE = "posted_entries.json"

class RSSFeedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1260348000316817501
        self.posted_ids = self.load_posted_ids()
        self.check_feed.start()

    def cog_unload(self):
        self.check_feed.cancel()

    def load_posted_ids(self):
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                return set(json.load(f))
        return set()

    def save_posted_ids(self):
        with open(JSON_FILE, "w") as f:
            json.dump(list(self.posted_ids), f, indent=2)

    @tasks.loop(minutes=10)
    async def check_feed(self):
        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            return

        new_entries = []
        for entry in reversed(feed.entries):  # oldest to newest
            entry_id = entry.get("id") or entry.get("link")
            if entry_id not in self.posted_ids:
                new_entries.append(entry)

        if not new_entries:
            return

        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        for entry in new_entries:
            entry_id = entry.get("id") or entry.get("link")
            title = entry.title
            link = entry.link
            summary = entry.summary if hasattr(entry, 'summary') else ''

            embed = discord.Embed(
                title=title,
                url=link,
                description=summary[:500] + ("..." if len(summary) > 500 else ""),
                color=discord.Color.blue()
            )

            await channel.send(embed=embed)
            self.posted_ids.add(entry_id)

        self.save_posted_ids()

    @check_feed.before_loop
    async def before_check_feed(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RSSFeedCog(bot))