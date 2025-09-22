import discord
from discord.ext import commands, tasks
from datetime import datetime
from zoneinfo import ZoneInfo

class WeeklyAllChannelsEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = ZoneInfo("Europe/Prague")
        self.last_sent_date = None
        self.check_time.start()

    def cog_unload(self):
        self.check_time.cancel()

    def create_embed(self):
        embed = discord.Embed(
            title="Turn on 'All Channels'!",
            description="Don't forget that we have many cool channels that might be hidden from you.\n\nYou can turn them on in the Server Settings.\n- Just follow the instructions below!",
            color=discord.Color.gold()
        )
        embed.set_image(url="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbm03ZTJkYWNiZ3k0NGdmbThnejhydDQ1amI2MWs0N2E2cHpraGw3NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hHbxrtb3G2b3Ax8FvP/giphy.gif")
        return embed

    def is_time_to_send(self):
        now = datetime.now(self.timezone)

        # Sunday at 20:00
        if now.weekday() != 6:  # 0=Monday, 4=Friday
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
    await bot.add_cog(WeeklyAllChannelsEmbed(bot))