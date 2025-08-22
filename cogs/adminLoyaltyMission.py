import sqlite3

import discord
from discord.ext import commands
from discord import app_commands

NARRATOR_ROLE_NAME = "Crew Narrator"
LOYALTY_ROLE_NAME = "Loyalty Marked"
ADMIN_ROLE_NAME = "Narrators"

class LoyaltyMissionAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_loyalty_mission_end", description="End a Loyalty Mission for all members of a Crew.")
    @app_commands.describe(role="The role of the Crew that finished the Loyalty Mission")
    async def admin_loyalty_mission_end(self, interaction: discord.Interaction, role: discord.Role):
        if not any(r.name == ADMIN_ROLE_NAME for r in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to end this mission.", ephemeral=True)
            return
        
        guild = interaction.guild
        narrator_role = discord.utils.get(guild.roles, name=NARRATOR_ROLE_NAME)
        loyalty_role = discord.utils.get(guild.roles, name=LOYALTY_ROLE_NAME)

        if not narrator_role or not loyalty_role:
            await interaction.response.send_message("Error: 'Crew Narrator' or 'Loyalty Marked' roles not found.", ephemeral=True)
            return

        '''
        spaceship_role = role
        parts = spaceship_role.split(" ", 1)
        if len(parts) != 2:
            await interaction.followup.send("Invalid spaceship role format.", ephemeral=True)
            return
        ship_key = parts[1].lower()

        conn = sqlite3.connect("data/ship_data.db")
        cur = conn.cursor()
        
        cur.execute("SELECT active_bounty FROM ship_data WHERE id = ?", (ship_key,))
        row = cur.fetchone()
        if not row:
            active_bounty = "undefined"
        else:
            active_bounty = row[3] if row[3] is not None else "undefined"

        if active_bounty != "Loyalty Mission":
            conn.close()
            await interaction.followup.send("There was no Loyalty Mission running!", ephemeral=True)
            return
        else:
            name_of_bounty = "undefined"
            cur.execute(
                "UPDATE ship_data SET active_bounty=? WHERE id=?",
                (name_of_bounty, ship_key),
            )
            conn.commit()
            conn.close()
        '''

        loyalty_nicknames = [member.display_name for member in role.members if loyalty_role in member.roles]

        affected = []
        for member in role.members:
            roles_to_remove = [r for r in [narrator_role, loyalty_role] if r in member.roles]
            if roles_to_remove:
                try:
                    await member.remove_roles(*roles_to_remove, reason="Loyalty Mission ended.")
                    affected.append(member.mention)
                except discord.Forbidden:
                    continue

        if affected:
            messageString = f"Removed **{NARRATOR_ROLE_NAME}** and **{LOYALTY_ROLE_NAME}** roles from: {', '.join(affected)}"
        else:
            messageString = f"No members in {role} had any Loyalty Mission roles to remove.", ephemeral=True

        embed = discord.Embed(
            title=f"Loyalty Mission Ended",
            description=f"Loyalty Mission ended for the Crew of {role}**\n\nOne Reroll rewarded to {loyalty_nicknames}!",
            color=discord.Color.gold()
        )
        embed.set_image(url="https://64.media.tumblr.com/6d3dfbf948c657abf2fa93c0ad0ff836/495d2ace7fab6c1a-03/s540x810/be49d7f4da569d2a61f6d0c5cb78e8c96b668c5a.gif")
        embed.set_footer(text=messageString)

        await interaction.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LoyaltyMissionAdmin(bot))