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
        self.process = await asyncio.create_subprocess_exec(
            "node", "./story_runner.js",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # no text=True here
        )

    async def get_next(self):
        lines = []

        while True:
            try:
                line_bytes = await asyncio.wait_for(self.process.stdout.readline(), timeout=5)
            except asyncio.TimeoutError:
                break

            if not line_bytes:
                break

            line = line_bytes.decode('utf-8').strip()  # decode bytes to str
            lines.append(line)

            if line.startswith("[") and "]" in line:
                await asyncio.sleep(0.05)

            if "===END===" in line:
                break

        return lines

    async def send_choice(self, index: int):
        choice_str = f"{index}\n"
        self.process.stdin.write(choice_str.encode('utf-8'))  # encode string to bytes
        await self.process.stdin.drain()

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
