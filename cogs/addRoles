import discord
from discord import app_commands
from discord.ext import commands

class RoleAdder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addplayerrole", description="Add the 'Player' role to all users who have the 'Crew' role.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def add_player_role(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        crew_role = discord.utils.get(guild.roles, name="Crew")
        player_role = discord.utils.get(guild.roles, name="Player")

        if not crew_role or not player_role:
            await interaction.response.send_message("One or both roles ('Crew', 'Player') not found.", ephemeral=True)
            return

        await interaction.response.send_message("⏳ Adding roles, this may take a moment...", ephemeral=True)

        count = 0
        failed = 0

        for member in guild.members:
            if crew_role in member.roles and player_role not in member.roles:
                try:
                    await member.add_roles(player_role)
                    count += 1
                except Exception as e:
                    failed += 1
                    print(f"Failed to add role to {member.display_name}: {e}")

        await interaction.followup.send(f"✅ Added 'Player' role to {count} members. ❌ Failed for {failed}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleAdder(bot))