import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import asyncio
import traceback

class InkSession:
    def __init__(self):
        self.process = None

    async def start_process(self):
        # Start the node story_runner.js subprocess asynchronously
        self.process = await asyncio.create_subprocess_exec(
            "node", "./story_runner.js",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            text=True
        )

    async def get_next(self):
        """
        Read all output lines from the subprocess until choices and/or END marker appear.
        Returns a list of output lines (strings).
        """
        lines = []

        while True:
            # Read line asynchronously with a timeout
            try:
                line = await asyncio.wait_for(self.process.stdout.readline(), timeout=5)
            except asyncio.TimeoutError:
                # No more output for 5 seconds — assume story ended or stuck
                break

            if not line:
                # EOF reached
                break

            line = line.strip()
            lines.append(line)

            # Wait briefly if line looks like a choice to gather all choices
            if line.startswith("[") and "]" in line:
                await asyncio.sleep(0.05)

            if "===END===" in line:
                break

        return lines

    async def send_choice(self, index: int):
        # Send the choice index to the subprocess stdin asynchronously
        self.process.stdin.write(f"{index}\n")
        await self.process.stdin.drain()

    async def is_finished(self):
        # Check if the last read lines contained the end marker
        # This should be called after get_next()
        return any("===END===" in line for line in await self.get_next())

    async def terminate(self):
        if self.process:
            self.process.terminate()
            try:
                await self.process.wait()
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
            await self.session.send_choice(self.index)
            # Small pause to let node process choice
            await asyncio.sleep(0.1)
            lines = await self.session.get_next()

            if any("===END===" in line for line in lines):
                await interaction.response.edit_message(content="**The End.**", view=None)
                await self.session.terminate()
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
            await interaction.response.send_message(f"❌ Error:\n```\n{tb}\n```", ephemeral=False)
            await self.session.terminate()

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
        session = InkSession()
        try:
            await session.start_process()
            lines = await session.get_next()
            if not lines:
                await interaction.followup.send("❌ The story engine did not respond.")
                await session.terminate()
                return

            text = "\n".join(line for line in lines if not line.startswith("["))
            view = InkView(session, lines)
            await view.refresh_buttons(lines)
            await interaction.followup.send(content=text, view=view)

        except Exception as e:
            tb = traceback.format_exc()
            await interaction.followup.send(f"❌ Error during story start:\n```\n{tb}\n```", ephemeral=False)
            await session.terminate()

async def setup(bot):
    await bot.add_cog(InkCog(bot))
