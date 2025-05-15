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

    @tasks.loop(minutes=11)
    async def dateFinder(self):
        currentYear = datetime.date.today().year
        today = datetime.date.today()

        todayOrder = today.timetuple().tm_yday
        dayWeek = todayOrder % 5

        if dayWeek == 0:
            dayName = "benduday"
        elif dayWeek == 4:
            dayName = "zhellday"
        elif dayWeek == 3:
            dayName = "taungsday"
        elif dayWeek == 2:
            dayName = "centaxday"
        elif dayWeek == 1:
            dayName = "primeday"
        else:
            dayName = "benduday"
        
        month = "elona"
        monthNumber = "x"

        if calendar.isleap(currentYear):
            if today > datetime.date(today.year, 2, 29):
                todayOrder -= 1

        if todayOrder < 6:
            monthName = "new-years-festival"
            monthNumber = "y"
            monthDay = todayOrder
        elif todayOrder < 41:
            monthName = "elona"
            monthNumber = "1"
            monthDay = todayOrder - 5
        elif todayOrder < 76:
            monthName = "kelona"
            monthNumber = "2"
            monthDay = todayOrder - 40
        elif todayOrder < 111:
            monthName = "selona"
            monthNumber = "3"
            monthDay = todayOrder - 75
        elif todayOrder < 146:
            monthName = "telona"
            monthNumber = "4"
            monthDay = todayOrder - 110
        elif todayOrder < 181:
            monthName = "nelona"
            monthNumber = "5"
            monthDay = todayOrder - 145
        elif todayOrder < 216:
            monthName = "helona"
            monthNumber = "6"
            monthDay = todayOrder - 180
        elif todayOrder < 221:
            monthName = "festival-of-life"
            monthNumber = "l"
            monthDay = todayOrder - 215
        elif todayOrder < 256:
            monthName = "melona"
            monthNumber = "7"
            monthDay = todayOrder - 220
        elif todayOrder < 291:
            monthName = "yelona"
            monthNumber = "8"
            monthDay = todayOrder - 255
        elif todayOrder < 326:
            monthName = "relona"
            monthNumber = "9"
            monthDay = todayOrder - 290
        elif todayOrder < 291:
            monthName = "festival-of-stars"
            monthNumber = "s"
            monthDay = todayOrder - 325
        else:
            monthName = "welona"
            monthNumber = "10"
            monthDay = todayOrder - 330

        if calendar.isleap(currentYear):
            if today == datetime.date(today.year, 2, 29):
                dayName = "leap-day"
                monthDay = "0"
                monthNumber = "0"
                monthName = "x"
                todayOrder = 0

        channelID = 1372560402319409152  # Replace with your actual channel ID
        channel = self.bot.get_channel(channelID)
        
        if channel:
            try:
                await channel.edit(name=f"「📅」{dayName}《{monthDay}-{monthName}┃{monthDay}-{monthNumber}┃{todayOrder}》")
            except Exception as e:
                print(f"Failed to update channel name: {e}")
        else:
            print("Channel not found.")

        # print(f"「📅」{dayName}《{monthDay}-{monthName}┃{monthDay}-{monthNumber}┃{todayOrder}》")

    @dateFinder.before_loop
    async def before_dateFinder(self):
        await self.bot.wait_until_ready()

# Load the cog
async def setup(bot):
    await bot.add_cog(DateChanger(bot))