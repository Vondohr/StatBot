import discord
from discord.ext import commands
from discord import app_commands

class EmbedCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_embed_create", description="Create a custom embed")
    @app_commands.describe(
        title="Title of the embed",
        description="Main body text. \ n (without space) for a new line",
        footer="Footer text",
        thumbnail="Thumbnail URL",
        image="Main image URL",
        color="Hex color code (e.g. #FF0000)"
    )
    async def embed_create(self, interaction: discord.Interaction,
                            title: str = None,
                            description: str = None,
                            footer: str = None,
                            thumbnail: str = None,
                            image: str = None,
                            color: str = None):

        member = interaction.guild.get_member(interaction.user.id)
        if not discord.utils.get(member.roles, id=1260298617818841318):
                await interaction.response.send_message("You are not an Admin!", ephemeral=True)
                return

        embed_color = discord.Color.default()
        if color:
            try:
                embed_color = discord.Color(int(color.strip("#"), 16))
            except ValueError:
                await interaction.response.send_message("Invalid hex color code. Use format like #FF0000.", ephemeral=True)
                return

        embed = discord.Embed(color=embed_color)
        if title:
            embed.title = title
        if description:
            embed.description = description.replace("\\n", "\n")
        if footer:
            embed.set_footer(text=footer.replace("\\n", "\n"))
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if image:
            embed.set_image(url=image)

        await interaction.response.send_message("Embed posted!", ephemeral=True)
        await interaction.channel.send(embed=embed)

    @app_commands.command(name="admin_embed_edit", description="Edit an existing embed message")
    @app_commands.describe(
        message_id="ID of the message to edit",
        title="New title",
        description="New description. \ n (without space) for a new line",
        footer="New footer",
        thumbnail="New thumbnail URL",
        image="New image URL",
        color="New hex color code (e.g. #00FF00)"
    )
    async def embed_edit(self, interaction: discord.Interaction,
                         message_id: str,
                         title: str = None,
                         description: str = None,
                         footer: str = None,
                         thumbnail: str = None,
                         image: str = None,
                         color: str = None):

        channel = interaction.channel

        member = interaction.guild.get_member(interaction.user.id)
        if not discord.utils.get(member.roles, id=1260298617818841318):
                await interaction.response.send_message("You are not an Admin!", ephemeral=True)
                return

        try:
            message = await channel.fetch_message(int(message_id))
            if not message.embeds:
                await interaction.response.send_message("That message doesn't contain an embed.", ephemeral=True)
                return

            embed = message.embeds[0].to_dict()
            new_embed = discord.Embed()

            if color:
                try:
                    embed_color = discord.Color(int(color.strip("#"), 16))
                except ValueError:
                    await interaction.response.send_message("Invalid hex color code. Use format like #00FF00.", ephemeral=True)
                    return
            elif 'color' in embed:
                embed_color = discord.Color(embed['color'])

            new_embed = discord.Embed(color=embed_color)

            if title:
                new_embed.title = title
            elif 'title' in embed:
                new_embed.title = embed['title']

            if description:
                new_embed.description = description.replace("\\n", "\n")
            elif 'description' in embed:
                new_embed.description = embed['description']

            if footer:
                new_embed.set_footer(text=footer.replace("\\n", "\n"))
            elif 'footer' in embed:
                new_embed.set_footer(text=embed['footer']['text'])

            if thumbnail:
                new_embed.set_thumbnail(url=thumbnail)
            elif 'thumbnail' in embed:
                new_embed.set_thumbnail(url=embed['thumbnail']['url'])

            if image:
                new_embed.set_image(url=image)
            elif 'image' in embed:
                new_embed.set_image(url=embed['image']['url'])

            await message.edit(embed=new_embed)
            await interaction.response.send_message("Embed edited successfully.", ephemeral=True)

        except discord.NotFound:
            await interaction.response.send_message("Message not found.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to edit that message.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmbedCreator(bot))