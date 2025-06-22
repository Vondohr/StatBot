import discord
from discord import app_commands
from discord.ext import commands

class RoleAdder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="mass_add_role",
        description="Add a role to all members who already have a specific role."
    )
    @app_commands.describe(
        target_role="The role that members must have to be affected.",
        role_to_add="The role you want to add to those members."
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mass_add_role(
        self,
        interaction: discord.Interaction,
        target_role: discord.Role,
        role_to_add: discord.Role
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"⏳ Adding `{role_to_add.name}` to all members with `{target_role.name}`...",
            ephemeral=True
        )

        count = 0
        failed = 0

        for member in guild.members:
            if target_role in member.roles and role_to_add not in member.roles:
                try:
                    await member.add_roles(role_to_add)
                    count += 1
                except Exception as e:
                    failed += 1
                    print(f"Failed to add role to {member.display_name}: {e}")

        await interaction.followup.send(
            f"✅ Added `{role_to_add.name}` to **{count}** members.\n"
            f"❌ Failed for **{failed}** members.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(RoleAdder(bot))