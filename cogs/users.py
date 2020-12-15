""" User Commands file to separate all the commands that do not require any permissions to call """
import os
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands
import methods


class Users(commands.Cog):
    """ Main Users class to define all the commands and class attributes """

    def __init__(self, bot):
        """ Main initialization method to define the class attributes """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff}
        print(f"{self.__class__.__name__} cog loaded.")

    @commands.command(help="", description="Returns the latency of the bot.")
    @commands.guild_only()
    async def ping(self, ctx):
        """ Returns the latency of the bot """
        ping = round(self.bot.latency * 1000)
        title = "**__Ping__**"
        description = f"The bot has {ping}ms ping"
        await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<@user>", description="Retrives discord information on the user.")
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member = None):
        """ Displays User Info e.g: .userinfo @Pat """
        member = ctx.message.author if member is None else member
        title = "**__Discord User Info__**"
        description = f"User Info for - {member.mention}"
        roles = ', '.join([role.name for role in ctx.guild.roles]).replace('@everyone', 'everyone')

        embed = methods.return_embed(self, ctx, title, description, color="pink", thumbnail=member.avatar_url)
        embed.add_field(name="Server Name", value=member.display_name, inline=False)
        embed.add_field(name="Status", value=member.status, inline=False)
        embed.add_field(name="Created On", value=member.created_at.strftime("%#d %B %Y"), inline=False)
        embed.add_field(name="Joined On", value=member.joined_at.strftime("%#d %B %Y"), inline=False)
        embed.add_field(name=f"Roles: {len(ctx.guild.roles)}", value=roles, inline=False)
        await ctx.send(embed=embed)

    @commands.command(help="", description="Retrieves information about the discord server.")
    @commands.guild_only()
    async def info(self, ctx):
        """ Displays bot and guild info e.g .info """
        config = methods.get_config()
        members = await ctx.guild.chunk()
        embed = methods.return_embed(self, ctx, title=ctx.guild.name, color="pink", thumbnail=ctx.guild.icon_url)
        embed.add_field(name="**Bot Prefix :**", value=config['prefix'], inline=False)
        embed.add_field(name="**Member Count :**", value=str(len(members)), inline=False)
        embed.add_field(name="**Server Owner :**", value=ctx.guild.owner.mention, inline=False)
        embed.add_field(name="**Roles :**", value=str(len(ctx.guild.roles)), inline=False)
        embed.add_field(name="**Region :**", value=ctx.guild.region, inline=False)
        embed.add_field(name="**Creation Date :**", value=ctx.guild.created_at.strftime('%#d/%B/%Y'), inline=False)
        embed.add_field(name="**Nitro Boosts :**", value=ctx.guild.premium_subscription_count, inline=False)
        embed.add_field(name="**Nitro Boosters :**", value=str(len(ctx.guild.premium_subscribers)), inline=False)
        embed.add_field(name="**Premium Tier :**", value=ctx.guild.premium_tier, inline=False)
        embed.add_field(name="**Bot Developer :**", value="Jam#0191", inline=False)
        await ctx.send(embed=embed)

    @commands.command(help="<@user> (Leave empty to view the leaderboard.)",
                      description="Retrieves the active invites in the server for a user or all users if none given.")
    @commands.guild_only()
    async def invites(self, ctx, member: discord.Member = None):
        """ Sends the leaderboard of current invites, send a user as a argument to fetch their personal invites """
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

            title = "**__Invite Leaderboard__**"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description="".join(list_1), color="green"))

        else:
            invs = invites.get(f"{member}")
            if invs is None:
                desc = f"**{member.mention}** has 0 invites."
            elif invs == 1:
                desc = f"**{member.mention}** has {invs} invite."
            else:
                desc = f"**{member.mention}** has {invs} invites."
            await ctx.send(embed=methods.return_embed(self, ctx, title="**__Invites__**", description=desc,
                                                      color="green"))

    @commands.command(help="<suggestion>",
                      description="Sends a suggestion into the suggestions channel and adds reactions.",
                      aliases=['suggestion'])
    @commands.guild_only()
    async def suggest(self, ctx, *, suggestion=None):
        """ Sends the message given to the suggestions channel and adds reactions """
        config = methods.get_config()
        channel_id = config["suggestions_channel_id"]
        if channel_id is None:
            description = "Please enter your 'suggestions' channel ID in the config file."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif suggestion is None:
            description = "Please provide a suggestion."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        else:
            channel = self.bot.get_channel(channel_id)
            title = "__Suggestion Added__"
            description = f"{ctx.author.mention} added a suggestion in {channel.mention}"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            description = f"**Suggested By:**\n{ctx.author.mention}\n\n**Suggestion:**\n{suggestion}"
            message = await channel.send(embed=methods.return_embed(self, ctx, description=description, color="green",
                                                                    thumbnail=ctx.author.avatar_url))
            await message.add_reaction("✅")
            await message.add_reaction("❌")

    @commands.command(help="<@user>", description="Retrieves the user's discord avatar.", aliases=['av'])
    @commands.guild_only()
    async def avatar(self, ctx, member: discord.Member = None):
        """ Retrieves the user's discord avatar """
        image = ctx.message.author.avatar_url if member is None else member.avatar_url
        await ctx.send(embed=methods.return_embed(self, ctx, image=image, color="pink"))

    @commands.command(help="", description="Retrieves all the roles in the discord server.")
    @commands.guild_only()
    async def roles(self, ctx):
        """ Retrieves all the roles in the guild """
        roles = sorted(ctx.message.guild.roles, key=lambda role_1: role_1.name)
        role_string = ""
        for role in roles:
            role_string += f"{role.mention}\n" if role.name != "@everyone" else f'{role.name}\n'

        title = "__Roles in this server__"
        await ctx.send(embed=methods.return_embed(self, ctx, title, description=role_string, color="green"))

    @commands.command(help="<@user>",
                      description="Retrieves previous 90 days of punishment history for the user from the audit logs.")
    @commands.guild_only()
    async def history(self, ctx, member: discord.Member = None):
        """ Returns the kick, ban and unban logs for a user within the last 90 days """
        if member is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No user given"))
        else:
            time_format = "%d/%B/%Y"
            ban_history, kick_history, unban_history = "", "", ""

            async for entry in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.ban):
                if entry.target == member:
                    ban_history += f"*{entry.created_at.strftime(time_format)}* - {entry.user.mention} "
                    ban_history += f"*banned* {entry.target.mention} for reason: *{entry.reason}*\n"

            async for entry in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.kick):
                if entry.target == member:
                    kick_history += f"*{entry.created_at.strftime(time_format)}* - {entry.user.mention} "
                    kick_history += f"*kicked* {entry.target.mention} for reason: *{entry.reason}*\n"

            async for entry in ctx.guild.audit_logs(limit=None, action=discord.AuditLogAction.unban):
                if entry.target == member:
                    unban_history += f"{entry.created_at.strftime(time_format)} - {entry.user.mention} "
                    unban_history += f"*unbanned* {entry.target.mention} for reason: *{entry.reason}*\n"

            ban_history = "None" if ban_history == "" else ban_history
            kick_history = "None" if kick_history == "" else kick_history
            unban_history = "None" if unban_history == "" else unban_history

            description = f"**__Ban History:__**\n{ban_history}\n\n**__Unban History:__**\n{unban_history}\n\n"
            description += f"**__Kick History:__**\n{kick_history}"

            title = f"**Punishment History in the last 90 days for:** *{member}*"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="pink"))

    @commands.command(help="", description="Shows all the custom commands", aliases=["customcommands", "commands"])
    @commands.guild_only()
    async def customcmds(self, ctx):
        """ Returns the list of custom commands for this bot """
        bot_commands = []
        data = methods.get_cmds()
        cmds = data["commands"]
        keys = cmds.keys()
        for key in keys:
            bot_commands.append(key)

        title = "__Custom Commands__"
        description = f"{', '.join(bot_commands)}"
        await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<username>", description="Lookup a minecraft user's name history and skin.")
    async def namemc(self, ctx, name=None):
        final_string = ""
        if name is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No username given"))

        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{name}") as c:
                        response = await c.json()
                        if c.status == 200:
                            uuid = response['id']

                            async with aiohttp.ClientSession() as session_2:
                                async with session_2.get(f"https://api.mojang.com/user/profiles/{uuid}/names") as i:
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

                            async with aiohttp.ClientSession() as session_3:
                                async with session_3.get(f"https://crafatar.com/renders/body/{uuid}") as d:
                                    response = await d.read()
                                    with open("skin.png", "wb") as f:
                                        f.write(response)

                                    if d.status == 200:
                                        directory = os.getcwd()
                                        file = discord.File(fr"{directory}\skin.png", filename="skin.png")
                                        title = "**__Name History__**"
                                        description = f"{final_string}"
                                        color = "pink"
                                        thumbnail = "attachment://skin.png"
                                        await ctx.send(file=file, embed=methods.return_embed(self, ctx, title,
                                                                                             description,
                                                                                             color, thumbnail))
                                        os.remove('skin.png')

                                    else:
                                        description = "An error occurred while fetching user data"
                                        await ctx.send(embed=methods.return_error(self, ctx, error=description))
                        else:
                            await ctx.send(embed=methods.return_error(self, ctx, error="User not found"))

            except aiohttp.ContentTypeError:
                await ctx.send(embed=methods.return_error(self, ctx, error="Invalid username"))

    @commands.command(help="<username>", description="Lookup a minecraft user's skin.")
    async def skin(self, ctx, name=None):
        """ Command to retrieve the skin of a minecraft player by searching their username with an API."""
        if name is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No username given"))

        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{name}") as c:
                        response = await c.json()
                        if c.status == 200:
                            uuid = response['id']

                if uuid is not None:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://crafatar.com/renders/body/{uuid}") as i:
                            response = await i.read()
                            with open("skin.png", "wb") as f:
                                f.write(response)
                            if i.status == 200:
                                directory = os.getcwd()
                                file = discord.File(fr"{directory}\skin.png", filename="skin.png")
                                title = f"Player: {name}"
                                image = "attachment://skin.png"
                                await ctx.send(file=file, embed=methods.return_embed(self, ctx, title,
                                                                                     color="pink", image=image))
                                os.remove("skin.png")
                            else:
                                description = "An error occurred while fetching user data."
                                await ctx.send(embed=methods.return_error(self, ctx, error=description))
                else:
                    await ctx.send(embed=methods.return_error(self, ctx, error="User not found"))

            except aiohttp.ContentTypeError:
                await ctx.send(embed=methods.return_error(self, ctx, error="Invalid username"))


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Users(bot))
