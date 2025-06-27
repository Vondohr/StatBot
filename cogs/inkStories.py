import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import asyncio
import traceback
import os

STORY_FILE = "test.json"  # Change this to match the filename you're using

class InkSession:
    def __init__(self):
        self.process = None

    async def start_process(self):
        self.process = await asyncio.create_subprocess_exec(
            "node", "./story_runner.js",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def get_next(self):
        lines = []
        while True:
            try:
                line_bytes = await asyncio.wait_for(self.process.stdout.readline(), timeout=2)
            except asyncio.TimeoutError:
                break

            if not line_bytes:
                break

            line = line_bytes.decode("utf-8").strip()
            if line:
                lines.append(line)

            if "===END===" in line:
                break

        return lines

    async def send_choice(self, index: int):
        choice_str = f"{index}\n"
        self.process.stdin.write(choice_str.encode('utf-8'))
        await self.process.stdin.drain()

    async def terminate(self):
        if self.process:
            self.process.terminate()
            try:
                await self.process.wait()
            except Exception:
                pass

class ChoiceButton(Button):
    def __init__(self, label, index, session, parent_view, story_title):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.index = index
        self.session = session
        self.parent_view = parent_view
        self.story_title = story_title

    async def callback(self, interaction: discord.Interaction):
        try:
            await self.session.send_choice(self.index)
            await asyncio.sleep(0.1)
            lines = await self.session.get_next()

            if any("===END===" in line for line in lines):
                await interaction.response.edit_message(embed=discord.Embed(
                    title=self.story_title,
                    description="**The End.**",
                    color=discord.Color.blue()
                ), view=None)
                await self.session.terminate()
                return

            new_text = "\n".join(line for line in lines if not line.startswith("["))
            self.parent_view.update_buttons(lines)

            embed = discord.Embed(
                title=self.story_title,
                description=new_text or "*...*",
                color=discord.Color.blue()
            )

            await interaction.response.edit_message(embed=embed, view=self.parent_view)

        except Exception:
            tb = traceback.format_exc()
            await interaction.response.send_message(f"❌ Error:\n```\n{tb}\n```", ephemeral=True)
            await self.session.terminate()

class InkView(View):
    def __init__(self, session, lines, story_title):
        super().__init__(timeout=300)
        self.session = session
        self.story_title = story_title
        self.update_buttons(lines)

    def update_buttons(self, lines):
        self.clear_items()
        for line in lines:
            if line.startswith("["):
                idx = int(line[1])
                label = line.split("] ", 1)[1]
                self.add_item(ChoiceButton(label, idx, self.session, self, self.story_title))

    async def on_timeout(self):
        await self.session.terminate()
        for child in self.children:
            child.disabled = True

class InkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="playstory", description="Play the story.")
    async def playstory(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        session = InkSession()
        story_title = os.path.splitext(os.path.basename(STORY_FILE))[0]  # e.g. "test.json" → "test"

        try:
            await session.start_process()
            lines = await session.get_next()

            if not lines:
                await session.terminate()
                return await interaction.followup.send("❌ The story engine did not respond.")

            text = "\n".join(line for line in lines if not line.startswith("["))
            view = InkView(session, lines, story_title)

            embed = discord.Embed(
                title=story_title,
                description=text or "*...*",
                color=discord.Color.blue()
            )

            await interaction.followup.send(embed=embed, view=view)

        except Exception:
            tb = traceback.format_exc()
            await interaction.followup.send(f"❌ Error during story start:\n```\n{tb}\n```", ephemeral=False)
            await session.terminate()

async def setup(bot):
    await bot.add_cog(InkCog(bot))