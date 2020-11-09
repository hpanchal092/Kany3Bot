import discord
from discord.ext import commands
import asyncio

no_ban_users = ["410934879958859777", "381682180922802176", "321451146562633730"]


class baseCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"{round(self.client.latency * 1000)}ms")

    @commands.command()
    async def echo(self, ctx, *, arg):
        await ctx.send(arg)

    @commands.command()
    async def ban(self, ctx):
        if str(ctx.author.id) not in no_ban_users:
            await ctx.author.ban(reason="you used the ban command dumbass")
        else:
            await ctx.send("Sorry, you are prohibited from using this command")


def setup(client):
    client.add_cog(baseCommands(client))
