import discord
from discord import app_commands
from discord.ext import commands, tasks
import calendar
import datetime

class DateChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dateFinder.start()

    def cog_unload(self):
        self.dateFinder.cancel()

    @tasks.loop(seconds=5)
    async def dateFinder(self):
        currentYear = datetime.date.today().year
        today = datetime.date.today()

        todayOrder = today.timetuple().tm_yday
        dayWeek = todayOrder % 5

        if dayWeek == 0:
            dayName = "Benduday"
        elif dayWeek == 4:
            dayName = "Zhellday"
        elif dayWeek == 3:
            dayName = "Taungsday"
        elif dayWeek == 2:
            dayName = "Centaxday"
        elif dayWeek == 1:
            dayName = "Primeday"
        else:
            dayName = "Benduday"
    
        if calendar.isleap(currentYear):
            print(f"{currentYear} is leap.")
        else:
            print(f"{currentYear} is not leap.")
        
        print(f"Today is the {todayOrder}. day of the year. It is {dayName}.")

    @dateFinder.before_loop
    async def before_dateFinder(self):
        await self.bot.wait_until_ready()

# Load the cog
async def setup(bot):
    await bot.add_cog(DateChanger(bot))