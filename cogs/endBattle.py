import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from typing import Literal

# Define allowed destinations as choices for the command
valid_destinations = [
    "Planet Carajam",
    "Planet Kashyyyk",
    "Planet Tatooine",
    "Planet Naboo",
    "Planet Nal Hutta",
    "Moon Nar Shaddaa",
    "Planet Ryloth",
    "Planet Ord Mantell",
    "Planet Lothal",
    "Planet Cantonica",
    "Planet Bracca",
    "Moon Jedha",
    "Planet Alderaan",
    "Planet Coruscant"
]

class EmbedEndBattleSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_end_battle", description="Ends a battle event embed to the current channel.")
    @app_commands.describe(planet_role="The role of the planet or moon where the battle happened")
    @app_commands.describe(winning_faction="The Faction that won the battle")
    @app_commands.describe(losing_faction="The Faction that lost the battle")
    async def send_embed(self, interaction: discord.Interaction, planet_role: str, winning_faction: Literal["Rebels", "Imperials", "Hutts", "Czerkans", "Hunters", "The Draeth"], losing_faction: Literal["Rebels", "Imperials", "Hutts", "Czerkans", "Hunters", "The Draeth"]):
        member = interaction.guild.get_member(interaction.user.id)
        if not discord.utils.get(member.roles, id=1260298617818841318):
                await interaction.response.send_message("You are not an Admin!", ephemeral=True)
                return
    
        role_planet = discord.utils.get(interaction.guild.roles, name=planet_role)
        role_winning = discord.utils.get(interaction.guild.roles, name=winning_faction)
        role_losing = discord.utils.get(interaction.guild.roles, name=losing_faction)

        interaction.response.send_message("Beginning the roles removal.", ephemeral=True)

        if not role_planet:
            await interaction.followup.send("Not a valid planet role!", ephemeral=True)
            return
        
        if winning_faction == losing_faction:
            await interaction.followup.send("The winning faction cannot be the same as the losing faction!", ephemeral=True)
            return

        if not role_winning == "The Draeth":
            members_winning = [member for member in interaction.guild.members if role_winning in member.roles]
            if not members_winning:
                await interaction.followup.send(f"Nobody has the {role_winning} role.", ephemeral=True)
            else:
                await interaction.followup.send(f"Removing '{role_winning}' role from {len(members_winning)} member(s).", ephemeral=True)

                for member in members_winning:
                    try:
                        await member.remove_roles(role_winning)
                    except discord.Forbidden:
                        await interaction.followup.send(f"Missing permissions to remove role from {member.display_name}", ephemeral=True)
                
                await interaction.followup.send(f"Finished removing the '{role_winning}' role from all applicable members.", ephemeral=True)
        

        if not role_losing == "The Draeth":
            members_losing = [member for member in interaction.guild.members if role_losing in member.roles]
            if not members_losing:
                await interaction.followup.send(f"Nobody has the {role_losing} role.", ephemeral=True)
            else:
                await interaction.followup.send(f"Removing '{role_losing}' role from {len(members_losing)} member(s).", ephemeral=True)

                for member in members_losing:
                    try:
                        await member.remove_roles(role_losing)
                    except discord.Forbidden:
                        await interaction.followup.send(f"Missing permissions to remove role from {member.display_name}", ephemeral=True)
                
                await interaction.followup.send(f"Finished removing the '{role_losing}' role from all applicable members.", ephemeral=True)
        
        # Add a message to everyone regarding the winning / losing faction

        # Wait for 2 hours (7200 seconds)
        # await asyncio.sleep(7200)
        await asyncio.sleep(5)

        members_planet = [member for member in interaction.guild.members if role_planet in member.roles]
        if not members_planet:
            await interaction.followup.send(f"Nobody has the {role_planet} role.", ephemeral=True)
        else:
            await interaction.followup.send(f"Removing '{role_planet}' role from {len(members_planet)} member(s).", ephemeral=True)

            for member in members_losing:
                try:
                    location_roles = [role for role in member.roles if role.name.startswith(("Planet", "Moon"))]
                    if len(location_roles) > 1:
                        await member.remove_roles(role_planet)
                except discord.Forbidden:
                    await interaction.followup.send(f"Missing permissions to remove role from {member.display_name}", ephemeral=True)
            
            await interaction.followup.send(f"Finished removing the '{role_planet}' role from all applicable members.", ephemeral=True)

        '''
        try:
            channel_id_int = int(interaction.channel_id)
            channel = interaction.guild.get_channel(channel_id_int)

            if factions == "The Draeth":
                descriptionText = "Bounty Hunter's Guild hub is under attack by **The Draeth!**\n\n**Join the fight!**"
            else:
                descriptionText = "Mercenaries needed!\n\n**Pick a side and join the fight!**"
            
            embed = discord.Embed(
                title=f"Battle on {planet_role}!",
                description=descriptionText,
                color=discord.Color.brand_red(),
            )
            embed.set_image(url="https://www.techspot.com/articles-info/1095/images/2015-11-21-image.gif")
            embed.set_footer(text="You can only join the fight for the next 24 hours!")

            view = ButtonView(factions, planet_role)
            message = await channel.send(embed=embed, view=view)
            view.message = message

            await interaction.response.send_message(f"Embed sent to {channel.mention}.", ephemeral=True)

        except ValueError:
            await interaction.response.send_message("Please provide a valid numeric channel ID.", ephemeral=True)
        '''

    # Define choices for location in the battle command
    @send_embed.autocomplete("planet_role")
    async def send_embed_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            discord.app_commands.Choice(name=dest, value=dest)
            for dest in valid_destinations if current.lower() in dest.lower()
        ][:25]  # Limit to 25 choices, the maximum for Discord
            
async def setup(bot):
    await bot.add_cog(EmbedEndBattleSender(bot))