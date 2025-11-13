import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class Supporters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1438517684470939829
        self.data_file = "supporter_embeds.json"

        # === CONFIG ===
        self.embeds_config = {
            "Ultra Supporters": {
                "roles": ["Ultra Supporter"],
                "color": discord.Color.gold(),
                "image_url": "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607000547480/UltraSupporter.gif",
                "message_id": None
            },
            "Top Supporters & Boosters": {
                "roles": ["Top Supporter", "Server Booster"],
                "color": discord.Color.blurple(),
                "image_url": "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607398875246/TopSupporter.gif",
                "message_id": None
            },
            "Supporters": {
                "roles": ["Supporter"],
                "color": discord.Color.green(),
                "image_url": "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607801794580/Supporter.gif",
                "message_id": None
            },
        }

        self.load_message_ids()

    # ---------- JSON STORAGE ----------
    def load_message_ids(self):
        """Load message IDs from file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for title, saved_data in saved.items():
                    if title in self.embeds_config:
                        self.embeds_config[title]["message_id"] = saved_data.get("message_id")
            except Exception as e:
                print(f"[Supporters] Failed to load JSON: {e}")

    def save_message_ids(self):
        """Save message IDs to file."""
        data = {t: {"message_id": d["message_id"]} for t, d in self.embeds_config.items()}
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[Supporters] Failed to save JSON: {e}")

    # ---------- STARTUP ----------
    async def cog_load(self):
        # Wait for bot ready, ensure embeds exist and register app command
        await self.bot.wait_until_ready()
        await self.ensure_embeds_exist()

        # Ensure the slash command is registered in the tree and synced
        # (this helps the command appear reliably)
        try:
            # Add the command to the tree only if not present
            if not self.bot.tree.get_command("refresh_supporters"):
                self.bot.tree.add_command(self.refresh_supporters)
            # Sync command tree so the command becomes visible
            await self.bot.tree.sync()
        except Exception as e:
            # Do not crash startup if sync fails; log for debugging
            print(f"[Supporters] Failed to register/sync app command: {e}")

    async def ensure_embeds_exist(self):
        """Make sure the thank-you channel contains all embeds."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"[Supporters] Channel {self.channel_id} not found.")
            return

        # Collect recent messages to look for existing embeds with titles
        messages = [m async for m in channel.history(limit=50)]
        found_titles = {m.embeds[0].title: m for m in messages if m.embeds}

        updated = False

        for title, data in self.embeds_config.items():
            msg = None
            # Try to fetch stored message
            if data["message_id"]:
                try:
                    msg = await channel.fetch_message(data["message_id"])
                except discord.NotFound:
                    msg = None
                except discord.Forbidden:
                    msg = None

            # Try to find by title if no valid message found
            if not msg:
                if title in found_titles:
                    msg = found_titles[title]
                    data["message_id"] = msg.id
                    updated = True
                else:
                    embed = discord.Embed(
                        title=title,
                        description="*(No supporters yet)*",
                        color=data["color"]
                    )
                    if data.get("image_url"):
                        embed.set_image(url=data["image_url"])
                    msg = await channel.send(embed=embed)
                    data["message_id"] = msg.id
                    updated = True

        if updated:
            self.save_message_ids()

        await self.update_all_embeds()

    # ---------- UPDATES ----------
    async def update_all_embeds(self):
        """Update all supporter embeds."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return
        guild = channel.guild

        for title in self.embeds_config.keys():
            await self.update_embed_for_category(guild, title)

    async def update_embed_for_category(self, guild: discord.Guild, title: str):
        """Refresh one embed with updated member lists."""
        channel = self.bot.get_channel(self.channel_id)
        data = self.embeds_config[title]
        message_id = data["message_id"]

        if not message_id:
            return

        # Collect members from roles
        members = set()
        for role_name in data["roles"]:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                members.update([m for m in role.members if not m.bot])

        members_text = "\n".join(f"- {m.mention}" for m in sorted(members, key=lambda x: x.name.lower())) \
            if members else "*(No supporters yet)*"

        embed = discord.Embed(title=title, description=members_text, color=data["color"])
        if data.get("image_url"):
            embed.set_image(url=data["image_url"])

        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(embed=embed)
        except discord.NotFound:
            new_msg = await channel.send(embed=embed)
            data["message_id"] = new_msg.id
            self.save_message_ids()
        except discord.Forbidden:
            print(f"[Supporters] Missing permissions to fetch/edit messages in channel {self.channel_id}.")

    # ---------- EVENTS ----------
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Trigger when supporter roles change."""
        before_roles = {r.name for r in before.roles}
        after_roles = {r.name for r in after.roles}
        changed_roles = before_roles ^ after_roles

        all_relevant_roles = {r for data in self.embeds_config.values() for r in data["roles"]}
        if any(r in all_relevant_roles for r in changed_roles):
            await self.update_all_embeds()

    # ---------- SLASH COMMAND ----------
    @app_commands.command(name="refresh_supporters", description="Manually refresh the supporter embeds.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def refresh_supporters(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.update_all_embeds()
        await interaction.followup.send("✅ Supporter embeds have been refreshed!", ephemeral=True)

    # ---------- APP COMMAND ERROR HANDLING ----------
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Cog-level handler for app command errors.
        This handles MissingPermissions for the refresh command and logs other errors.
        """
        # MissingPermissions raised by app_commands.checks(has_permissions=...) lands here
        if isinstance(error, app_commands.MissingPermissions):
            try:
                await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
            except Exception:
                # Interaction may already be responded to; attempt followup
                try:
                    await interaction.followup.send("🚫 You don't have permission to use this command.", ephemeral=True)
                except Exception:
                    pass
            return

        # Fallback: log and (if possible) notify caller
        print(f"[Supporters] App command error: {error}")
        try:
            await interaction.response.send_message("⚠️ An error occurred while executing the command.", ephemeral=True)
        except Exception:
            try:
                await interaction.followup.send("⚠️ An error occurred while executing the command.", ephemeral=True)
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(Supporters(bot))