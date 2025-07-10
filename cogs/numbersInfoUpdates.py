import discord
from discord.ext import commands

class MemberTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.voice_channel_id = 1277600577043300475

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.update_voice_channel_name(member.guild)

    async def update_voice_channel_name(self, guild: discord.Guild):
        # Get the current number of members
        member_count = guild.member_count

        # Count roles with "Spaceship" in the name
        spaceship_roles = sum(1 for role in guild.roles if "spaceship" in role.name.lower())

        # Compose the new name
        new_name = f"「👥」{member_count} Members |「🚀」{spaceship_roles} Crews"

        # Get the voice channel
        voice_channel = guild.get_channel(self.voice_channel_id)
        if voice_channel and isinstance(voice_channel, discord.VoiceChannel):
            try:
                await voice_channel.edit(name=new_name)
                print(f"Updated voice channel name to: {new_name}")
            except discord.Forbidden:
                print("Missing permissions to edit the voice channel.")
            except discord.HTTPException as e:
                print(f"Failed to edit voice channel: {e}")
        else:
            print("Voice channel not found or invalid.")

async def setup(bot: commands.Bot):
    await bot.add_cog(MemberTracker(bot))
