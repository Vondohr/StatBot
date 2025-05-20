import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal

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

        button1 = discord.ui.Button(label=label1, style=discord.ButtonStyle.red)
        async def button1_callback(interaction: discord.Interaction):
            target_roles = ["Rebels", "Imperials", "Hutts"]
            user_roles = [role.name for role in interaction.user.roles]

            member = interaction.guild.get_member(interaction.user.id)
            if not discord.utils.get(member.roles, id=1261788616527708181):
                await interaction.response.send_message("You are not in any Crew!", ephemeral=True)
                return

            if any(role in user_roles for role in target_roles):
                await interaction.response.send_message(f"You have already joined the fight!\n\n**Go to {planet_role} aid your faction!**", ephemeral=True)
                return
            
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

        # Button 2
        button2 = discord.ui.Button(label=label2, style=discord.ButtonStyle.red)
        async def button2_callback(interaction: discord.Interaction):
            target_roles = ["Rebels", "Imperials", "Hutts"]
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

    @app_commands.command(name="admin_send_battle_invite", description="Send a battle invitation embed with buttons to choose a side.")
    @app_commands.describe(planet_role="The role of the planet or moon where the battle is happening")
    @app_commands.describe(factions="Choose factions that are fighting")
    async def send_embed(self, interaction: discord.Interaction, planet_role: str, factions: Literal["Rebels vs Empire", "Rebels vs Hutts", "Hutts vs Empire"]):
        member = interaction.guild.get_member(interaction.user.id)
        if not discord.utils.get(member.roles, id=1260298617818841318):
                await interaction.response.send_message("You are not an Admin!", ephemeral=True)
                return
    
        role = discord.utils.get(interaction.guild.roles, name=planet_role)

        if not role:
            await interaction.response.send_message("Not a valid role!", ephemeral=True)
            return

        try:
            channel_id_int = int(1260348000316817501)
            channel = interaction.guild.get_channel(channel_id_int)
            
            embed = discord.Embed(
                title=f"Battle on {planet_role}!",
                description="Mercenaries needed!\n\n**Pick a side and join the fight!**",
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

async def setup(bot):
    await bot.add_cog(EmbedSender(bot))