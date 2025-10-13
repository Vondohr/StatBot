import asyncio
import discord
from discord import app_commands
from discord.ext import commands


class KickCrewModal(discord.ui.Modal, title="Confirm Crew Kick"):
    def __init__(self, target: discord.Member):
        super().__init__()
        self.target = target
        self.confirmation = discord.ui.TextInput(
            label='Type "Yes" below to confirm.',
            placeholder='This will remove the member from your Crew.',
            required=True,
            max_length=3
        )
        self.add_item(self.confirmation)

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirmation.value.strip().lower() == "yes":
            roles = self.target.roles
            is_on_location = any(role.name.startswith(("Planet", "Moon")) for role in roles)

            # Announce the kick
            embed = discord.Embed(
                title="Crew Member Removed",
                description=f"{self.target.mention} has been removed from the Crew.",
                color=discord.Color.red()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1427237203708350544/CrewLeaving.gif")
            await interaction.response.send_message(embed=embed)

            await asyncio.sleep(10)

            # Add default planet role if not already on one
            if not is_on_location:
                planet_role = discord.utils.get(interaction.guild.roles, name="Planet Carajam")
                if planet_role:
                    await self.target.add_roles(planet_role)

            # Remove spaceship role if present
            spaceship_role = next((role for role in roles if role.name.startswith("Spaceship")), None)
            if spaceship_role:
                crew_role = discord.utils.get(interaction.guild.roles, name="Crew")
                await self.target.remove_roles(spaceship_role, crew_role)
            else:
                await interaction.followup.send("They are not in a spaceship!", ephemeral=True)
        else:
            await interaction.response.defer(ephemeral=True)


class KickFromCrew(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick_from_crew", description="Remove a member from your current Crew (requires confirmation).")
    @app_commands.describe(member="Select the Crew member to remove.")
    async def kick_from_crew(self, interaction: discord.Interaction, member: discord.Member):
        author_roles = interaction.user.roles
        target_roles = member.roles
        allowed_category_name = "「🌀」Crews【Spaceships】"

        # Channel category check
        if interaction.channel.category is None or interaction.channel.category.name != allowed_category_name:
            await interaction.response.send_message(
                f"This command can only be used in channels under the '{allowed_category_name}' category.",
                ephemeral=True
            )
            return

        # Both must have a "Spaceship" role and it must be the same one
        author_ship = next((role for role in author_roles if role.name.startswith("Spaceship")), None)
        target_ship = next((role for role in target_roles if role.name.startswith("Spaceship")), None)

        if not author_ship or not target_ship:
            await interaction.response.send_message(
                "Both users must be part of a Crew to use this command.",
                ephemeral=True
            )
            return

        if author_ship != target_ship:
            await interaction.response.send_message(
                f"{member.mention} is not part of your Crew!",
                ephemeral=True
            )
            return

        # Cannot kick yourself
        if member == interaction.user:
            await interaction.response.send_message("You cannot kick yourself.", ephemeral=True)
            return

        # Check the user is a Captain
        if not any(role.name == "Captains" for role in author_roles):
            await interaction.response.send_message("You do not have permission to remove Crew members. Become a Captain first!", ephemeral=True)
            return

        # Show the modal
        modal = KickCrewModal(member)
        await interaction.response.send_modal(modal)


async def setup(bot: commands.Bot):
    await bot.add_cog(KickFromCrew(bot))