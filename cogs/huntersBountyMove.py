import random
import discord
from discord.ext import commands, tasks
from datetime import datetime
from zoneinfo import ZoneInfo

class WeeklyHuntersBountyEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = ZoneInfo("Europe/Prague")
        self.last_sent_date = None
        self.check_time.start()

    def cog_unload(self):
        self.check_time.cancel()

    def create_embed(self):
        genNumber = random.randint(1,5)
        textToShow = "The Draeth have caught up with us again. Time to relocate!"

        if genNumber == 1:
            textToShow = "The Draeth have caught up with us again. Time to relocate!"
        elif genNumber == 2:
            textToShow = "This was a scheduled jump. No need for panic!"
        elif genNumber == 3:
            textToShow = "We always stay one step ahead of our enemies. Time to jump!"
        elif genNumber == 4:
            textToShow = "We need to help one of our Strongholds that is under attack!"
        elif genNumber == 5:
            textToShow = "A large number of bounties for us in this sector. Enjoy!"

        embed = discord.Embed(
            title="Huntress of the Stars has jumped to a new star system!",
            description=textToShow,
            color=discord.Color.gold()
        )
        embed.set_image(url="https://64.media.tumblr.com/1f3b93c4af348a984598df1931311dc6/bcb287e54fc302cd-6d/s540x810/d6724055a9d1b36393c1ef95ad51d329d7edbbe7.gif")
        embed.set_footer(text="Huntress of the Stars is 'out of time', which means that you can be here at any time, even during bounties. You can RP it as being connected using a hologram.")
        return embed

    def is_time_to_send(self):
        now = datetime.now(self.timezone)

        # Thursday at 20:00
        if now.weekday() != 1:  # 0=Monday, 4=Friday
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
            channel = self.bot.get_channel(1291758467929079819)
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
    await bot.add_cog(WeeklyHuntersBountyEmbed(bot))