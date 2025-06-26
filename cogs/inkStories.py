import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import subprocess
import asyncio
import traceback

class InkSession:
    def __init__(self):
        self.proc = subprocess.Popen(
            ["node", "./story_runner.js"],  # Ensure relative path is correct
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.output_lines = []

    async def get_next(self):
        """Read all story output and collect all choices."""
        self.output_lines = []

        try:
            while True:
                line = self.proc.stdout.readline()
                if not line:
                    break

                line = line.strip()
                self.output_lines.append(line)

                if line.startswith("[") and "]" in line:
                    await asyncio.sleep(0.05)

                if "===END===" in line:
                    break

            return self.output_lines
        except Exception as e:
            raise RuntimeError(f"Error reading from Ink story: {e}")

    def send_choice(self, index: int):
        try:
            self.proc.stdin.write(f"{index}\n")
            self.proc.stdin.flush()
        except Exception as e:
            raise RuntimeError(f"Error sending choice to Ink story: {e}")

    def is_finished(self):
        return any("===END===" in line for line in self.output_lines)

    def terminate(self):
        try:
            self.proc.terminate()
        except Exception:
            pass

class ChoiceButton(Button):
    def __init__(self, label, index, session, parent_view):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.index = index
        self.session = session
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        try:
            self.session.send_choice(self.index)
            await asyncio.sleep(0.1)
            lines = await asyncio.wait_for(self.session.get_next(), timeout=3)

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

        except Exception as e:
            tb = traceback.format_exc()
            await interaction.response.send_message(f"❌ Error: ```\n{tb}\n```", ephemeral=False)
            self.session.terminate()

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
        await interaction.response.defer(thinking=True)
        try:
            session = InkSession()
            lines = await asyncio.wait_for(session.get_next(), timeout=3)
            text = "\n".join(line for line in lines if not line.startswith("["))

            view = InkView(session, lines)
            await view.refresh_buttons(lines)
            await interaction.followup.send(content=text, view=view)

        except Exception as e:
            tb = traceback.format_exc()
            await interaction.followup.send(f"❌ Error during story start:\n```\n{tb}\n```", ephemeral=False)

async def setup(bot):
    await bot.add_cog(InkCog(bot))