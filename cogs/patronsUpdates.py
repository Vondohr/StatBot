import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import traceback

class Supporters(commands.Cog):
    """Maintains 3 persistent embeds listing supporters and exposes /refresh_supporters."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # CONFIG: set your channel id here
        self.channel_id: int = 1438517684470939829
        # Optionally set a specific guild id for immediate guild-scoped command registration.
        # If None the cog will attempt to register to the first guild the bot is in.
        self.guild_id: int | None = None

        self.data_file = "supporter_embeds.json"

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

        # load persisted message ids (if any)
        self.load_message_ids()

    # ---------------- JSON storage ----------------
    def load_message_ids(self) -> None:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for title, saved_data in saved.items():
                    if title in self.embeds_config:
                        self.embeds_config[title]["message_id"] = saved_data.get("message_id")
            except Exception as e:
                print(f"[Supporters] Failed to load JSON: {e}")
                traceback.print_exc()

    def save_message_ids(self) -> None:
        try:
            to_save = {t: {"message_id": d["message_id"]} for t, d in self.embeds_config.items()}
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(to_save, f, indent=4)
        except Exception as e:
            print(f"[Supporters] Failed to save JSON: {e}")
            traceback.print_exc()

    # ---------------- cog lifecycle ----------------
    async def cog_load(self) -> None:
        # Wait for bot ready first
        await self.bot.wait_until_ready()
        # Create/find embeds
        await self.ensure_embeds_exist()

        # Register the app command. Prefer guild-scoped (fast) registration.
        try:
            guild_obj = None
            if self.guild_id:
                guild_obj = discord.Object(id=self.guild_id)
            else:
                # try to use first guild the bot is in
                if self.bot.guilds:
                    guild_obj = discord.Object(id=self.bot.guilds[0].id)

            # Add command with guild if possible (instant)
            if guild_obj:
                # avoid duplicate registration
                if not self.bot.tree.get_command("refresh_supporters", guild=guild_obj):
                    self.bot.tree.add_command(self.refresh_supporters, guild=guild_obj)
                await self.bot.tree.sync(guild=guild_obj)
                print(f"[Supporters] Registered /refresh_supporters to guild {guild_obj.id}")
            else:
                # global registration fallback
                if not self.bot.tree.get_command("refresh_supporters"):
                    self.bot.tree.add_command(self.refresh_supporters)
                await self.bot.tree.sync()
                print("[Supporters] Registered /refresh_supporters globally (may take up to 1 hour to appear)")
        except Exception as e:
            print(f"[Supporters] Failed to register/sync app command: {e}")
            traceback.print_exc()

    # ---------------- embed creation / verification ----------------
    async def ensure_embeds_exist(self) -> None:
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"[Supporters] Channel {self.channel_id} not found (bot may not have it cached).")
            return

        # look through recent messages for existing embeds
        try:
            recent = [m async for m in channel.history(limit=100)]
        except discord.Forbidden:
            print(f"[Supporters] Missing permissions to read history in channel {self.channel_id}.")
            return
        except Exception as e:
            print(f"[Supporters] Error fetching channel history: {e}")
            traceback.print_exc()
            return

        found_titles = {m.embeds[0].title: m for m in recent if m.embeds}

        updated = False
        for title, cfg in self.embeds_config.items():
            msg = None
            mid = cfg.get("message_id")
            if mid:
                try:
                    msg = await channel.fetch_message(mid)
                except discord.NotFound:
                    msg = None
                except discord.Forbidden:
                    print(f"[Supporters] Forbidden fetching message id {mid}")
                    msg = None
                except Exception:
                    msg = None

            if not msg:
                if title in found_titles:
                    msg = found_titles[title]
                    cfg["message_id"] = msg.id
                    updated = True
                else:
                    # create embed
                    embed = discord.Embed(title=title, description="*(No supporters yet)*", color=cfg["color"])
                    if cfg.get("image_url"):
                        try:
                            embed.set_image(url=cfg["image_url"])
                        except Exception:
                            # don't fail if image url is invalid
                            pass
                    try:
                        msg = await channel.send(embed=embed)
                        cfg["message_id"] = msg.id
                        updated = True
                    except discord.Forbidden:
                        print(f"[Supporters] Missing permissions to send messages in channel {self.channel_id}.")
                        return
                    except Exception as e:
                        print(f"[Supporters] Failed to send initial embed for {title}: {e}")
                        traceback.print_exc()

        if updated:
            self.save_message_ids()

        # final sync of contents
        await self.update_all_embeds()

    # ---------------- updating embeds ----------------
    async def update_all_embeds(self) -> None:
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"[Supporters] Channel {self.channel_id} not found when updating.")
            return
        guild = channel.guild
        if not guild:
            print("[Supporters] Channel not attached to a guild? Aborting update.")
            return

        for title in self.embeds_config.keys():
            try:
                await self.update_embed_for_category(guild, title)
            except Exception as e:
                print(f"[Supporters] Error updating embed '{title}': {e}")
                traceback.print_exc()

    async def update_embed_for_category(self, guild: discord.Guild, title: str) -> None:
        cfg = self.embeds_config[title]
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        message_id = cfg.get("message_id")
        if not message_id:
            return

        # gather members for all roles in this category
        members = set()
        for rname in cfg["roles"]:
            role = discord.utils.get(guild.roles, name=rname)
            if role:
                members.update([m for m in role.members if not m.bot])

        members_sorted = sorted(members, key=lambda m: m.display_name.lower())
        lines = [f"- {m.mention}" for m in members_sorted]
        description = "\n".join(lines) if lines else "*(No supporters yet)*"

        # Ensure embed description < 4096 chars (give some safety margin)
        if len(description) > 4000:
            description = description[:4000]
            # try to cut at last newline to avoid mid-line truncation
            last_nl = description.rfind("\n")
            if last_nl > 0:
                description = description[:last_nl]
            description += "\n*(List truncated)*"

        embed = discord.Embed(title=title, description=description, color=cfg["color"])
        if cfg.get("image_url"):
            try:
                embed.set_image(url=cfg["image_url"])
            except Exception:
                pass

        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(embed=embed)
        except discord.NotFound:
            # recreate and persist id
            try:
                new_msg = await channel.send(embed=embed)
                cfg["message_id"] = new_msg.id
                self.save_message_ids()
            except discord.Forbidden:
                print(f"[Supporters] Missing send permission to recreate embed in channel {self.channel_id}.")
        except discord.Forbidden:
            print(f"[Supporters] Missing permission to fetch/edit message {message_id} in channel {self.channel_id}.")
        except Exception as e:
            print(f"[Supporters] Unexpected error editing message {message_id}: {e}")
            traceback.print_exc()

    # ---------------- events ----------------
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        before_roles = {r.name for r in before.roles}
        after_roles = {r.name for r in after.roles}
        changed = before_roles ^ after_roles
        relevant = {r for cfg in self.embeds_config.values() for r in cfg["roles"]}
        if any(r in relevant for r in changed):
            # debounced update is possible but we update immediately here
            await self.update_all_embeds()

    # ---------------- slash command ----------------
    @app_commands.command(name="refresh_supporters", description="Manually refresh the supporter embeds.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def refresh_supporters(self, interaction: discord.Interaction) -> None:
        """Admin-only manual refresh."""
        await interaction.response.defer(ephemeral=True)
        try:
            await self.update_all_embeds()
            await interaction.followup.send("✅ Supporter embeds refreshed!", ephemeral=True)
        except Exception as e:
            print(f"[Supporters] Error in refresh_supporters: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("⚠️ Failed to refresh supporter embeds.", ephemeral=True)
            except Exception:
                pass

    # ---------------- cog-level app command errors ----------------
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        # Handle missing permissions for app commands
        if isinstance(error, app_commands.MissingPermissions):
            try:
                await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
            except Exception:
                try:
                    await interaction.followup.send("🚫 You don't have permission to use this command.", ephemeral=True)
                except Exception:
                    pass
            return

        # Fallback: log and notify
        print(f"[Supporters] App command error: {error}")
        traceback.print_exc()
        try:
            await interaction.response.send_message("⚠️ An error occurred while executing the command.", ephemeral=True)
        except Exception:
            try:
                await interaction.followup.send("⚠️ An error occurred while executing the command.", ephemeral=True)
            except Exception:
                pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Supporters(bot))