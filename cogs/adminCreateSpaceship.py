from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

FORUM_CATEGORY_ID = 1260704136475967498
NARRATORS_ROLE_ID = 1260298617818841318
ASSETS_DIR = Path(__file__).with_suffix("").parent / "assets"

PREDEFINED_POSTS = {
    "Cockpit": "Cockpit.gif",
    "Common Room": "CommonRoom.gif",
    "Crew Quarters": "CrewQuarters.gif",
    "Engineering": "Engineering.gif",
    "Captain's Quarters": "CaptainsQuarters.gif",
    "Gunner Bay": "GunnerBay.gif",
    "OOC Lounge (Discussions & Planning)": "OOCLounge.gif",
}

def build_overwrites(guild: discord.Guild, narrators_role: discord.Role, spaceship_role: discord.Role) -> dict:
    everyone = discord.PermissionOverwrite(
        view_channel=False,
        manage_channels=False,
        manage_permissions=False,
        manage_webhooks=False,
        create_instant_invite=False,
        create_public_threads=False,
        send_messages_in_threads=False,
        send_messages=False,
        embed_links=False,
        attach_files=False,
        add_reactions=False,
        use_external_emojis=False,
        use_external_stickers=False,
        mention_everyone=False,
        manage_messages=False,
        manage_threads=False,
        read_message_history=False,
        send_tts_messages=False,
        send_voice_messages=False,
        use_application_commands=False,
    )

    narrators = discord.PermissionOverwrite(
        view_channel=True,
        manage_channels=False,
        manage_permissions=False,
        manage_webhooks=False,
        create_instant_invite=False,
        create_public_threads=False,
        create_private_threads=False,
        send_messages_in_threads=True,
        send_messages=False,
        embed_links=True,
        attach_files=True,
        add_reactions=True,
        use_external_emojis=True,
        use_external_stickers=True,
        mention_everyone=False,
        manage_messages=False,
        manage_threads=False,
        read_message_history=True,
        send_tts_messages=True,
        send_voice_messages=True,
        use_application_commands=True,
        use_embedded_activities=True,
    )

    spaceship = discord.PermissionOverwrite(
        view_channel=True,
        manage_channels=False,
        manage_permissions=False,
        manage_webhooks=False,
        create_instant_invite=False,
        create_public_threads=False,
        create_private_threads=False,
        send_messages_in_threads=True,
        send_messages=False,
        embed_links=True,
        attach_files=True,
        add_reactions=True,
        use_external_emojis=True,
        use_external_stickers=True,
        mention_everyone=False,
        manage_messages=False,
        manage_threads=False,
        read_message_history=True,
        send_tts_messages=True,
        send_voice_messages=True,
        use_application_commands=True,
        use_embedded_activities=True,
    )

    return {
        guild.default_role: everyone,
        narrators_role: narrators,
        spaceship_role: spaceship,
    }


def sanitize_name(s: str) -> str:
    s = " ".join(s.split())
    return s[:90].capitalize()

class AdminCreateSpaceship(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="admin_create_spaceship", description="Create a new spaceship forum with default rooms")
    @app_commands.describe(spaceship_name="Name of the new spaceship", prefix="Emoji for the forum name, defaults to ❓")
    async def admin_create_spaceship(self, interaction: discord.Interaction, spaceship_name: str, prefix: str = "❓"):
        await interaction.response.defer(ephemeral=True)

        narrators = interaction.guild.get_role(NARRATORS_ROLE_ID)
        if not narrators or narrators not in interaction.user.roles:
            await interaction.followup.send("You are not allowed to use this command!", ephemeral=True)
            return

        spaceship_name = sanitize_name(spaceship_name)
        if not spaceship_name:
            await interaction.followup.send("Invalid spaceship name.", ephemeral=True)
            return

        missing = [fn for fn in PREDEFINED_POSTS.values() if not (ASSETS_DIR / fn).is_file()]
        if missing:
            await interaction.followup.send(f"Missing asset files: {', '.join(missing)}", ephemeral=True)
            return

        category = interaction.guild.get_channel(FORUM_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.followup.send("Error: Category ID is invalid.", ephemeral=True)
            return

        existing_forum = discord.utils.get(category.channels, name=f"【{prefix}】{spaceship_name}")
        if existing_forum:
            await interaction.followup.send(f"A forum for **{spaceship_name}** already exists.", ephemeral=True)
            return

        try:
            spaceship_role_name = f"Spaceship {spaceship_name}"
            spaceship_role = discord.utils.get(interaction.guild.roles, name=spaceship_role_name)

            if not spaceship_role:
                spaceship_role = await interaction.guild.create_role(
                    name=spaceship_role_name,
                    reason=f"Role for spaceship '{spaceship_name}' created by {interaction.user}"
                )


            narrators_role = interaction.guild.get_role(NARRATORS_ROLE_ID)
            overwrites = build_overwrites(interaction.guild, narrators_role, spaceship_role)

            forum = await interaction.guild.create_forum(
                name=f"【{prefix}】{spaceship_name}",
                category=category,
                overwrites=overwrites,
                reason=f"Created by {interaction.user} via /admin_create_spaceship"
)

            for post_name, gif_filename in PREDEFINED_POSTS.items():
                fp = ASSETS_DIR / gif_filename
                with fp.open("rb") as f:
                    file = discord.File(f, filename=gif_filename)
                    await forum.create_thread(
                        name=post_name,
                        file=file
                    )

            try:
                await interaction.user.add_roles(spaceship_role, reason=f"Creator of '{spaceship_name}'")
            except Exception:
                pass

        except Exception as e:
            try:
                if 'forum' in locals():
                    await forum.delete(reason="Rollback due to error during setup")
            finally:
                try:
                    if 'spaceship_role' in locals():
                        await spaceship_role.delete(reason="Rollback due to error during setup")
                finally:
                    await interaction.followup.send(f"Setup failed: {e}", ephemeral=True)
                    return

        await interaction.followup.send(
            f"Spaceship **{spaceship_name}** created with default rooms! Role `{spaceship_role_name}` also created and assigned.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCreateSpaceship(bot))
