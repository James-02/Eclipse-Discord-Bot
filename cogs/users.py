""" User Commands file to seperate all the commands that do not require any permissions to call """
import json
import os
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

CONFIG_FILE = "data/config.json"


class Users(commands.Cog):
    """ Main Users class to define all the commands and class attributes """

    def __init__(self, bot):
        """ Main initialization method to define the class attributes """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff}
        self.data = get_config()
        print(f"{self.__class__.__name__} cog loaded.")

    @commands.command(help="", description="Returns the latency of the bot.")
    @commands.guild_only()
    async def ping(self, ctx):
        """ Returns the latency of the bot """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        ping = round(self.bot.latency * 1000)
        embed = discord.Embed(title="**__Ping__**", description=(f'The bot has {ping}ms ping'),
                              color=self.colors.get("green"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="<@user>", description="Retrives discord information on the user.")
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member = None):
        """ Displays User Info e.g: .userinfo @Pat """
        member = ctx.message.author if member is None else member
        timestamp = ctx.message.created_at.strftime(self.time_format)

        embed = discord.Embed(title="**__Discord User Info__**", description=f"User Info for - {member.mention}",
                              color=self.colors.get("pink"))
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Server Name", value=member.display_name, inline=False)
        embed.add_field(name="Status", value=member.status, inline=False)
        embed.add_field(name="Created On", value=member.created_at.strftime("%#d %B %Y"), inline=False)
        embed.add_field(name="Joined On", value=member.joined_at.strftime("%#d %B %Y"), inline=False)
        embed.add_field(name=f"Roles: {len(ctx.guild.roles)}",
                        value=', '.join([role.name for role in ctx.guild.roles]).replace('@everyone', 'everyone'),
                        inline=False)
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="", description="Retrieves information about the discord server.")
    @commands.guild_only()
    async def info(self, ctx):
        """ Displays bot and guild info e.g .botinfo """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        config = get_config()
        members = set(ctx.guild.members)
        desc = ""
        desc += f"**Bot Prefix :** {config['prefix']}\n"
        desc += f"**Member Count :** {str(len(members))}\n"
        desc += f"**Server Owner :** {ctx.guild.owner.mention}\n"
        desc += f"**Roles :** {len(ctx.guild.roles)}\n"
        desc += f"**Region :** {ctx.guild.region}\n"
        desc += f"**Creation Date :** {ctx.guild.created_at.strftime('%#d/%B/%Y')}\n"
        desc += f"**Nitro Boosts :** {ctx.guild.premium_subscription_count}\n"
        desc += f"**Nitro Boosters :** {str(len(ctx.guild.premium_subscribers))}\n"
        desc += f"**Premium Tier :** {ctx.guild.premium_tier}\n"

        embed = discord.Embed(title=f"__{ctx.message.guild.name}__", description=f"{desc}\n`Bot made by Jam#0191`",
                              color=self.colors.get("pink"))
        embed.set_thumbnail(url=f"{ctx.message.guild.icon_url}")
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="<@user> (Leave empty to view the leaderboard.)",
                      description="Retrieves the active invites in the server for a user or all users if none specified.")
    @commands.guild_only()
    async def invites(self, ctx, member: discord.Member = None):
        """ Sends the leaderboard of current invites, send a user as a argument to fetch their personal invites """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        invites = {}
        invite = await ctx.message.guild.invites()
        for i in invite:
            if i.inviter.name in invites.keys():
                invites[i.inviter.name] += 1
            else:
                invites.update({(i.inviter.name + "#" + i.inviter.discriminator): i.uses})

        if member is None:
            list_1 = []
            values = sorted(invites.items(), reverse=True, key=lambda kv: kv[1])
            count = 0
            for key, value in values:
                count += 1
                if value == 1:
                    list_1.append(f"**{count}. {key}** has {value} invite.\n")

                else:
                    list_1.append(f"**{count}. {key}** has {value} invites.\n")

            embed = discord.Embed(title="**__Invite Leaderboard__**", description="".join(list_1),
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            invs = invites.get(f"{member}")
            if invs is None:
                desc = f"**{member.mention}** has 0 invites."

            elif invs == 1:
                desc = f"**{member.mention}** has {invs} invite."

            else:
                desc = f"**{member.mention}** has {invs} invites."

            embed = discord.Embed(title="**__Invites__**", description=desc, color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<suggestion>",
                      description="Sends a suggestion into the suggestions channel and adds reactions.",
                      aliases=['suggestion'])
    @commands.guild_only()
    async def suggest(self, ctx, *, suggestion=None):
        """ Sends the message given to the suggestions channel and adds reactions """
        config = get_config()
        timestamp = ctx.message.created_at.strftime(self.time_format)
        channel_id = config["suggestions_channel_id"]
        if channel_id is None:
            embed = discord.Embed(title="__Error__",
                                  description="Please enter your 'suggestions' channel ID in the config file.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        if suggestion is None:
            embed = discord.Embed(title="__Error__", description="Please provide a suggestion.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(title="**__Suggestion Added__**",
                                  description=f"{ctx.author.mention} added a suggestion in {channel.mention}",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

            embed = discord.Embed(
                description=f"**Suggested By:**\n{ctx.author.mention}\n\n**Suggestion:**\n{suggestion}",
                color=self.colors.get("green"))
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            message = await channel.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")

    @commands.command(help="<@user>", description="Retrieves the user's discord avatar.", aliases=['avatar'])
    @commands.guild_only()
    async def av(self, ctx, member: discord.Member = None):
        """ Retrieves the user's discord avatar """
        image = ctx.message.author.avatar_url if member is None else member.avatar_url
        embed = discord.Embed(color=self.colors.get("pink"))
        embed.set_image(url=image)
        await ctx.send(embed=embed)

    @commands.command(help="", description="Retrieves all the roles in the discord server.")
    @commands.guild_only()
    async def roles(self, ctx):
        """ Retrieves all the roles in the guild """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        roles = sorted(ctx.message.guild.roles, key=lambda role: role.name)
        role_string = ""
        for role in roles:
            role_string += f"{role.mention}\n" if role.name != "@everyone" else f'{role.name}\n'

        embed = discord.Embed(title="__Roles in this server__", description=role_string, color=self.colors.get("green"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="<@user>",
                      description="Retrieves previous 90 days of punishment history for the user from the audit logs.")
    @commands.guild_only()
    async def history(self, ctx, member: discord.Member = None):
        """ Returns the kick, ban and unban logs for a user within the last 90 days """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if member is None:
            embed = discord.Embed(title="__Error__", description="No user given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            time_format = "%d/%B/%Y"
            ban_history, kick_history, unban_history = "", "", ""

            async for entry in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.ban):
                if entry.target == member:
                    ban_history += f"*{entry.created_at.strftime(time_format)}* - {entry.user.mention} *banned* {entry.target.mention} for reason: *{entry.reason}*\n"

            async for entry in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.kick):
                if entry.target == member:
                    kick_history += f"*{entry.created_at.strftime(time_format)}* - {entry.user.mention} *kicked* {entry.target.mention} for reason: *{entry.reason}*\n"

            async for entry in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.unban):
                if entry.target == member:
                    unban_history += f"{entry.created_at.strftime(time_format)} - {entry.user.mention} *unbanned* {entry.target.mention} for reason: *{entry.reason}*\n"

            ban_history = "None" if ban_history == "" else ban_history
            kick_history = "None" if kick_history == "" else kick_history
            unban_history = "None" if unban_history == "" else unban_history

            embed = discord.Embed(title=f"**Punishment History in the last 90 days for:** *{member}*",
                                  description=f"**__Ban History:__**\n{ban_history}\n\n**__Unban History:__**\n{unban_history}\n\n**__Kick History:__**\n{kick_history}",
                                  color=self.colors.get("pink"))

            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="", description="Shows all the custom commands", aliases=["customcommands", "commands"])
    @commands.guild_only()
    async def customcmds(self, ctx):
        """ Returns the list of custom commands for this bot """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        bot_commands = []
        data = get_cmds()
        cmds = data["commands"]
        keys = cmds.keys()
        for key in keys:
            bot_commands.append(key)

        embed = discord.Embed(title="__Custom Commands__", description=f"{', '.join(bot_commands)}",
                              color=self.colors.get("green"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="<username>", description="Lookup a minecraft user's name history and skin.")
    async def namemc(self, ctx, name=None):
        final_string = ""
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if name is None:
            embed = discord.Embed(title="__Error__", description="No username given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{name}") as c:
                        response = await c.json()
                        if c.status == 200:
                            uuid = response['id']

                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"https://api.mojang.com/user/profiles/{uuid}/names") as i:
                                    response = await i.json()
                                    for names in range(len(response)):
                                        names = response[names]
                                        changed_name = names["name"]
                                        if 'changedToAt' in names:
                                            date = names["changedToAt"]
                                            date = datetime.utcfromtimestamp(date / 1000).strftime('%d/%m/%Y')
                                            final_string += f"**{changed_name}** - {date}\n"

                                        else:
                                            final_string += f"**{changed_name}**\n"

                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"https://crafatar.com/renders/body/{uuid}") as c:
                                    response = await c.read()
                                    with open("skin.png", "wb") as f:
                                        f.write(response)

                                    if c.status == 200:
                                        directory = os.getcwd()
                                        embed = discord.Embed(title=f"**__Name History__**",
                                                              description=f"{final_string}",
                                                              color=self.colors.get("pink"))
                                        file = discord.File(f"{directory}\skin.png", filename="skin.png")
                                        embed.set_thumbnail(url="attachment://skin.png")
                                        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}",
                                                         icon_url=self.bot.user.avatar_url)
                                        await ctx.send(file=file, embed=embed)

                                    else:
                                        embed = discord.Embed(title="__Error__",
                                                              description="An error occured while fetching user data.",
                                                              color=self.colors.get("red"))
                                        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}",
                                                         icon_url=self.bot.user.avatar_url)
                                        await ctx.send(embed=embed)

                        else:
                            embed = discord.Embed(title="__Error__", description="User not found.",
                                                  color=self.colors.get("red"))
                            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}",
                                             icon_url=self.bot.user.avatar_url)
                            await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="__Error__", description="An error occured.", color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(help="<username>", description="Lookup a minecraft user's skin.")
    async def skin(self, ctx, name=None):
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if name is None:
            embed = discord.Embed(title="__Error__", description="No username given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{name}") as c:
                        response = await c.json()
                        if c.status == 200:
                            uuid = response['id']

                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"https://crafatar.com/renders/body/{uuid}") as c:
                                    response = await c.read()
                                    with open("skin.png", "wb") as f:
                                        f.write(response)
                                    if c.status == 200:
                                        directory = os.getcwd()
                                        embed = discord.Embed(title=f"Player: {name}", color=self.colors.get("pink"))
                                        file = discord.File(f"{directory}\skin.png", filename="skin.png")
                                        embed.set_image(url="attachment://skin.png")
                                        await ctx.send(file=file, embed=embed)

                                    else:
                                        embed = discord.Embed(title="__Error__", description="User not found.",
                                                              color=self.colors.get("red"))
                                        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}",
                                                         icon_url=self.bot.user.avatar_url)
                                        await ctx.send(embed=embed)

                        else:
                            embed = discord.Embed(title="__Error__", description="User not found.",
                                                  color=self.colors.get("red"))
                            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}",
                                             icon_url=self.bot.user.avatar_url)
                            await ctx.send(embed=embed)

            except:
                embed = discord.Embed(title="__Error__", description="An error occured.", color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)


def get_config():
    """ Function to get the config data """
    try:
        with open(CONFIG_FILE) as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def get_cmds():
    """ Function to get the custom commands data """
    try:
        with open("data/custom_cmds.json", "r") as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Users(bot))
