import discord
from discord.ext import commands, tasks
from datetime import datetime
from zoneinfo import ZoneInfo

class WeeklyEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = ZoneInfo("Europe/Prague")
        self.last_sent_date = None
        self.check_time.start()

    def cog_unload(self):
        self.check_time.cancel()

    def create_embed(self):
        embed = discord.Embed(
            title="If you enjoy what this server offers, keep reading!",
            description="Don't forget that you can support us here: https://discord.com/channels/1258379465919041589/1293211215262253097\n\nYou can:\n- Get a cool unicode icon for your Crew channel!\n- Get your own Opening Crawl\n- Gain access to an upper floor of Hunter's Bounty, with jukebox and other cool stuff!\n- Feel good that you supported something you like!\n",
            color=discord.Color.gold()
        )
        embed.set_image(url="https://c.tenor.com/nwBMOVfhuS0AAAAC/tenor.gif")
        embed.set_footer(text="We love you all ♥️")
        return embed

    def is_time_to_send(self):
        now = datetime.now(self.timezone)

        # Thursday at 20:00
        if now.weekday() != 4:  # 0=Monday, 4=Friday
            return False
        
        if now.hour != 20 or now.minute != 0:
            return False

        # Only once per day
        today = now.date()
        if self.last_sent_date == today:
            return False
            
        return True

    @tasks.loop(minutes=1)
    async def check_time(self):
        if self.is_time_to_send():
            channel = self.bot.get_channel(1258379466376216597)
            if channel:
                embed = self.create_embed()
                await channel.send(embed=embed)
                self.last_sent_date = datetime.now(self.timezone).date()
            else:
                print("Channel not found or ID is invalid.")

    @check_time.before_loop
    async def before_check_time(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyEmbed(bot))