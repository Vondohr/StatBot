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
            await interaction.response.send_message(
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
        
        # CHECK FOR RUNNING BOUNTIES NEEDED

        embed = discord.Embed(
            title=f"Loyalty Mission",
            description=f"Loyalty Mission prepared for {player.mention}. An Admin must start it.",
            color=discord.Color.gold()
        )
        embed.set_image(url="https://64.media.tumblr.com/18d4a604b3b44ff8c6d2556a8da8cb34/4c683c0be10a5deb-22/s500x750/84fa248322bdf0a4080354615487c08a0bb94817.gif")
        embed.set_footer(text="The whole Crew can take part in this Mission!")
        view = LoyaltyMissionView(interaction.user, player)

        await interaction.channel.send(content="One of the <@&1260298617818841318> will be here with you shortly to start the Mission.", embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(LoyaltyMission(bot))