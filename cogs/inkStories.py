import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import asyncio
import traceback

class InkSession:
    def __init__(self):
        self.process = None
        self.story_file = "unknown"

    async def start_process(self):
        self.process = await asyncio.create_subprocess_exec(
            "node", "./story_runner.js",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Give it a moment to start up
        await asyncio.sleep(0.1)

        # Get the story filename from the process arguments
        try:
            # Check what args node was called with
            self.story_file = await self._extract_filename()
        except Exception:
            self.story_file = "Unknown"

    async def _extract_filename(self):
        # This assumes story_runner.js has the story filename hardcoded
        # So we fake it here with a temp override (alternatively, set it manually)
        with open("story_runner.js", "r", encoding="utf-8") as f:
            for line in f:
                if "fs.readFileSync" in line:
                    parts = line.strip().split("fs.readFileSync(")
                    if len(parts) > 1:
                        filename_part = parts[1].split(",")[0].replace("'", "").replace('"', "").strip()
                        return filename_part.split("/")[-1].replace(".json", "")
        return "Unknown"

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
        if interaction.user.id != self.parent_view.author_id:
            await interaction.response.send_message("❌ This is not your story.", ephemeral=True)
            return

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
    def __init__(self, session, lines, story_title, author_id):
        super().__init__(timeout=300)
        self.session = session
        self.story_title = story_title
        self.author_id = author_id
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

    @app_commands.command(name="play_story", description="Play the story.")
    async def playstory(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        session = InkSession()

        try:
            await session.start_process()
            lines = await session.get_next()

            if not lines:
                await session.terminate()
                return await interaction.followup.send("❌ The story engine did not respond.")

            text = "\n".join(line for line in lines if not line.startswith("["))
            story_title = session.story_file

            view = InkView(session, lines, story_title, interaction.user.id)

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
