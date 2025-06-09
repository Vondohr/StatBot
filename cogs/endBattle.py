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
        
        if winning_faction == losing_faction:
            await interaction.response.send_message("The winning faction cannot be the same as the losing faction!", ephemeral=True)
            return

        if not role_winning == "The Draeth":
            members_winning = [member for member in interaction.guild.members if role_winning in member.roles]
            if members_winning:
                await interaction.channel.send(f"(*Removing '{role_winning}' role from {len(members_winning)} member(s).*)")

                for member in members_winning:
                    try:
                        await member.remove_roles(role_winning)
                    except discord.Forbidden:
                        await interaction.response.send_message(f"Missing permissions to remove role from {member.display_name}", ephemeral=True)

        if not role_losing == "The Draeth":
            members_losing = [member for member in interaction.guild.members if role_losing in member.roles]
            if members_losing:
                await interaction.channel.send(f"(*Removing '{role_losing}' role from {len(members_losing)} member(s).*)")

                for member in members_losing:
                    try:
                        await member.remove_roles(role_losing)
                    except discord.Forbidden:
                        await interaction.response.send_message(f"Missing permissions to remove role from {member.display_name}", ephemeral=True)
        
        embed = discord.Embed(
                title=f"Battle on {planet_role} ended! Winning side: {winning_faction}",
                description=f"Losing side: {losing_faction}",
                color=discord.Color.dark_gold(),
            )
        embed.set_image(url="https://pa1.aminoapps.com/6813/24c6a2c1f792538227c5c664a45611265c46fc6a_hq.gif")
        if winning_faction == "Rebels":
            embed.set_thumbnail(url="https://www.nicepng.com/png/full/200-2009186_rebel-alliance-star-wars-rebel-logo.png")
        elif winning_faction == "Imperials":
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/0/0d/Red_emblem_of_the_First_Galactic_Empire.png")
        elif winning_faction == "Hutts":
            embed.set_thumbnail(url="https://static.wikia.nocookie.net/star-wars-expanded-universe-holocron/images/4/4b/Hutt_Symbol.png")
        elif winning_faction == "Czerkans":
            embed.set_thumbnail(url="https://static.wikia.nocookie.net/oppressive-games-power/images/9/99/Czerka1.png")
        elif winning_faction == "Hunters":
            embed.set_thumbnail(url="https://images.seeklogo.com/logo-png/48/2/star-wars-mandalorian-mythosaur-skull-logo-png_seeklogo-484140.png")
        elif winning_faction == "The Draeth":
            embed.set_thumbnail(url="https://lumiere-a.akamaihd.net/v1/images/image_4aaef442.png")
        embed.set_footer(text="This location will get inaccessible for you in 2 hours.")

        await interaction.channel.send(embed=embed)

        # Wait for 2 hours (7200 seconds)
        await asyncio.sleep(7200)

        members_planet = [member for member in interaction.guild.members if role_planet in member.roles]
        if members_planet:
            await interaction.channel.send(f"*Shuttles arrive to take everyone away from {role_planet}.*")

            for member in members_planet:
                try:
                    location_roles = [role for role in member.roles if role.name.startswith(("Planet", "Moon"))]
                    if len(location_roles) > 1:
                        await member.remove_roles(role_planet)
                except discord.Forbidden:
                    await interaction.response.send_message(f"Missing permissions to remove role from {member.display_name}", ephemeral=True)

    # Define choices for location in the battle command
    @send_embed.autocomplete("planet_role")
    async def send_embed_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            discord.app_commands.Choice(name=dest, value=dest)
            for dest in valid_destinations if current.lower() in dest.lower()
        ][:25]  # Limit to 25 choices, the maximum for Discord
            
async def setup(bot):
    await bot.add_cog(EmbedEndBattleSender(bot))