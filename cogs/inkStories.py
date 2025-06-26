import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import subprocess
import asyncio

class InkSession:
    def __init__(self):
        self.proc = subprocess.Popen(
            ["node", "story_runner.js"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.output_lines = []

    async def get_next(self):
        """Read all lines and all choices without prematurely stopping."""
        self.output_lines = []
        while True:
            line = self.proc.stdout.readline()
            if not line:
                break

            line = line.strip()
            self.output_lines.append(line)

            # Wait a moment after a choice line to let all of them print
            if line.startswith("[") and "]" in line:
                await asyncio.sleep(0.05)

            if "===END===" in line:
                break

        return self.output_lines

    def send_choice(self, index: int):
        self.proc.stdin.write(f"{index}\n")
        self.proc.stdin.flush()

    def is_finished(self):
        return any("===END===" in line for line in self.output_lines)

    def terminate(self):
        self.proc.terminate()

class ChoiceButton(Button):
    def __init__(self, label, index, session, parent_view):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.index = index
        self.session = session
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        self.session.send_choice(self.index)
        await asyncio.sleep(0.1)
        lines = await self.session.get_next()

        if self.session.is_finished():
            await interaction.response.edit_message(content="The End.", view=None)
            self.session.terminate()
            return

        new_text = "\n".join(line for line in lines if not line.startswith("["))
        self.parent_view.clear_items()
        for line in lines:
            if line.startswith("["):
                idx = int(line[1])
                label = line.split("] ", 1)[1]
                self.parent_view.add_item(ChoiceButton(label, idx, self.session, self.parent_view))

        await interaction.response.edit_message(content=new_text, view=self.parent_view)

class InkView(View):
    def __init__(self, session, initial_lines):
        super().__init__(timeout=None)
        self.session = session
        self.initial_lines = initial_lines

    async def refresh_buttons(self, lines):
        self.clear_items()
        for line in lines:
            if line.startswith("["):
                idx = int(line[1])
                label = line.split("] ", 1)[1]
                self.add_item(ChoiceButton(label, idx, self.session, self))

class InkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="playstory", description="Play the story.")
    async def playstory(self, interaction: discord.Interaction):
        session = InkSession()
        lines = await session.get_next()
        text = "\n".join(line for line in lines if not line.startswith("["))

        view = InkView(session, lines)
        await view.refresh_buttons(lines)
        await interaction.response.send_message(content=text, view=view)

async def setup(bot):
    await bot.add_cog(InkCog(bot))
