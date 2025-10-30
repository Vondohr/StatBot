import asyncio
import json
import random
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

# from utils.executeChecks import rp_only

# SOME PARTS ARE COMMENTED OUT!!!!!!!!!!

class RerollButton(discord.ui.View):
    def __init__(self, bot, user: discord.User, cog, interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.cog = cog
        self.interaction = interaction
        self.add_item(self.RerollButtonItem(self))

    class RerollButtonItem(discord.ui.Button):
        def __init__(self, parent_view):
            super().__init__(label="Reroll (X/Y Remaining)", style=discord.ButtonStyle.danger)
            self.parent_view = parent_view

        async def callback(self, interaction: discord.Interaction):
            # Only allow the user who initiated the command
            if interaction.user.id != self.parent_view.user.id:
                await interaction.response.send_message("You cannot use this button.", ephemeral=True)
                return

            # Disable button
            self.disabled = True
            await interaction.message.edit(view=self.parent_view)

            # Modify original embed (strikethrough + new gif)
            embed = interaction.message.embeds[0]
            embed.title = f"~~{embed.title}~~ REROLLED!"
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1433544328751611955/CrystalBlue.gif")
            await interaction.message.edit(embed=embed, view=self.parent_view)

            # Do the reroll with 0 Glitterstims
            await asyncio.sleep(2)
            await self.parent_view.cog.roll(self.parent_view.interaction, glitterstims=0)


class RollDiceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll_testing", description="Roll a mission dice using optional Glitterstims (0-4)")
    @app_commands.describe(glitterstims="Number of Glitterstims to use (0-4)")
    # @rp_only()
    async def roll(self, interaction: discord.Interaction, glitterstims: int = 0):
        await interaction.response.defer(ephemeral=False)

        user = interaction.user
        user_roles = [r.name for r in user.roles]
        if "Crew" not in user_roles:
            await interaction.followup.send("You are not allowed to roll the dice!", ephemeral=True)
            return

        if glitterstims < 0 or glitterstims > 4:
            await interaction.followup.send("Enter a valid Glitterstim value! The value must be between 0 and 4.", ephemeral=True)
            return

        spaceship_role = next((r.name for r in user.roles if r.name.startswith("Spaceship")), None)
        if not spaceship_role:
            await interaction.followup.send("You are not assigned to a spaceship.", ephemeral=True)
            return
        ship_key = spaceship_role.split(" ", 1)[-1].lower()

        cconn = sqlite3.connect("data/character_data.db")
        ccur = cconn.cursor()
        aconn = sqlite3.connect("data/character_data/activeBonuses.db")
        acur = aconn.cursor()
        ccur.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                credits INTEGER DEFAULT 0,
                glitterstims INTEGER DEFAULT 0
            )
        """)
        aconn.execute("""
            CREATE TABLE IF NOT EXISTS activeBonuses (
                id TEXT PRIMARY KEY,
                Owner TEXT,
                Name TEXT,
                Description TEXT,
                BonusMin INTEGER,
                BonusMax INTEGER,
                Uses INTEGER
            )
        """)
        cols = {r[1] for r in ccur.execute("PRAGMA table_info(characters)").fetchall()}
        if "glitterstims" not in cols:
            ccur.execute("ALTER TABLE characters ADD COLUMN glitterstims INTEGER DEFAULT 0")
        uid = str(user.id)
        row = ccur.execute("SELECT credits, glitterstims FROM characters WHERE id = ?", (uid,)).fetchone()
        if not row:
            cconn.close()
            await interaction.followup.send("You do not have a character yet.", ephemeral=True)
            return

        acur.execute("SELECT Name, Description, BonusMin, BonusMax, Uses FROM activeBonuses WHERE Owner = ?", (uid,))
        credits, glitter_have = row
        bonuses = {r[0]: {"Description": r[1], "BonusMin": r[2], "BonusMax": r[3], "Uses": r[4]} for r in acur.fetchall()}

        sconn = sqlite3.connect("data/ship_data.db")
        scur = sconn.cursor()
        scur.execute("""
            CREATE TABLE IF NOT EXISTS ships (
                id TEXT PRIMARY KEY,
                dice INTEGER,
                dice_sides INTEGER,
                failures INTEGER,
                active_bounty TEXT
            )
        """)
        srow = scur.execute("SELECT dice, dice_sides, failures FROM ships WHERE id = ?", (ship_key,)).fetchone()
        if not srow:
            sconn.close()
            cconn.close()
            await interaction.followup.send("Ship data not found.", ephemeral=True)
            return

        dice, dice_sides, failures = srow if srow else (35, 35, 0)
        dice = dice if dice is not None else 35
        dice_sides = dice_sides if dice_sides is not None else 35
        failures = failures if failures is not None else 0

        if glitter_have < glitterstims:
            cconn.close()
            sconn.close()
            await interaction.followup.send(f"You don't have that many Glitterstims! You currently have **{glitter_have}** left.", ephemeral=True)
            return

        bonus_min = 0
        bonus_max = 0
        for b in list(bonuses.values()):
            try:
                bonus_min += int(b.get("BonusMin", 0) or 0)
                bonus_max += int(b.get("BonusMax", 0) or 0)
            except:
                pass
        for key in list(bonuses.keys()):
            b = bonuses[key]
            uses = int(b.get("Uses", 1) or 1) - 1
            b["Uses"] = uses

        roll = random.randint(1 + bonus_min, dice + bonus_max)
        total = roll + glitterstims
        result = "Success"
        if total < 6:
            if roll <= 1:
                result = "Crit Fail"
            else:
                result = "Fail"

        image_map = {
            "Success": "https://cdn.discordapp.com/attachments/1422602593179271189/1433544331977035897/CrystalGreen.gif",
            "Fail": "https://cdn.discordapp.com/attachments/1422602593179271189/1433544330940911677/CrystalRed.gif",
            "Crit Fail": "https://cdn.discordapp.com/attachments/1422602593179271189/1433544330416488518/CrystalBlack.gif"
        }
        pre_image = image_map.get(result)

        embed_pre = discord.Embed(
            title=f"{user.display_name} is rolling the dice!",
            color=discord.Color.dark_embed()
        )
        embed_pre.set_image(url=pre_image)
        roll_msg = await interaction.followup.send(embed=embed_pre, wait=True)
        await asyncio.sleep(4.7)

        if result != "Success":
            failures = (failures or 0) + 2
            new_dice = max((dice_sides or 35) - failures, 10)
            scur.execute("UPDATE ships SET dice = ?, failures = ? WHERE id = ?", (new_dice, failures, ship_key))
            dice = new_dice
        else:
            if dice > 11:
                dice = dice - 1
                scur.execute("UPDATE ships SET dice = ? WHERE id = ?", (dice, ship_key))
        sconn.commit()
        sconn.close()

        if not (roll <= 1 and total < 6):
            glitter_have -= glitterstims

        ccur.execute("UPDATE characters SET glitterstims = ? WHERE id = ?", (glitter_have, uid))
        cconn.commit()
        cconn.close()

        for name, b in bonuses.items():
            try:
                new_uses = int(b.get("Uses", 0) or 0)
            except Exception:
                new_uses = 0
            acur.execute("UPDATE activeBonuses SET Uses = ? WHERE Owner = ? AND Name = ?", (new_uses, uid, name,))

        acur.execute("DELETE FROM activeBonuses WHERE Owner = ? AND (CAST(Uses AS INTEGER) IS NULL OR Uses <= 0)", (uid,))
        aconn.commit()
        aconn.close()

        color = discord.Color.green()
        title = "SUCCESS"
        image_url = "https://cdn.discordapp.com/attachments/1422602593179271189/1433544331507138741/CrystalGreenOnly.gif"

        if result == "Fail":
            color = discord.Color.red()
            title = "FAIL"
            image_url = "https://cdn.discordapp.com/attachments/1422602593179271189/1433544329313652846/CrystalRedOnly.gif"
        if result == "Crit Fail":
            color = discord.Color.default()
            title = "CRITICAL FAIL"
            image_url = "https://cdn.discordapp.com/attachments/1422602593179271189/1433544329934274710/CrystalBlackOnly.gif"

        embed = discord.Embed(title=title, color=color)
        embed.description = (
            f"**{roll}** (your roll) + **{glitterstims}** (Glitterstims applied) = **{total}**\n\n"
            f"The number of sides of the dice is now **{dice}**.\n"
            f"You and your crew have **{(failures or 0) // 2}** Failures so far in this mission."
        )
        embed.set_footer(text=f"{user.display_name}'s roll")
        embed.set_image(url=image_url)

        # If result ≤ 5, add reroll button
        view = None
        if total <= 5:
            view = RerollButton(self.bot, user, self, interaction)

        await roll_msg.edit(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(RollDiceCommand(bot))