import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

DATA_FILE = "message_counts.json"

# --- CONFIGURATION ---
RP_CATEGORY_IDS = [1261294138666651658, 1361750766187970580, 1260704136475967498, 1260571745614823485, 1264938045665185854, 1258379465919041591]  # IDs of RP category channels
NON_RP_CATEGORY_IDS = [1259264566387413003, 1301567802372526080, 1263949872768487475, ]  # IDs of Non-RP category channels
# ---------------------

class MessageCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def add_message(self, category_type):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if today not in self.data:
            self.data[today] = {"RP": 0, "nonRP": 0}
        self.data[today][category_type] += 1
        self.save_data()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.category_id in RP_CATEGORY_IDS:
            self.add_message("RP")
        elif message.channel.category_id in NON_RP_CATEGORY_IDS:
            self.add_message("nonRP")

    def calculate_change(self, current, previous):
        if previous == 0:
            return "∞%" if current > 0 else "0%"
        change = ((current - previous) / previous) * 100

        returnString = ""

        if change > 0:
            returnString = f"{change:+.2f}% ⬆️🟩"
        elif change < 0:
            returnString = f"{change:+.2f}% ⬇️🟥"
        else:
            returnString = f"{change:+.2f}%"

        return returnString

    def get_stats_for_days(self, days):
        today = datetime.utcnow().date()
        stats = []
        for i in range(days):
            day = today - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            stats.append((day_str, self.data.get(day_str, {"RP": 0, "nonRP": 0})))
        stats.reverse()
        return stats

    def get_stats_for_weeks(self, weeks):
        week_data = defaultdict(lambda: {"RP": 0, "nonRP": 0})
        for day_str, counts in self.data.items():
            day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
            iso_year, iso_week, _ = day_date.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            week_data[week_key]["RP"] += counts["RP"]
            week_data[week_key]["nonRP"] += counts["nonRP"]

        sorted_weeks = sorted(week_data.keys())
        last_weeks = sorted_weeks[-weeks:]
        return [(wk, week_data[wk]) for wk in last_weeks]

    def get_stats_for_months(self, months):
        month_data = defaultdict(lambda: {"RP": 0, "nonRP": 0})
        for day_str, counts in self.data.items():
            month_key = day_str[:7]  # YYYY-MM
            month_data[month_key]["RP"] += counts["RP"]
            month_data[month_key]["nonRP"] += counts["nonRP"]

        sorted_months = sorted(month_data.keys())
        last_months = sorted_months[-months:]
        return [(m, month_data[m]) for m in last_months]

    @app_commands.command(name="stats", description="Show message count stats.")
    @app_commands.describe(period_type="Choose day/week/month", amount="How many periods back to show")
    async def stats(self, interaction: discord.Interaction, period_type: str, amount: int):
        if amount > 25 or amount < 1:
            await interaction.response.send_message("Amount must be between 1 and 25.", ephemeral=True) # 0 Days doesn't make sense, and 25 is the maximum amount of fields per embed
            return
        
        period_type = period_type.lower()
        if period_type not in ["days", "weeks", "months"]:
            await interaction.response.send_message("Invalid period type! Use: days, weeks, months", ephemeral=True)
            return

        if period_type == "days":
            stats_data = self.get_stats_for_days(amount)
        elif period_type == "weeks":
            stats_data = self.get_stats_for_weeks(amount)
        else:
            stats_data = self.get_stats_for_months(amount)

        embed = discord.Embed(title=f"📊 Message Stats ({period_type.capitalize()})", color=discord.Color.blue())
        prev_rp = prev_nonrp = None

        for label, counts in stats_data:
            rp = counts["RP"]
            nonrp = counts["nonRP"]

            if prev_rp is None:
                rp_change = "N/A"
                nonrp_change = "N/A"
            else:
                rp_change = self.calculate_change(rp, prev_rp)
                nonrp_change = self.calculate_change(nonrp, prev_nonrp)

            embed.add_field(
                name=label,
                value=f"**RP:** {rp} ({rp_change})\n**Non-RP:** {nonrp} ({nonrp_change})",
                inline=False
            )

            prev_rp, prev_nonrp = rp, nonrp

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MessageCounter(bot))