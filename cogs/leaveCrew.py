import asyncio
import discord
from discord import app_commands
from discord.ext import commands

class LeaveCrewModal(discord.ui.Modal, title="Confirm Leaving Crew"):
    confirmation = discord.ui.TextInput(
        label='Type "Yes" to confirm. Remember that you will lose all the Rerolls gained through Loyalty Missions with this Crew.',
        placeholder='Yes',
        required=True,
        max_length=3
    )

    def __init__(self, user: discord.User):
        super().__init__()
        self.user = user

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirmation.value.strip().lower() == "yes":
            roles = [role for role in interaction.user.roles]
            isOnLocation = False
            
            embed = discord.Embed(
                title="Crew Departure",
                description=f"{self.user.mention} has left their crew.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

            await asyncio.sleep(10)
            
            for role in roles:
                if role.name.startswith("Planet") or role.name.startswith("Moon"):
                    isOnLocation = True
                    
            if not isOnLocation:
                await interaction.user.add_roles("Planet Carajam")
            
            spaceship_role = next((role for role in roles if role.name.startswith("Spaceship")), None)
            if not spaceship_role:
                await interaction.response.send_message("You are not in a spaceship!", ephemeral=True)
                return
            else:
                await interaction.user.remove_roles(spaceship_role)
        else:
            # Do nothing if incorrect input
            await interaction.response.defer(ephemeral=True)


class LeaveCrew(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="leave_crew", description="Leave your current crew after confirmation.")
    async def leave_crew(self, interaction: discord.Interaction):
        roles = [role for role in interaction.user.roles]
        
        allowed_category_name = "「🌀」Crews【Spaceships】"

        if interaction.channel.category is None or interaction.channel.category.name != allowed_category_name:
            await interaction.response.send_message(
                f"This command can only be used in channels under the '{allowed_category_name}' category.",
                ephemeral=True
            )
            return
        
        if not any(role.name == "Crew" for role in roles):
            await interaction.response.send_message("You are in no Crew!", ephemeral=True)
            return
        
        if any(role.name == "Crew Narrator" for role in roles):
            await interaction.response.send_message("You are Narrating a Loyalty Mission. Finish it first!", ephemeral=True)
            return
        
        if any(role.name == "Loyalty Marked" for role in roles):
            await interaction.response.send_message("You are on a Loyalty Mission. Finish it first!", ephemeral=True)
            return

        modal = LeaveCrewModal(interaction.user)
        await interaction.response.send_modal(modal)

async def setup(bot: commands.Bot):
    await bot.add_cog(LeaveCrew(bot))