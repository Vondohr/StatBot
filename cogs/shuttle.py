import random
import discord
from discord import app_commands
from discord.ext import commands
import asyncio

VALID_PREFIXES = ["Planet", "Moon"]
WAIT_BEFORE_REVOKE = 1 * 60
# WAIT_BEFORE_REVOKE = 5 * 60

valid_destinations = [
    "Planet Carajam", "Planet Kashyyyk", "Planet Tatooine", "Planet Naboo", "Planet Nal Hutta",
    "Moon Nar Shaddaa", "Planet Ryloth", "Planet Ord Mantell", "Planet Lothal", "Planet Cantonica",
    "Planet Bracca", "Moon Jedha", "Planet Alderaan", "Planet Coruscant"
]

active_shuttles = set()

class CancelButton(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=WAIT_BEFORE_REVOKE)
        self.user = user
        self.cancelled = False
        self.message = None

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This button isn't for you.", ephemeral=True)
            return
        self.cancelled = True
        self.disable_all_items()

        try:
            await interaction.response.edit_message(content="🚫 Shuttle cancelled.", view=self)
        except discord.InteractionResponded:
            pass
        except Exception as e:
            print(f"Error editing message after cancel: {e}")
        self.stop()

    async def on_timeout(self):
        self.disable_all_items()
        try:
            if self.message:
                await self.message.edit(view=self)
        except Exception as e:
            print(f"Error disabling buttons after timeout: {e}")

class Shuttle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def extract_destination(self, role_name: str) -> str:
        for prefix in VALID_PREFIXES:
            if role_name.startswith(prefix + " "):
                return role_name[len(prefix) + 1:]
        return None

    @app_commands.command(name="shuttle", description="Take a shuttle to a planet or moon.")
    @app_commands.describe(location="Choose your destination")
    async def shuttle(self, interaction: discord.Interaction, location: str):
        user_id = interaction.user.id

        if not interaction.channel.name.startswith("「🚀」"):
            await interaction.response.send_message("You can only call Shuttles in Spaceports!", ephemeral=True)
            return

        if user_id in active_shuttles:
            await interaction.response.send_message("You already have a shuttle en route. Please wait until it lands.", ephemeral=True)
            return

        if location not in valid_destinations:
            await interaction.response.send_message("Invalid destination!", ephemeral=True)
            return

        if not any(role.name == "Player" for role in interaction.user.roles):
            await interaction.response.send_message("You are not allowed to call for a Shuttle!", ephemeral=True)
            return

        if any(role.name == "Crew" for role in interaction.user.roles):
            await interaction.response.send_message("You are not allowed to use Shuttles! Jump with your own ship.", ephemeral=True)
            return

        active_shuttles.add(user_id)
        shuttle_duration = random.randint(1, 2)  # or 40–55
        cancel_view = CancelButton(interaction.user)

        embed = discord.Embed(
            title=f"🚀 Shuttle Launch Sequence Initiated for {interaction.user.nick}",
            description=f"Destination: **{location}**\n\nThe shuttle will arrive in 5 minutes. Click **Cancel** to abort.\n\nFlight duration: `{shuttle_duration}` minutes.",
            color=discord.Color.dark_gold()
        )
        embed.set_image(url="https://64.media.tumblr.com/eaeefa3884095ca9c7b7e44b2752693e/eec4ede0fa31de36-5b/s540x810/d8cbdb39737d68d577ac1dab12a9f1c9e52b83f2.gif")

        await interaction.response.send_message(embed=embed, view=cancel_view)
        message = await interaction.original_response()
        cancel_view.message = message

        if cancel_view.cancelled:
            active_shuttles.discard(user_id)
            return

        await asyncio.sleep(WAIT_BEFORE_REVOKE)

        # Refresh the member to ensure fresh roles
        try:
            member = await interaction.guild.fetch_member(user_id)
        except discord.NotFound:
            active_shuttles.discard(user_id)
            return

        # Remove all planet/moon roles
        for role in member.roles:
            if role.name.startswith("Planet") or role.name.startswith("Moon"):
                await member.remove_roles(role)

        # Wait the travel duration
        await asyncio.sleep(shuttle_duration * 60)

        new_role = discord.utils.get(interaction.guild.roles, name=location)
        if new_role:
            try:
                await member.add_roles(new_role)
            except discord.Forbidden:
                await interaction.followup.send("I couldn't assign the destination role.", ephemeral=True)
        else:
            await interaction.followup.send("Destination role not found.", ephemeral=True)
            active_shuttles.discard(user_id)
            return

        destinationLong = self.extract_destination(location)
        if not destinationLong:
            await interaction.followup.send("Invalid role format.", ephemeral=True)
            active_shuttles.discard(user_id)
            return

        destination = destinationLong.replace(" ", "-")
        forum_channel = discord.utils.find(
            lambda c: isinstance(c, discord.ForumChannel) and destination.lower() in c.name.lower(),
            interaction.guild.channels
        )

        if not forum_channel:
            await interaction.followup.send(f"No forum channel containing `{destination}` found.", ephemeral=True)
            active_shuttles.discard(user_id)
            return

        target_thread = None
        async for thread in forum_channel.threads():
            if "🚀" in thread.name:
                target_thread = thread
                break

        if not target_thread:
            await interaction.followup.send(f"No 🚀 thread found in `{forum_channel.name}`.", ephemeral=True)
            active_shuttles.discard(user_id)
            return

        arrival_embed = discord.Embed(
            title=f"{member.display_name} has landed",
            description=f"{member.mention} has arrived at **{location}**.",
            color=discord.Color.blue()
        )
        arrival_embed.set_image(url="https://64.media.tumblr.com/05fb6dde48bb81815d939ee4f7ed000c/eec4ede0fa31de36-c9/s540x810/0fe51ba6ec2bd34a5fc46b247bf34e6a5af18cb4.gif")

        await target_thread.send(embed=arrival_embed)
        active_shuttles.discard(user_id)

    @shuttle.autocomplete("location")
    async def shuttle_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            discord.app_commands.Choice(name=dest, value=dest)
            for dest in valid_destinations if current.lower() in dest.lower()
        ][:25]

async def setup(bot):
    await bot.add_cog(Shuttle(bot))