""" Management module to define all moderation commands seperately for easier sorting """
import asyncio
import json
import random

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get
import methods


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
        """ Creates an embedded message where the user can type a message to send
            e.g .announce __Announcement__ this is a test """
        await ctx.message.delete()
        await ctx.send(embed=methods.return_embed(self, ctx, title=None, description=message,
                                                  color="blue"))

    @commands.command(help="<role> (Leave empty to mute everyone)",
                      description="Mutes the channel for all members with the role specified.",
                      aliases=["lock", "channellock"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def channelmute(self, ctx, role: discord.Role = None):
        """ Mutes the channel for a specific role, leave the argument empty to mute everyone """
        if role is None:
            role = get(ctx.guild.roles, name='@everyone')
            await ctx.message.channel.set_permissions(role, send_messages=False)
            title = "**__Channel Muted__**"
            description = "All members in this channel have been muted."
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        else:
            await ctx.message.channel.set_permissions(role, send_messages=False)
            title = "**__Channel Muted__**"
            description = f"All members in this channel with the role `{role}` have been muted."
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<role> (Leave empty to mute everyone)",
                      description="Un-mutes the channel for all members with the role specified.",
                      aliases=["unlock", "channelunlock"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def channelunmute(self, ctx, role: discord.Role = None):
        """ Unmutes the channel for a specific role, leave the argument empty to unmute everyone """
        if role is None:
            role = get(ctx.guild.roles, name='@everyone')
            await ctx.message.channel.set_permissions(role, send_messages=True)
            title = "**__Channel Un-muted__**"
            description = "All members in this channel have been un-muted."
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        else:
            await ctx.message.channel.set_permissions(role, send_messages=True)
            title = "**__Channel Un-muted__**"
            description = f"All members in this channel with the role `{role}` have been un-muted."
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<seconds>",
                      description="Enables slow-mode with a time between messages, enter '0' or 'off' to turn it off.")
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def slowmode(self, ctx, time: int = None):
        """ Enables slow-mode in the channel, set the time between messages using (prefix)slow-mode (time) """
        if time == "off":
            channel = ctx.message.channel
            await channel.edit(slowmode_delay=0)
            title = "**__Slow-mode__**"
            description = "Slow-mode has been turned off in this channel."
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        elif time is not None:
            desc = "This channel's slowmode has been set to 1 second." if time == '1' else \
                f"This channel's slowmode has been set to {time} seconds."
            channel = ctx.message.channel
            await channel.edit(slowmode_delay=time)
            await ctx.send(embed=methods.return_embed(self, ctx, title="__Slow-mode__", description=desc,
                                                      color="green"))
        else:
            await ctx.send(embed=methods.return_error(self, ctx, error="No time was given."))

    @commands.command(help="<@user> <reason> (Reason is not required.)",
                      description="Kicks a user from the discord server.")
    @commands.guild_only()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """ Kicks a user .kick @Pat """
        await member.kick(reason=reason)
        title = "__User Kicked__"
        description = f"{member.mention} was kicked by {ctx.message.author.mention}"
        await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<@user> <reason> (Reason is not required.)",
                      description="Bans a user from the discord server.")
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """ Bans a user .ban @Pat """
        banned_users = await ctx.guild.bans()
        if member not in banned_users:
            await member.ban(reason=reason)
            title = "__User Banned__"
            description = f"{member.mention} was banned by {ctx.message.author.mention}"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))
        else:
            await ctx.send(embed=methods.return_error(self, ctx, error=f"{member.mention} is already banned."))

    @commands.command(help="<user#1234>", description="Unbans a user from the discord server.")
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """ Unbans a user, e.g: .unban Pat#8616"""
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        user = None
        for ban_entry in banned_users:
            user = ban_entry.user

        if user not in banned_users:
            await ctx.send(embed=methods.return_error(self, ctx, error=f"{member} is not banned."))

        elif (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            title = "__User Unbanned__"
            description = f"{member} was unbanned by {ctx.message.author.mention}"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<@user> <role>", description="Grants the user the role.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def roleadd(self, ctx, member: discord.Member, role: discord.Role):
        """ Adds the role to the user, e.g: .roleadd @Jam Member """
        if role not in member.roles:
            await member.add_roles(role)
            title = "**__Role Added__**"
            description = f"{member.mention} was given role {role.mention}"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        elif role in member.roles:
            description = f"{member.mention} already has role {role.mention}"
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="<@user> <role>", description="Removes the role from the user.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def roleremove(self, ctx, member: discord.Member, role: discord.Role = None):
        """ Removes the role from the user, e.g: .roleremove @Jam Member """
        if role in member.roles:
            await member.remove_roles(role)
            title = "**__Role Removed__**"
            description = f"{member.mention} was removed of role {role.mention}"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        elif role not in member.roles:
            description = f"{member.mention} does not have role {role}"
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="<@user>", description="Gives the user the Muted role.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        """ Adds the 'Muted' role to the user but only if there is a muted role, e.g: .mute @Jam """
        config = methods.get_config()
        muted_role = config["muted_role"]
        role = get(member.guild.roles, name=muted_role)

        if role is None:
            description = "No `Muted` role has been set in the config."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif not get(ctx.guild.roles, name=muted_role):
            description = f"**The role `{role}` does not exist.**"
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif role not in member.roles:
            await member.add_roles(role)
            title = "**__User Muted__**"
            description = f"{member.mention} was muted by {ctx.message.author.mention}"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        elif role in member.roles:
            description = f"{member.mention} is already muted."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="<@user>", description="Removes the Muted role from the user.")
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """ Removes the 'Muted' role from the user """
        config = methods.get_config()
        muted_role = config["muted_role"]
        role = get(member.guild.roles, name=muted_role)

        if role is None:
            description = "No `Muted` role has been set in the config."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif not get(ctx.guild.roles, name=muted_role):
            description = f"**The role `{role}` does not exist.**"
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif role in member.roles:
            await member.remove_roles(role)
            title = "**__User Un-muted__**"
            description = f"{member.mention} was un-muted by {ctx.message.author.mention}"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        elif role not in member.roles:
            description = f"{member.mention} is not muted."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="<amount>", description="Clears an amount of recent messages from the channel's history.",
                      aliases=['clear'])
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=10):
        """ Clears messages from chat: e.g .clear 100 """
        await ctx.channel.purge(limit=amount)
        title = "**__Clear__**"
        description = f'Cleared {amount} messages'
        message = await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))
        await asyncio.sleep(2)
        await message.delete()

    @commands.command(help="", description="Unbans all the banned users from the discord server.")
    @commands.guild_only()
    @has_permissions(manage_guild=True)
    async def unbanall(self, ctx):
        """ Command to unban all users from the guild """
        banned_users = await ctx.guild.bans()
        title = "__Unban All__"
        description = "Starting to unban users..."
        message = await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="pink"))
        users = []

        for ban_entry in banned_users:
            user = ban_entry.user
            users.append(user)
            await ctx.guild.unban(user)

        description = f"{len(users)} users have been unbanned."
        await message.edit(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<role/role> <emoji/emoji>\ne.g reactionroles Member/Trusted :clap:/:eyes:",
                      description=("Creates a message where the reactions give roles, "
                                   "separate different roles or emojis with a '/' but separate arguments with a space"))
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    async def reactionroles(self, ctx, roles=None, emojis=None):
        """ Command to create an embed with reactions that saves the data to a config:
            for the events to add specific roles on reactions """
        reaction_roles = methods.get_reaction_roles()
        role_to_check = None
        try:
            roles = roles.split("/")
            emojis = emojis.split("/")
            message_string = ""

            if len(roles) != len(emojis):
                description = "Incorrect usage, make sure the number of roles match the number of emojis."
                await ctx.send(embed=methods.return_error(self, ctx, error=description))

        except AttributeError:
            description = ("Unknown emoji or incorrect format, "
                           f"use '{methods.get_prefix()}help reactionroles' for more information.")
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        else:
            for role in roles:
                try:
                    role_to_check = get(ctx.guild.roles, name=role)
                    if role is None:
                        await ctx.send(embed=methods.return_error(self, ctx, error="No role(s) given"))
                        break

                    if role_to_check not in ctx.guild.roles:
                        await ctx.send(embed=methods.return_error(self, ctx, error=f"Role: `{role}` not found."))
                        break

                except AttributeError:
                    await ctx.send(embed=methods.return_error(self, ctx, error=f"Role: `{role}` not found."))
                    break

            for reaction in emojis:
                if reaction is None:
                    await ctx.send(embed=methods.return_error(self, ctx, error="No emoji(s) given."))
                    break

                if role_to_check in ctx.guild.roles:
                    for i, _emoji in enumerate(emojis):
                        message_string += f"{emojis[i]} : `{roles[i]}`\n"

                    title = "**__Reaction Roles__**"
                    description = f"**React here to receive roles:**\n{message_string}"
                    message = await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))
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
        help=("<emoji/emoji> <message>\n(One reaction is required but multiple can be used if they are split by a '/'."
              "\n(Make sure that there are no spaces between multiple reactions)"),
        description=("Creates a message that users can react to, "
                     "separate reactions with a '/' but separate different arguments with a space."))
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def poll(self, ctx, emoji=None, *, message=None):
        """ Command to create an embedded poll message with multiple reactions e.g .poll :yes:/:no: Red Wallpaper? """
        try:
            emojis = emoji.split("/")

            if emoji is None:
                await ctx.send(embed=methods.return_error(self, ctx, error="No emoji(s) given."))
            elif message is None:
                await ctx.send(embed=methods.return_error(self, ctx, error="No message given to create the poll with."))
            else:
                title = "**__Poll__**"
                description = f"{message}"
                message = await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))
                self.message_ids.append(message.id)

                for reaction in emojis:
                    await message.add_reaction(reaction)

                await ctx.message.delete()

        except discord.HTTPException:
            await message.delete()
            description = f"Unknown emoji or incorrect format, " \
                          f"use '{methods.get_prefix()}help poll' for more information."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        except AttributeError:
            description = f"Unknown emoji or incorrect format, " \
                          f"use '{methods.get_prefix()}help poll' for more information."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="<@user> <name>", description="Change a user's nickname in the server.")
    @commands.guild_only()
    @has_permissions(change_nickname=True)
    async def nick(self, ctx, user: discord.Member = None, *, name=None):
        """ Command to change a user's nickname e.g .nick @Jam Jammy """
        if user is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No user given."))
        elif name is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No name given."))
        else:
            await user.edit(nick=name)
            title = "__Nick Changed__"
            description = f"{user.mention}'s nick was changed to `{name}`"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(
        help="<time> <description>\n\n (Make sure the giveaway channel id is set in the config)",
        description="Staff command to start a giveaway in the giveaways channel. e.g: giveaway 1d Highest Rank")
    @has_permissions(manage_messages=True)
    async def giveaway(self, ctx, timer, *, message=None):
        """ Staff command to start a giveaway """
        config = methods.get_config()
        channel_id = config["giveaways_channel_id"]
        if channel_id is None:
            description = "Please enter your 'giveaways' channel ID into the config file."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

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
                description = f"Invalid time format. Please choose either days (d), hours (h) or minutes (m).\n " \
                              f"e.g: {config['prefix']}giveaway 5h Top Rank!"
                await ctx.send(embed=methods.return_error(self, ctx, error=description))

            days, hours, minutes, secs = calc_time(timer)
            channel = self.bot.get_channel(channel_id)
            title = ":partying_face: **__Giveaway__** :partying_face: "
            description = f"{message}\n\n **Ends in: {days}d {hours}h {minutes}m {secs}s.**\n\n" \
                          f"*Started by: {ctx.message.author.mention}*"
            giveaway = await channel.send(embed=methods.return_embed(self, ctx, title, description, color="blue"))
            await giveaway.add_reaction("🎉")
            await ctx.message.delete()

            while timer > 0:
                if timer > 60:
                    await asyncio.sleep(60)
                    timer -= 60
                    days, hours, minutes, secs = calc_time(timer)
                    title = ":partying_face: **__Giveaway__** :partying_face: "
                    description = f"{message}\n\n **Ends in: {days}d {hours}h {minutes}m.**\n\n" \
                                  f"*Started by: {ctx.message.author.mention}*"
                    await giveaway.edit(embed=methods.return_embed(self, ctx, title, description, color="blue"))

                else:
                    if timer <= 60:
                        await asyncio.sleep(1)
                        timer -= 1
                        days, hours, minutes, secs = calc_time(timer)
                        title = ":partying_face: **__Giveaway__** :partying_face: "
                        description = f"{message}\n\n **Ends in: {days}d {hours}h {minutes}m {secs}s.**\n\n" \
                                      f"*Started by: {ctx.message.author.mention}*"
                        await giveaway.edit(embed=methods.return_embed(self, ctx, title, description, color="blue"))

            if timer == 0:
                msg = await giveaway.channel.fetch_message(giveaway.id)
                for reaction in msg.reactions:
                    if reaction.emoji == "🎉":
                        members = await reaction.users().flatten()
                        member = random.choice(members)
                        member = self.bot.get_user(member.id)

                        title = ":partying_face: **__Giveaway__** :partying_face: "
                        description = f"{message}\n\n **Ended.**\n\n*Started by: {ctx.message.author.mention}*"
                        await giveaway.edit(embed=methods.return_embed(self, ctx, title, description, color="red"))
                        await giveaway.edit(content=f"🎉 **{member.mention} has won the giveaway of**: `{message}`")

    @commands.command(help="<message id>", description="Selects a different user to win the giveaway.")
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def reroll(self, ctx, message_id=None):
        """ Staff command to re-roll the latest giveaway """
        config = methods.get_config()
        channel_id = config["giveaways_channel_id"]
        if message_id is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No message ID was given to re-roll with."))
        elif channel_id is None:
            description = "Please enter your 'giveaways' channel ID into the config file."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))
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


def calc_time(seconds):
    """ Function to calculate the time left in giveaway countdown """
    seconds_in_day = 60 * 60 * 24
    seconds_in_hour = 60 * 60
    seconds_in_minute = 60

    days = seconds // seconds_in_day
    hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
    minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
    secs = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) - (minutes * seconds_in_minute)
    return days, hours, minutes, secs


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Moderation(bot))
