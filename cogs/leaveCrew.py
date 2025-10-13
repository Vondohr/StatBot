import asyncio
import discord
from discord import app_commands
from discord.ext import commands


class LeaveCrewModal(discord.ui.Modal, title="Confirm Leaving Crew"):
    def __init__(self, user: discord.Member):
        super().__init__()
        self.user = user
        self.confirmation = discord.ui.TextInput(
            label='Type "Yes" below to confirm. All Rerolls will be lost.',
            placeholder='Yes',
            required=True,
            max_length=3
        )
        self.add_item(self.confirmation)

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirmation.value.strip().lower() == "yes":
            roles = interaction.user.roles
            is_on_location = any(role.name.startswith(("Planet", "Moon")) for role in roles)

            # Announce departure
            embed = discord.Embed(
                title="Crew Departure",
                description=f"{self.user.mention} has left their crew.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

            await asyncio.sleep(10)

            # Add default planet role if not already on one
            if not is_on_location:
                planet_role = discord.utils.get(interaction.guild.roles, name="Planet Carajam")
                if planet_role:
                    await interaction.user.add_roles(planet_role)

            # Remove spaceship role if present
            spaceship_role = next((role for role in roles if role.name.startswith("Spaceship")), None)
            if spaceship_role:
                crew_role = discord.utils.get(interaction.guild.roles, name="Crew")
                await interaction.user.remove_roles(spaceship_role, crew_role)
            else:
                await interaction.followup.send("You are not in a spaceship!", ephemeral=True)
        else:
            await interaction.response.defer(ephemeral=True)


class LeaveCrew(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="leave_crew", description="Leave your current Crew (requires confirmation).")
    async def leave_crew(self, interaction: discord.Interaction):
        roles = interaction.user.roles
        allowed_category_name = "「🌀」Crews【Spaceships】"

        # Channel category check
        if interaction.channel.category is None or interaction.channel.category.name != allowed_category_name:
            await interaction.response.send_message(
                f"This command can only be used in channels under the '{allowed_category_name}' category.",
                ephemeral=True
            )
            return

        # Role checks
        if not any(role.name == "Crew" for role in roles):
            await interaction.response.send_message("You are in no Crew!", ephemeral=True)
            return

        if any(role.name == "Crew Narrator" for role in roles):
            await interaction.response.send_message("You are Narrating a Loyalty Mission. Finish it first!", ephemeral=True)
            return

        if any(role.name == "Loyalty Marked" for role in roles):
            await interaction.response.send_message("You are on a Loyalty Mission. Finish it first!", ephemeral=True)
            return
            
        # Show the modal
        modal = LeaveCrewModal(interaction.user)
        await interaction.response.send_modal(modal)


async def setup(bot: commands.Bot):
    await bot.add_cog(LeaveCrew(bot))