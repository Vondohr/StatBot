import sqlite3

import discord
from discord.ext import commands
from discord import app_commands

NARRATOR_ROLE_NAME = "Crew Narrator"
LOYALTY_ROLE_NAME = "Loyalty Marked"
ADMIN_ROLE_NAME = "Narrators"

class AdminLoyaltyMission(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_loyalty_end", description="End a Loyalty Mission for all members of a Crew.")
    @app_commands.describe(spaceship="The role of the Crew that finished the Loyalty Mission")
    async def admin_loyalty_end(self, interaction: discord.Interaction, spaceship: discord.Role):
        if not any(r.name == ADMIN_ROLE_NAME for r in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to end this mission.", ephemeral=True)
            return
        
        guild = interaction.guild
        narrator_role = discord.utils.get(guild.roles, name=NARRATOR_ROLE_NAME)
        loyalty_role = discord.utils.get(guild.roles, name=LOYALTY_ROLE_NAME)

        if not narrator_role or not loyalty_role:
            await interaction.response.send_message("Error: 'Crew Narrator' or 'Loyalty Marked' roles not found.", ephemeral=True)
            return

        spaceship_role = spaceship.name
        parts = spaceship_role.split(" ", 1)
        if parts[0].lower() != "spaceship":
            await interaction.response.send_message("Invalid spaceship role format.", ephemeral=True)
            return
        ship_key = parts[1].lower()

        '''
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

        loyalty_nicknames = []
        for member in spaceship.members:
            member_to_mention = [r for r in [loyalty_role] if r in member.roles]
            if member_to_mention:
                loyalty_nicknames.append(member.display_name)

        if loyalty_nicknames:
            rewardedString = f"One Reroll rewarded to {', '.join(loyalty_nicknames)}!"
        else:
            rewardedString = f"No Rerolls rewarded!"


        affected = []
        for member in spaceship.members:
            roles_to_remove = [r for r in [narrator_role, loyalty_role] if r in member.roles]
            if roles_to_remove:
                try:
                    await member.remove_roles(*roles_to_remove, reason="Loyalty Mission ended.")
                    affected.append(member.display_name)
                except discord.Forbidden:
                    continue

        if affected:
            messageString = f"Removed the '{NARRATOR_ROLE_NAME}' and '{LOYALTY_ROLE_NAME}' roles from: {', '.join(affected)}"
        else:
            messageString = f"No members in {spaceship} had any Loyalty Mission roles to remove."

        embed = discord.Embed(
            title=f"Loyalty Mission Ended",
            description=f"The Crew of {spaceship} has completed their loyalty mission.\n\n**{rewardedString}**",
            color=discord.Color.gold()
        )
        embed.set_image(url="https://64.media.tumblr.com/6d3dfbf948c657abf2fa93c0ad0ff836/495d2ace7fab6c1a-03/s540x810/be49d7f4da569d2a61f6d0c5cb78e8c96b668c5a.gif")
        embed.set_footer(text=messageString)

        await interaction.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminLoyaltyMission(bot))