import discord
from discord.ext import commands, tasks

import os
import asyncio

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.wait_until_ready()  # extra safe
    await asyncio.sleep(2)  # wait for guilds to load
    await bot.tree.sync()
    print("Bot ready! Stats incoming!")

with open("token.txt") as file:
    token = file.read()

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.load_extension("ink_adventure")
        await bot.start(token)

asyncio.run(main())