import discord
import json
from discord.ext import commands
from discord import app_commands

class AdminItemCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_item_create", description="Create a new item (admin only)")
    @app_commands.describe(name="Name of the new item")
    @app_commands.describe(description="Description of the new item")
    @app_commands.describe(amount="How many times should this item be added to your Inventory")
    async def admin_item_create(
        self,
        interaction: discord.Interaction,
        name: app_commands.Range[str, 1, 20],  # min 1, max 20 characters
        description: app_commands.Range[str, 1, 35],  # min 1, max 35 characters
        amount: app_commands.Range[int, 1, 10]  # only 1 to 10 allowed
    ):
        roles = [role for role in interaction.user.roles]

        # Check if user has the Crew role
        if not any(role.name == "Narrators" for role in roles):
            if interaction.user.id != 398850136442404864:
                await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)
                return

        '''
        with open("data.json", "r") as f:
            data = json.load(f)

        inventory_limit = 50
        inventoryUser = data[interaction.user.id]["inventory"]

        if len(inventoryUser) >= inventory_limit:
            await interaction.followup.send(f"You have too many items in your inventory!", ephemeral=True)
            return

        inventoryUser[name] = name
        inventoryUser[name]["Description"] = description
        inventoryUser[name]["Amount"] = amount
        
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)
        '''

        await interaction.response.send_message(
            f"✅ Created item:\n**Name**: `{name}`\n**Description**: `{description}`\n**Amount**: `{amount}`",
            ephemeral=True
        )

        channel_id = 1272509655113011261  # Testing channel
        channel = self.bot.get_channel(channel_id)

        if channel:
            await channel.send(f"{interaction.user.display_name} create a new item: {name}, {description}, {amount}x.")
        else:
            print("Channel not found.")

async def setup(bot):
    await bot.add_cog(AdminItemCreate(bot))