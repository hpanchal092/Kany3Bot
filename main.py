import discord
from discord.ext import commands
import os
import settings

client = commands.Bot(command_prefix="-k ")


@client.command()
async def reload(ctx, *, extension):
    client.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded {extension}")


@client.command()
async def load(ctx, *, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension}")


@client.command()
async def unload(ctx, *, extension):
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded {extension}")


@client.event
async def on_ready():
    print("bot is online")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(settings.TOKEN)
