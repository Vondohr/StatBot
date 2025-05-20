import discord
from discord.ext import commands

class ActivityTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listen to every message sent in the server
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Prevent bot from responding to itself or other bots
        if message.author.bot:
            return

        # Example: print to console
        # if message.channel.category.name == "Text Channels":
        #    print(f"[{message.guild.name}] #{message.channel.name} - {message.author}: {message.content}")
        # else:
            # print("Message not in the Text Channels category")

        # You can also log this to a file or a database
        # with open("message_log.txt", "a", encoding="utf-8") as f:
        #     f.write(f"{message.created_at} - {message.guild.name} - {message.channel.name} - {message.author}: {message.content}\n")

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(ActivityTracker(bot))