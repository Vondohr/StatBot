import discord
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

class ButtonView(discord.ui.View):
    def __init__(self, factions, planet_role):
        super().__init__(timeout=86400)

        if factions == "Rebels vs Empire":
            label1 = "Rebels"
            label2 = "Imperials"
        elif factions == "Rebels vs Hutts":
            label1 = "Rebels"
            label2 = "Hutts"
        elif factions == "Hutts vs Empire":
            label1 = "Hutts"
            label2 = "Imperials"
        elif factions == "Empire vs Czerkans":
            label1 = "Imperials"
            label2 = "Czerkans"
        elif factions == "Czerkans vs Hutts":
            label1 = "Czerkans"
            label2 = "Hutts"
        elif factions == "Czerkans vs Rebels":
            label1 = "Czerkans"
            label2 = "Rebels"
        elif factions == "The Draeth":
            label1 = "Fight!"
            label2 = "EMPTY"

        button1 = discord.ui.Button(label=label1, style=discord.ButtonStyle.red)
        async def button1_callback(interaction: discord.Interaction):
            target_roles = ["Rebels", "Imperials", "Hutts", "Czerkans", "Hunters"]
            user_roles = [role.name for role in interaction.user.roles]

            member = interaction.guild.get_member(interaction.user.id)
            if not discord.utils.get(member.roles, id=1261788616527708181):
                if not discord.utils.get(member.roles, id=1292841133835292702):
                    await interaction.response.send_message("You cannot take part in Battles yet! Find a Crew or create a Character!", ephemeral=True)
                    return

            if any(role in user_roles for role in target_roles):
                await interaction.response.send_message(f"You have already joined the fight!\n\n**Go to {planet_role} to aid your faction!**", ephemeral=True)
                return
            
            if button1.label == "Fight!":
                role_name = "Hunters"
            else:
                role_name = button1.label
            
            guild = interaction.guild
            member = interaction.user
            role = discord.utils.get(guild.roles, name=role_name)
            planet = discord.utils.get(guild.roles, name=planet_role)

            if role:
                await member.add_roles(role, planet)
                await interaction.response.send_message(f"You are now fighting for the **{role.name}**!\n\n**Go to {planet_role} to aid your faction!**", ephemeral=True)
            else:
                await interaction.response.send_message(f"Role **{role_name}** not found. Contact the mods!", ephemeral=True)
            
        button1.callback = button1_callback
        self.add_item(button1)

        if not label2 == "EMPTY":
            # Button 2
            button2 = discord.ui.Button(label=label2, style=discord.ButtonStyle.red)
            async def button2_callback(interaction: discord.Interaction):
                target_roles = ["Rebels", "Imperials", "Hutts", "Czerkans"]
                user_roles = [role.name for role in interaction.user.roles]

                member = interaction.guild.get_member(interaction.user.id)
                if not discord.utils.get(member.roles, id=1261788616527708181):
                    await interaction.response.send_message("You are not in any Crew!", ephemeral=True)
                    return

                if any(role in user_roles for role in target_roles):
                    await interaction.response.send_message(f"You have already joined the fight!\n\n**Go to {planet_role} to aid your faction!**", ephemeral=True)
                    return

                role_name = button2.label
                guild = interaction.guild
                member = interaction.user
                role = discord.utils.get(guild.roles, name=role_name)
                planet = discord.utils.get(guild.roles, name=planet_role)

                if role:
                    await member.add_roles(role, planet)
                    await interaction.response.send_message(f"You are now fighting for the **{role.name}**!\n\n**Go to {planet_role} to aid your faction!**", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Role **{role_name}** not found. Contact the mods!", ephemeral=True)

            button2.callback = button2_callback
            self.add_item(button2)

    async def on_timeout(self):
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True

            try:
                await self.message.edit(view=self)
            except Exception as e:
                print(f"Failed to disable buttons: {e}")

class EmbedSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_send_battle_invite", description="Send a battle invitation embed with buttons to choose a side. Current channel will be used.")
    @app_commands.describe(planet_role="The role of the planet or moon where the battle is happening")
    @app_commands.describe(factions="Choose factions that are fighting")
    async def send_embed(self, interaction: discord.Interaction, planet_role: str, factions: Literal["Rebels vs Empire", "Rebels vs Hutts", "Hutts vs Empire", "Empire vs Czerkans", "Czerkans vs Hutts", "Czerkans vs Rebels", "The Draeth"]):
        member = interaction.guild.get_member(interaction.user.id)
        if not discord.utils.get(member.roles, id=1260298617818841318):
                await interaction.response.send_message("You are not an Admin!", ephemeral=True)
                return
    
        role = discord.utils.get(interaction.guild.roles, name=planet_role)

        if not role:
            await interaction.response.send_message("Not a valid role!", ephemeral=True)
            return

        try:
            channel_id_int = int(interaction.channel_id)
            channel = interaction.guild.get_channel(channel_id_int)

            if factions == "The Draeth":
                descriptionText = "Bounty Hunter's Guild hub is under attack by **The Draeth!**\n\n**Join the fight!**\n\n**Reward**\n400 ᖬ\n\nDuration of the event\n2 days (expected)"
            else:
                descriptionText = "Mercenaries needed!\n\n**Pick a side and join the fight!**\n\n**Reward**\n400 ᖬ\n\nDuration of the event\n2 days (expected)"
            
            embed = discord.Embed(
                title=f"Battle on {planet_role}!",
                description=descriptionText,
                color=discord.Color.brand_red(),
            )
            if factions == "The Draeth":
                embed.set_image(url="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGFmcm5laTFvbWNncTVudGU5MnA2ZXNyM2FpNG14MzhwZzUzZGxrMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9hCnOTQMC4hXNoKzZ6/giphy.gif")
            else:
                embed.set_image(url="https://www.techspot.com/articles-info/1095/images/2015-11-21-image.gif")
            embed.set_footer(text="You can only join the fight for the next 24 hours!")

            view = ButtonView(factions, planet_role)
            message = await channel.send(embed=embed, view=view)
            view.message = message

            await interaction.response.send_message(f"Embed sent to {channel.mention}.", ephemeral=True)

        except ValueError:
            await interaction.response.send_message("Please provide a valid numeric channel ID.", ephemeral=True)

    # Define choices for location in the battle command
    @send_embed.autocomplete("planet_role")
    async def send_embed_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            discord.app_commands.Choice(name=dest, value=dest)
            for dest in valid_destinations if current.lower() in dest.lower()
        ][:25]  # Limit to 25 choices, the maximum for Discord

async def setup(bot):
    await bot.add_cog(EmbedSender(bot))