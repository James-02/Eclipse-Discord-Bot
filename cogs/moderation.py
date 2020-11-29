""" Management module to define all moderation commands seperately for easier sorting """
import asyncio
import json
import random

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get

CONFIG_FILE = "data/config.json"


class Moderation(commands.Cog):
    """ Management class is used to sort all the moderation commands into one cog """

    def __init__(self, bot):
        """ Initialization method to define all the attributes required for the class """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.message_ids = []
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff, "blue": 0x0080c0}
        print(f"{self.__class__.__name__} cog loaded.")

    @commands.command(help="<message>", description="Embeds your messages and deletes the original.")
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def announce(self, ctx, *, message):
        """ Creates an embedded message where the user can type a message to send e.g .announce this is a test """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        await ctx.message.delete()
        embed = discord.Embed(title="**__Announcement__**", description=message, color=self.colors.get("blue"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="<role> (Leave empty to mute everyone)",
                      description="Mutes the channel for all members with the role specified.",
                      aliases=["lock", "channellock"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def channelmute(self, ctx, role: discord.Role = None):
        """ Mutes the channel for a specific role, leave the argument empty to mute everyone """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if role is None:
            role = get(ctx.guild.roles, name='@everyone')
            await ctx.message.channel.set_permissions(role, send_messages=False)
            embed = discord.Embed(title="**__Channel Muted__**",
                                  description="All members in this channel have been muted.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            await ctx.message.channel.set_permissions(role, send_messages=False)
            embed = discord.Embed(title="**__Channel Muted__**",
                                  description=f"All members in this channel with the role `{role}` have been muted.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<role> (Leave empty to mute everyone)",
                      description="Unmutes the channel for all members with the role specified.",
                      aliases=["unlock", "channelunlock"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def channelunmute(self, ctx, role: discord.Role = None):
        """ Unmutes the channel for a specific role, leave the argument empty to unmute everyone """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if role is None:
            role = get(ctx.guild.roles, name='@everyone')
            await ctx.message.channel.set_permissions(role, send_messages=True)
            embed = discord.Embed(title="**__Channel Unmuted__**",
                                  description="All members in this channel have been unmuted.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            await ctx.message.channel.set_permissions(role, send_messages=True)
            embed = discord.Embed(title="**__Channel Unmuted__**",
                                  description=f"**All members in this channel with the role `{role}` have been unmuted.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<seconds>",
                      description="Enables slowmode with a time between messages, enter '0' or 'off' to turn it off.")
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def slowmode(self, ctx, time=None):
        """ Enables slowmode in the channel, set the time between messages using (prefix)slowmode (time) """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if time == "off":
            channel = ctx.message.channel
            await channel.edit(slowmode_delay=0)
            embed = discord.Embed(title="**__Slowmode__**", description="Slowmode has been turned off in this channel.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif time is not None:
            desc = "This channel's slowmode has been set to 1 second." if time == '1' else f"This channel's slowmode has been set to {time} seconds."
            channel = ctx.message.channel
            await channel.edit(slowmode_delay=time)
            embed = discord.Embed(title="**__Slowmode__**", description=desc, color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="**__Error__**", description="No time was given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<@user> <reason> (Reason is not required.)",
                      description="Kicks a user from the discord server.")
    @commands.guild_only()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """ Kicks a user .kick @Pat """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        await member.kick(reason=reason)
        embed = discord.Embed(title="__User Kicked__",
                              description=f"{member.mention} was kicked by {ctx.message.author.mention}",
                              color=self.colors.get("green"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="<@user> <reason> (Reason is not required.)",
                      description="Bans a user from the discord server.")
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """ Bans a user .ban @Pat """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        banned_users = await ctx.guild.bans()
        if member not in banned_users:
            await member.ban(reason=reason)
            embed = discord.Embed(title="__User Banned__",
                                  description=f"{member.mention} was banned by {ctx.message.author.mention}",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="__Error__", description=f"{member.mention} is already banned.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<user#1234>", description="Unbans a user from the discord server.")
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """ Unbans a user, e.g: .unban Pat#8616"""
        timestamp = ctx.message.created_at.strftime(self.time_format)
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(title="__User Unbanned__",
                                  description=f"{member} was unbanned by {ctx.message.author.mention}",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif member not in banned_users:
            embed = discord.Embed(title="__Error__", description=f"{member} is not banned.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<@user> <role>", description="Grants the user the role.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def roleadd(self, ctx, member: discord.Member, role: discord.Role):
        """ Adds the role to the user, e.g: .roleadd @Jam Member """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if role not in member.roles:
            await member.add_roles(role)
            embed = discord.Embed(title="**__Role Added__**",
                                  description=f"{member.mention} was given role {role.mention}",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif role in member.roles:
            embed = discord.Embed(title="**__Denied__**",
                                  description=f"{member.mention} already has role {role.mention}",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<@user> <role>", description="Removes the role from the user.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def roleremove(self, ctx, member: discord.Member, role: discord.Role = None):
        """ Removes the role from the user, e.g: .roleremove @Jam Member """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(title="**__Role Removed__**",
                                  description=f"{member.mention} was removed of role {role.mention}",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif role not in member.roles:
            embed = discord.Embed(title="**__Denied__**", description=f"{member.mention} does not have role {role}",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<@user>", description="Gives the user the Muted role.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        """ Adds the 'Muted' role to the user but only if there is a muted role, e.g: .mute @Jam """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        config = get_config()
        muted_role = config["muted_role"]
        role = get(member.guild.roles, name=muted_role)

        if role is None:
            embed = discord.Embed(title="**__Error__**", description="No `Muted` role has been set in the config.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif not get(ctx.guild.roles, name=muted_role):
            embed = discord.Embed(title="**__Error__**", description=f"**The role `{role}` does not exist.**",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif role not in member.roles:
            await member.add_roles(role)
            embed = discord.Embed(title="**__User Muted__**",
                                  description=f"{member.mention} was muted by {ctx.message.author.mention}",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif role in member.roles:
            embed = discord.Embed(title="**__Denied__**", description=f"{member.mention} is already muted.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<@user>", description="Removes the Muted role from the user.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """ Removes the 'Muted' role from the user """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        config = get_config()
        muted_role = config["muted_role"]
        role = get(member.guild.roles, name=muted_role)

        if role is None:
            embed = discord.Embed(title="**__Error__**", description="No `Muted` role has been set in the config.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif not get(ctx.guild.roles, name=muted_role):
            embed = discord.Embed(title="**__Error__**", description=f"**The role `{role}` does not exist.**",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(title="**__User Unmuted__**",
                                  description=f"{member.mention} was unmuted by {ctx.message.author.mention}",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif role not in member.roles:
            embed = discord.Embed(title="**__Denied__**", description=f"{member.mention} is not muted.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<amount>", description="Clears an amount of recent messages from the channel's history.",
                      aliases=['clear'])
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=10):
        """ Clears messages from chat: e.g .clear 100 """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(title="**__Clear__**", description=f'Cleared {amount} messages',
                              color=self.colors.get("green"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await message.delete()

    @commands.command(help="", description="Unbans all the banned users from the discord server.")
    @commands.guild_only()
    @has_permissions(manage_guild=True)
    async def unbanall(self, ctx):
        """ Command to unban all users from the guild """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        banned_users = await ctx.guild.bans()
        embed = discord.Embed(title="__Unban All__", description="Starting to unban users...",
                              color=self.colors.get("pink"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        message = await ctx.send(embed=embed)
        users = []

        for ban_entry in banned_users:
            user = ban_entry.user
            users.append(user)
            await ctx.guild.unban(user)

        embed = discord.Embed(title="__Unban All__", description=f"{len(users)} users have been unbanned.",
                              color=self.colors.get("green"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await message.edit(embed=embed)

    @commands.command(help="<role/role> <emoji/emoji>\ne.g reactionroles Member/Trusted :clap:/:eyes:",
                      description="Creates a message where the reactions give roles, seperate different roles or emojis with a '/' but seperate arguments with a space.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def reactionroles(self, ctx, roles=None, emojis=None):
        """ Reactionroles command to create an embed with reactions that saves the data to a config for the events to add roles on reactions """
        reaction_roles = get_reaction_roles()
        timestamp = ctx.message.created_at.strftime(self.time_format)
        try:
            roles = roles.split("/")
            emojis = emojis.split("/")
            message_string = ""

            if len(roles) != len(emojis):
                embed = discord.Embed(title="__Error__",
                                      description="Incorrect usage, make sure the number of roles match the number of emojis.",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

        except AttributeError:
            embed = discord.Embed(title="**Error**",
                                  description=f"Unknown emoji or incorrect format, use '{get_prefix()}help reactionroles' for more information.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            for role in roles:
                try:
                    role_to_check = get(ctx.guild.roles, name=role)
                    if role is None:
                        embed = discord.Embed(title="__Error__", description="No role(s) given.",
                                              color=self.colors.get("red"))
                        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                        await ctx.send(embed=embed)
                        break

                    if role_to_check not in ctx.guild.roles:
                        embed = discord.Embed(title="__Error__", description=f"Role: `{role}` not found.",
                                              color=self.colors.get("red"))
                        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                        await ctx.send(embed=embed)
                        break

                except AttributeError:
                    embed = discord.Embed(title="__Error__", description=f"Role: `{role}` not found.",
                                          color=self.colors.get("red"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)
                    break

            for reaction in emojis:
                if reaction is None:
                    embed = discord.Embed(title="__Error__", description="No emoji(s) given.",
                                          color=self.colors.get("red"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)
                    break

                if role_to_check in ctx.guild.roles:
                    for i, _emoji in enumerate(emojis):
                        message_string += f"{emojis[i]} : `{roles[i]}`\n"

                    embed = discord.Embed(title="**__Reaction Roles__**",
                                          description=f"**React here to recieve roles:**\n{message_string}",
                                          color=self.colors.get("green"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    message = await ctx.send(embed=embed)
                    self.message_ids.append(message.id)

                    for final_reaction in emojis:
                        await message.add_reaction(final_reaction)

                    reaction_roles["reaction_messages"].append({
                        "message_id": message.id,
                        "reaction_emojis": emojis,
                        "reaction_roles": roles
                    })

                    with open("data/reaction_roles.json", "w", encoding="UTF-8") as i:
                        json.dump(reaction_roles, i, indent=4, ensure_ascii=False)

                    await ctx.message.delete()
                    break

    @commands.command(
        help="<emoji/emoji> <message>\n(One reaction is required but multiple can be used if they are split by a '/'.\nMake sure that there are no spaces between multiple reactions.)",
        description="Creates a message that users can react to, seperate reactions with a '/' but seperate different arguments with a space.")
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def poll(self, ctx, emoji=None, *, message=None):
        """ Command to create an embedded poll message with multiple reactions e.g .poll :yes:/:no: Red Wallpaper? """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        try:
            emojis = emoji.split("/")

            if emoji is None:
                embed = discord.Embed(title="__Error__", description="No emoji(s) given.", color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

            elif message is None:
                embed = discord.Embed(title="__Error__", description="No message given for the poll to be created.",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title="**__Poll__**", description=f"{message}", color=self.colors.get("green"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                message = await ctx.send(embed=embed)
                self.message_ids.append(message.id)

                for reaction in emojis:
                    await message.add_reaction(reaction)

                await ctx.message.delete()

        except AttributeError:
            embed = discord.Embed(title="**Error**",
                                  description=f"Unknown emoji or incorrect format, use '{get_prefix()}help poll' for more information.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @poll.error
    async def poll_error(self, ctx, error):
        """ Function to catch the poll command's errors """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if isinstance(error, commands.errors.CommandInvokeError):
            async for message in ctx.channel.history(limit=2):
                if message.author.id == self.bot.user.id:
                    if message.id in self.message_ids:
                        await message.delete()
                        break

            embed = discord.Embed(title="**Error**",
                                  description=f"Unknown emoji or incorrect format, use '{get_prefix()}help poll' for more information.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @reactionroles.error
    async def reactions_error(self, ctx, error):
        """ Function to catch reactionroles command errors """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if isinstance(error, commands.errors.CommandInvokeError):
            async for message in ctx.channel.history(limit=2):
                if message.author.id == self.bot.user.id:
                    if message.id in self.message_ids:
                        await message.delete()
                        break

            embed = discord.Embed(title="**Error**",
                                  description=f"Unknown emoji or incorrect format, use '{get_prefix()}help reactionroles' for more information.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<@user> <name>", description="Change a user's nickname in the server.")
    @commands.guild_only()
    @has_permissions(change_nickname=True)
    async def nick(self, ctx, user: discord.Member = None, *, name=None):
        """ Command to change a user's nickname e.g .nick @Jam Jammy """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if user is None:
            embed = discord.Embed(title="__Error__", description="No user given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif name is None:
            embed = discord.Embed(title="__Error__", description="No name given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            await user.edit(nick=name)
            embed = discord.Embed(title="__Nick Changed__",
                                  description=f"{user.mention}'s nick was changed to `{name}`",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(
        help="<time> <description>\n\n This command can be typed in any channel and it will be sent in the giveaways channel aslong as the channel's id is set in the config.",
        description="Staff command to start a giveaway in the giveaways channel. e.g: giveaway 1d Highest Rank")
    @has_permissions(manage_messages=True)
    async def giveaway(self, ctx, timer, *, message=None):
        """ Staff command to start a giveaway """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        config = get_config()
        channel_id = self.data["giveaways_channel_id"]
        if channel_id is None:
            embed = discord.Embed(title="__Error__",
                                  description="Please enter your 'giveaways' channel ID into the config file.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            if "d" in timer:
                timer = timer.replace("d", "")
                timer = int(timer)
                timer *= 86400

            elif "h" in timer:
                timer = timer.replace("h", "")
                timer = int(timer)
                timer *= 3600

            elif "m" in timer:
                timer = timer.replace("m", "")
                timer = int(timer)
                timer *= 60

            else:
                embed = discord.Embed(title="__Error__",
                                      description=f"Invalid time format. Please choose either days (d), hours (h) or minutes (m).\n e.g: {config['prefix']}giveaway 5h Top Rank!",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

            seconds = timer
            seconds_in_day = 60 * 60 * 24
            seconds_in_hour = 60 * 60
            seconds_in_minute = 60

            days = seconds // seconds_in_day
            hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
            minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
            secs = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) - (minutes * seconds_in_minute)

            channel = self.bot.get_channel(channel_id)
            embed = discord.Embed(title=":partying_face: **__Giveaway__** :partying_face: ",
                                  description=f"{message}\n\n **Ends in: {days}d {hours}h {minutes}m {secs}s.**\n\n*Started by: {ctx.message.author.mention}*",
                                  color=self.colors.get("blue"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            giveaway = await channel.send(embed=embed)
            await giveaway.add_reaction("🎉")
            await ctx.message.delete()

            while timer > 0:
                if timer > 60:
                    await asyncio.sleep(60)
                    timer -= 60
                    seconds = timer
                    seconds_in_day = 60 * 60 * 24
                    seconds_in_hour = 60 * 60
                    seconds_in_minute = 60

                    days = seconds // seconds_in_day
                    hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
                    minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
                    secs = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) - (
                                minutes * seconds_in_minute)
                    embed = discord.Embed(title=":partying_face: **__Giveaway__** :partying_face: ",
                                          description=f"{message}\n\n **Ends in: {days}d {hours}h {minutes}m.**\n\n*Started by: {ctx.message.author.mention}*",
                                          color=self.colors.get("blue"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await giveaway.edit(embed=embed)

                else:
                    if timer <= 60:
                        await asyncio.sleep(1)
                        timer -= 1
                        seconds = timer
                        seconds_in_day = 60 * 60 * 24
                        seconds_in_hour = 60 * 60
                        seconds_in_minute = 60

                        days = seconds // seconds_in_day
                        hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
                        minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
                        secs = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) - (
                                    minutes * seconds_in_minute)
                        embed = discord.Embed(title=":partying_face: **__Giveaway__** :partying_face: ",
                                              description=f"{message}\n\n **Ends in: {days}d {hours}h {minutes}m {secs}s.**\n\n*Started by: {ctx.message.author.mention}*",
                                              color=self.colors.get("blue"))
                        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                        await giveaway.edit(embed=embed)

            if timer == 0:
                msg = await giveaway.channel.fetch_message(giveaway.id)
                for reaction in msg.reactions:
                    if reaction.emoji == "🎉":
                        members = await reaction.users().flatten()
                        member = random.choice(members)
                        member = self.bot.get_user(member.id)

                        embed = discord.Embed(title=":partying_face: **__Giveaway__** :partying_face: ",
                                              description=f"{message}\n\n **Ended.**\n\n*Started by: {ctx.message.author.mention}*",
                                              color=self.colors.get("red"))
                        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                        await giveaway.edit(embed=embed)
                        await giveaway.edit(content=f"🎉 **{member.mention} has won the giveaway of**: `{message}`")

    @commands.command(help="<message id>", description="Selects a different user to win the giveaway.")
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def reroll(self, ctx, message_id=None):
        """ Staff command to re-roll the latest giveaway """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        config = get_config()
        channel_id = config["giveaways_channel_id"]
        if message_id is None:
            embed = discord.Embed(title="__Error__", description="No message id was given to reroll.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif channel_id is None:
            embed = discord.Embed(title="__Error__",
                                  description="Please enter your 'giveaways' channel ID into the config file.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            await ctx.message.delete()
            message = await ctx.fetch_message(message_id)
            for reaction in message.reactions:
                if reaction.emoji == "🎉":
                    members = await reaction.users().flatten()
                    member = random.choice(members)
                    member = self.bot.get_user(member.id)
                    msg = message.content.split(":")
                    await message.edit(content=f"🎉 **{member.mention} has won the giveaway re-roll of**:{msg[1]}")


def get_config():
    """ Function to get the config file's data """
    try:
        with open(CONFIG_FILE, "r", encoding="UTF-8") as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def get_prefix():
    """ Function to get the prefix data """
    try:
        with open(CONFIG_FILE, "r", encoding="UTF-8") as i:
            prefix_data = json.load(i)
            return prefix_data["prefix"]

    except FileNotFoundError as error:
        print(error)


def get_reaction_roles():
    """ Function to get the reaction-roles file's data """
    try:
        with open("data/reaction_roles.json", "r", encoding="UTF-8") as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Moderation(bot))
