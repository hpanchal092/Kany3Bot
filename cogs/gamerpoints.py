import discord
from discord.ext import commands
import random as rng
import math
import asyncio
import pymongo
from pymongo import MongoClient
import os
import settings

BASE_PERCENTAGE = 0.9
PERCENTAGE_INCREMENT = 0.05
MAX_BAN_TIME = 60
BAN_TIME_SCALE = 1.5

cluster = MongoClient(settings.MONGOCLIENT)
db = cluster["discord"]
collection = db["kany3"]


class gamerPoints(commands.Cog):
    def __init__(self, client):
        self.client = client

        results = collection.find({})
        self.users = {}
        for result in results:
            self.users[result["_id"]] = result["info"]

    @commands.command()
    async def stats(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        else:
            member = member

        member_id = member.id
        if member_id not in self.users:
            await ctx.send("User has no stats")
        else:
            embed = discord.Embed(color=discord.Color.red(), timestamp=ctx.message.created_at)
            embed.set_author(name=member)
            embed.add_field(name="Gamer Points", value=self.users[member_id]["gamer_points"])
            embed.add_field(name="Total Bans", value=self.users[member_id]["bans"])
            embed.add_field(name="Successful Spins", value=self.users[member_id]["spins"] - 1)

            await ctx.send(embed=embed)

    @commands.command()
    async def spin(self, ctx, ban_time=None):
        # Adds user to users.json if he is not already in it
        author_id = ctx.author.id
        if author_id not in self.users:
            self.users[author_id] = {}
            self.users[author_id]["name"] = ctx.author.name
            self.users[author_id]["gamer_points"] = 0
            self.users[author_id]["bans"] = 0
            self.users[author_id]["spins"] = 1

        # Makes ban sure ban_time is passed integer and is within range 1 - 60
        if ban_time is None:
            await ctx.send("Please specify a ban time")
            return
        ban_time = round(float(ban_time))
        if ban_time > MAX_BAN_TIME:
            await ctx.send("The maximum ban time you can set is 60 minutes")
            return
        if ban_time < 1:
            await ctx.send("The minimum ban time you can set is 1 minute")
            return

        # percentage user needs to pass to not get banned
        spin_percentage = BASE_PERCENTAGE - (self.users[author_id]["spins"] * PERCENTAGE_INCREMENT)
        # gamer points the user will gain if he passes the spin
        added_gamer_points = calcPoints(self.users[author_id]["spins"], ban_time)

        # embed user will see before he reacts whether to spin or not
        embed = discord.Embed(color=discord.Color.red(), timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author)
        embed.add_field(name="Potential Gamer Point Gain", value=str(added_gamer_points))
        embed.add_field(name="Total Gamer Points After", value=self.users[author_id]["gamer_points"] + added_gamer_points)
        embed.add_field(name="Chance of Getting Banned", value=f"{round(1 - spin_percentage, 2) * 100}%")
        embed.add_field(name="Ban Time", value=str(ban_time))

        # sends embed and reacts ✅ or ❎
        msg = await ctx.send("Spin?", embed=embed)
        for emoji in ('✅', '❎'):
            await msg.add_reaction(emoji)

        # checks if user reacted with either ✅ or ❎ and spins or cancels accordingly
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['✅', '❎']
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Timed out")
        else:
            if user == ctx.author:
                if str(reaction.emoji) == "❎":
                    await ctx.send("Canceled spin")
                    return
                percentage = round(rng.random(), 2)
                if percentage <= spin_percentage:
                    self.users[author_id]["gamer_points"] += added_gamer_points
                    await ctx.send(f"yo dawg, you won {added_gamer_points} gamer point(s). you got {self.users[author_id]['gamer_points']} gamer point(s) now")
                    self.users[author_id]["spins"] += 1

                    post = {"_id": ctx.author.id}
                    post_info = {"info": self.users[author_id]}
                    collection.update(post, post_info, upsert=True)
                else:
                    self.users[author_id]["gamer_points"] = 0
                    self.users[author_id]["spins"] = 1
                    self.users[author_id]["bans"] += 1

                    post = {"_id": ctx.author.id}
                    post_info = {"info": self.users[author_id]}
                    collection.update(post, post_info, upsert=True)

                    await ctx.send(f"{ctx.author} got banned for {ban_time} minute(s)")
                    await ctx.author.ban(reason="you got rekt homie")
                    await asyncio.sleep(ban_time * 60)
                    await ctx.author.unban()


def calcPoints(x, t):
    return math.ceil(math.log10(x + 1) * BAN_TIME_SCALE * t)


def setup(client):
    client.add_cog(gamerPoints(client))
