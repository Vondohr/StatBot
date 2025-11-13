import discord
from discord.ext import commands
from discord import app_commands

class Supporters(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 123456789012345678  # replace with your channel ID

    async def cog_load(self):
        await self.bot.wait_until_ready()
        try:
            await self.ensure_embeds_exist()
        except Exception as e:
            print(f"[Supporters] Failed during startup: {e}")

    async def ensure_embeds_exist(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"[Supporters] Channel {self.channel_id} not found or bot lacks permissions.")
            return

        try:
            messages = [m async for m in channel.history(limit=10)]
        except Exception as e:
            print(f"[Supporters] Could not read channel history: {e}")
            return

        # Just log for now
        print(f"[Supporters] Found {len(messages)} recent messages in channel {channel.id}")

    @app_commands.command(name="refresh_supporters", description="Refresh supporter embeds.")
    async def refresh_supporters(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Command works!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Supporters(bot))
