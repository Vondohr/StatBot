import sqlite3

import discord
from discord.ext import commands
from discord import app_commands

# CHANGE THESE ROLE NAMES TO MATCH YOUR SERVER
NARRATOR_ROLE_NAME = "Crew Narrator"
LOYALTY_ROLE_NAME = "Loyalty Marked"
ADMIN_ROLE_NAME = "Narrators"

class LoyaltyMissionView(discord.ui.View):
    def __init__(self, author: discord.Member, target: discord.Member):
        super().__init__(timeout=None)
        self.author = author
        self.target = target

    @discord.ui.button(label="Start the Loyalty Mission", style=discord.ButtonStyle.primary)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has Admin role
        if not any(r.name == ADMIN_ROLE_NAME for r in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to start this mission.", ephemeral=True)
            return
        
        '''
        user = self.author
        user_roles = [role.name for role in user.roles]
        spaceship_role = next((r for r in user_roles if r.startswith("Spaceship")), None)
        if not spaceship_role:
            await interaction.followup.send("Player has no Crew!", ephemeral=True)
            return

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

        if active_bounty != "undefined":
            conn.close()
            await interaction.followup.send("The Crew already has an active bounty.", ephemeral=True)
            return

        name_of_bounty = "loyalty_mission"

        cur.execute(
            "UPDATE ship_data SET active_bounty=? WHERE id=?",
            (name_of_bounty, ship_key),
        )
        conn.commit()
        conn.close()
        '''

        guild = interaction.guild
        narrator_role = discord.utils.get(guild.roles, name=NARRATOR_ROLE_NAME)
        loyalty_role = discord.utils.get(guild.roles, name=LOYALTY_ROLE_NAME)

        if not narrator_role or not loyalty_role:
            await interaction.response.send_message("Error: Roles not found on this server.", ephemeral=True)
            return

        # Assign roles
        try:
            await self.author.add_roles(narrator_role)
            await self.target.add_roles(loyalty_role)

            # Disable the button
            button.disabled = True
            await interaction.response.edit_message(view=self)

            await interaction.channel.send(
                f"✅ Loyalty Mission started! {self.author.mention} is now {narrator_role.mention}, and {self.target.mention} is now {loyalty_role.mention}."
            )
        except discord.Forbidden:
            await interaction.response.send_message("I don’t have permission to manage roles.", ephemeral=True)


class LoyaltyMission(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="loyalty_mission", description="Start a Loyalty Mission for your Crewmate.")
    async def loyalty_mission(self, interaction: discord.Interaction, player: discord.Member):
        
        if not any(role.name == "Crew" for role in interaction.user.roles):
            await interaction.response.send_message("You are not in any Crew! Join one first.", ephemeral=True)
            return
        
        if interaction.channel.category_id != 1260704136475967498:
            await interaction.response.send_message("Loyalty Missions can only be started from your Spaceship!", ephemeral=True)
            return
        
        # CHECK FOR RUNNING BOUNTIES NEEDED
        '''
        user = interaction.user
        user_roles = [role.name for role in user.roles]
        spaceship_role = next((r for r in user_roles if r.startswith("Spaceship")), None)
        if not spaceship_role:
            await interaction.followup.send("You have no crew! You cannot accept bounties.", ephemeral=True)
            return

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

        if active_bounty != "undefined":
            conn.close()
            await interaction.followup.send("You already have an active bounty! Finish the current one first.", ephemeral=True)
            return
        '''

        embed = discord.Embed(
            title=f"Loyalty Mission",
            description=f"Loyalty Mission prepared for {player.mention}. {interaction.user.mention} will be the Crew Narrator\n\n**One of the server Admins/Narrators must start the Mission.**",
            color=discord.Color.gold()
        )
        embed.set_image(url="https://64.media.tumblr.com/18d4a604b3b44ff8c6d2556a8da8cb34/4c683c0be10a5deb-22/s500x750/84fa248322bdf0a4080354615487c08a0bb94817.gif")
        embed.set_footer(text="The whole Crew can take part in this Mission!")
        view = LoyaltyMissionView(interaction.user, player)

        await interaction.channel.send(content="One of the <@&1260298617818841318> will be here with you shortly to start the Mission.", embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(LoyaltyMission(bot))