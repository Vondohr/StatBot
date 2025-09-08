import discord
from discord.ext import commands, tasks
import os

messagesCounts = "message_counts.json"
postedEntries = "posted_entries.json"

class JsonUploader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.upload_json_files.start()  # start the loop when cog loads

    def cog_unload(self):
        self.upload_json_files.cancel()  # stop loop if cog unloads

    @tasks.loop(hours=2)
    async def upload_json_files(self):
        """Uploads two JSON files every 2 hours."""
        channel_id = 1370819441318695024 # logs channel
        channel = self.bot.get_channel(channel_id)

        if channel is None:
            print(f"Channel with ID {channel_id} not found.")
            return

        file1_path = os.path.join(os.getcwd(), messagesCounts)
        file2_path = os.path.join(os.getcwd(), postedEntries)

        if not os.path.exists(file1_path) or not os.path.exists(file2_path):
            await channel.send("One or both JSON files were not found.")
            return

        files = [
            discord.File(file1_path, filename=messagesCounts),
            discord.File(file2_path, filename=postedEntries)
        ]
        await channel.send("Here are the JSON files:", files=files)

    @upload_json_files.before_loop
    async def before_upload(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(JsonUploader(bot))