""" Tickets cog that defines all the ticket commands """
import json
import os
import sqlite3

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get

CONFIG_FILE = "data/config.json"
TICKET_FILE = "data/tickets.db"


class Tickets(commands.Cog):
    """ Main Ticket class to setup attributes and methods to be called on each event """

    def __init__(self, bot):
        """ Class initialization method to define class attributes """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.data = get_config()
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff, "blue": 0x0080c0}
        print(f"{self.__class__.__name__} cog loaded.")

    @commands.command(help="",
                      description="Creates a ticket to ask for support, users may only open 1 ticket at a time.",
                      aliases=["new", "createticket"])
    @commands.guild_only()
    async def ticket(self, ctx):
        """ Creates a ticket channel in the ticket category and mentions the user (MAKE SURE THERE IS A TICKET CATEGORY) """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        try:
            conn = sqlite3.connect(TICKET_FILE)
            cursor = conn.cursor()
            select = """ SELECT ticket_id, user_id FROM tickets; """
            cursor.execute(select)
            data = cursor.fetchall()
            conn.commit()

        except FileNotFoundError as error:
            print(error)
            conn.close()

        except IOError as error:
            print(error)
            conn.close()

        tuples = list(zip(*data))
        tickets = [] if tuples == [] else tuples[0]
        user_ids = [] if tuples == [] else tuples[1]
        ticket_number = int(max(tickets)) if tickets != [] else 1000
        category_check = get(ctx.guild.categories, name="tickets")

        if ctx.author.id in user_ids:
            embed = discord.Embed(title="**__Error__**",
                                  description="You already have a ticket open, this ticket must be closed before you can open another.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            conn.close()

        elif category_check not in ctx.guild.categories:
            embed = discord.Embed(title="**__Error__**",
                                  description="There is no category named 'tickets' for the channel to be created, please create one and set your permissions correctly.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            conn.close()

        elif ctx.author.id not in user_ids and (ticket_number + 1) not in tickets:
            ticket_number += 1
            ticket_channel = f"ticket-{ticket_number}"

            category = get(ctx.guild.categories, name="tickets")

            ticket = await ctx.message.guild.create_text_channel(ticket_channel, category=category)
            channel = self.bot.get_channel(ticket.id)
            overwrite = discord.PermissionOverwrite()
            overwrite.update(read_messages=True, read_message_history=True, send_messages=True)
            await channel.set_permissions(ctx.author, overwrite=overwrite)

            msg = "**__Ticket Support__**\n**Please describe your issue in detail and a staff member should assist you shortly.**"
            await channel.send(f"{msg}\n{ctx.author.mention}")
            embed = discord.Embed(title="**__Ticket Created__**",
                                  description="**A ticket channel has been created for you.**",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

            data = f""" INSERT INTO tickets(ticket_id, user_id, channel_id)             
                        VALUES({ticket_number}, {ctx.author.id}, {channel.id}) """

            cursor.execute(data)
            conn.commit()
            conn.close()

    @commands.command(help="<@user>", description="Adds a user to the ticket.", aliases=["add", "ticket_add", "tadd"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def ticketadd(self, ctx, user: discord.Member = None):
        """ Ticket command to add a user to the ticket channel, requires manage channel permissions """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if user is None:
            embed = discord.Embed(title="__Error__", description="No user given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            try:
                conn = sqlite3.connect(TICKET_FILE)
                cursor = conn.cursor()
                select = """ SELECT channel_id FROM tickets; """
                cursor.execute(select)
                data = cursor.fetchall()
                conn.commit()
                conn.close()

            except FileNotFoundError as error:
                print(error)
                conn.close()

            except IOError as error:
                print(error)
                conn.close()

            tuples = list(zip(*data))
            channel_ids = [] if tuples == [] else tuples[0]

            if ctx.channel.id in channel_ids:
                try:
                    channel = self.bot.get_channel(ctx.channel.id)
                    overwrite = discord.PermissionOverwrite()
                    overwrite.update(read_messages=True, read_message_history=True, send_messages=True)
                    await channel.set_permissions(user, overwrite=overwrite)

                    embed = discord.Embed(title="__Success__", description=f"Added {user.mention} to ticket.",
                                          color=self.colors.get("green"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)

                except:
                    embed = discord.Embed(title="__Error__",
                                          description=f"Failed to add {user.mention} to the ticket, they may already be added.",
                                          color=self.colors.get("red"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title="__Error__", description="This channel is not a ticket.",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(help="<@user>", description="Removes a user from a ticket.",
                      aliases=["remove", "ticket_remove", "remove_user", "tremove"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def ticketremove(self, ctx, user: discord.Member = None):
        """ Ticket command to remove a user from the ticket channel, requires manage channel permissions """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if user is None:
            embed = discord.Embed(title="__Error__", description="No user given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            try:
                conn = sqlite3.connect(TICKET_FILE)
                cursor = conn.cursor()
                select = """ SELECT channel_id FROM tickets; """
                cursor.execute(select)
                data = cursor.fetchall()
                conn.commit()
                conn.close()

            except FileNotFoundError as error:
                print(error)
                conn.close()

            except IOError as error:
                print(error)
                conn.close()

            tuples = list(zip(*data))
            channel_ids = [] if tuples == [] else tuples[0]

            if ctx.channel.id in channel_ids:
                try:
                    channel = self.bot.get_channel(ctx.channel.id)
                    overwrite = discord.PermissionOverwrite()
                    overwrite.update(read_messages=False, read_message_history=False, send_messages=False)
                    await channel.set_permissions(user, overwrite=overwrite)

                    embed = discord.Embed(title="__Success__", description=f"Removed {user.mention} from the ticket.",
                                          color=self.colors.get("green"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)

                except:
                    embed = discord.Embed(title="__Error__",
                                          description=f"Failed to remove {user.mention} to the ticket, they may not be added.",
                                          color=self.colors.get("red"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title="__Error__", description="This channel is not a ticket.",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(help="<reason>", description="Closes the ticket with a final message.")
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def close(self, ctx, *, message=None):
        """ Ticket command to close the ticket, requires manage channel permissions """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        try:
            conn = sqlite3.connect(TICKET_FILE)
            cursor = conn.cursor()
            select = """ SELECT user_id, channel_id FROM tickets; """
            cursor.execute(select)
            data = cursor.fetchall()
            conn.commit()

        except FileNotFoundError as error:
            print(error)
            conn.close()

        except IOError as error:
            print(error)
            conn.close()

        tuples = list(zip(*data))
        channel_ids = [] if tuples == [] else tuples[1]
        user_ids = [] if tuples == [] else tuples[0]

        for channel_id in channel_ids:
            if ctx.channel.id == channel_id:
                index = channel_ids.index(channel_id)
                user_id = user_ids[index]
                break

        if ctx.channel.id not in channel_ids:
            embed = discord.Embed(title="__Error__", description="This channel is not a ticket.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            conn.close()

        else:
            try:
                transcript = {}
                member = self.bot.get_user(user_id)

                await ctx.send(f"Ticket Closed by {ctx.message.author}\nReason: {message}")
                headers = {"Authorization": f"Bot {self.data['token']}"}
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(f"https://discord.com/api/channels/{ctx.channel.id}/messages",
                                           params={"limit": 100}) as i:
                        if i.status == 200:
                            data = await i.json()
                            for line in data:
                                date = line.get("timestamp").split("T")
                                msg = line.get("content")
                                author = line.get("author")
                                user = author.get("username")
                                tag = author.get("discriminator")
                                transcript.update({f"[{date[0]} {date[1][:11]} UTC]": f"{user}#{tag} : {msg}\n"})
                            values = sorted(transcript.items(), key=lambda kv: kv[0])
                            for key, value in values:
                                with open(f"{ctx.channel}.txt", "a", encoding="UTF-16") as i:
                                    i.write(f"{key} {value}")

                            file = discord.File(f"{ctx.channel}.txt", filename=f"{ctx.channel}.txt")
                            await member.send("Your ticket was closed, here is the transcript.", file=file)
                            os.remove(f"{ctx.channel}.txt")
                            delete = f""" DELETE FROM tickets WHERE channel_id = {ctx.channel.id}; """
                            cursor.execute(delete)
                            data = cursor.fetchall()
                            conn.commit()
                            conn.close()
                            await ctx.channel.delete()

            except Exception as error:
                print(error)
                conn.close()

    @commands.command(help="",
                      description="Creates an embed where users can react to open a ticket, only one of these messages can be active at a time.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def setuptickets(self, ctx):
        """ Ticket command to create a reaction embed where users can create tickets by reacting, requires administrator permissions """
        await ctx.message.delete()
        timestamp = ctx.message.created_at.strftime(self.time_format)
        category_check = bool(get(ctx.guild.categories, name="tickets"))

        if not category_check:
            embed = discord.Embed(title="__Error__",
                                  description="There is no category named 'tickets' for the channel to be created in, a staff member must create one and set their desired permissions.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="__Create a ticket__",
                                  description=f"**React here to open a ticket or type {get_prefix()}ticket.**",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")

            try:
                self.data["ticket_setup_id"] = message.id
                with open(CONFIG_FILE, "w") as i:
                    json.dump(self.data, i, indent=4)

            except FileNotFoundError as error:
                print(error)

            except IOError as error:
                print(error)

    @commands.command(help="<name>", description="Renames a ticket channel.", aliases=["ticketrename", "rename"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def trename(self, ctx, *, name=None):
        """ Ticket command to rename a ticket, requires manage channel permissions """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        channel = self.bot.get_channel(ctx.channel.id)
        if name is None:
            embed = discord.Embed(title="__Error__", description="No name was given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            try:
                conn = sqlite3.connect(TICKET_FILE)
                cursor = conn.cursor()
                select = """ SELECT channel_id FROM tickets; """
                cursor.execute(select)
                data = cursor.fetchall()
                conn.commit()
                conn.close()

            except FileNotFoundError as error:
                print(error)
                conn.close()

            except IOError as error:
                print(error)
                conn.close()

            tuples = list(zip(*data))
            channel_ids = [] if tuples == [] else tuples[0]

            if ctx.channel.id in channel_ids:
                await channel.edit(name=name)
                embed = discord.Embed(title="__Channel Renamed__",
                                      description=f"This ticket channel was renamed to {channel.mention}",
                                      color=self.colors.get("green"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title="__Error__", description=f"{channel.mention} is not a ticket.",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(help="<role>", description="Ability to add or remove roles from viewing the ticket.",
                      aliases=["ticketrole"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def trole(self, ctx, arg=None, role: discord.Role = None):
        """ Ticket command to add/remove a role's ability to interact with a ticket, requires manage channel permissions """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        channel = self.bot.get_channel(ctx.channel.id)

        if role is None or role not in ctx.guild.roles:
            embed = discord.Embed(title="__Error__", description="Invalid Role.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif arg is None:
            embed = discord.Embed(title="__Error__",
                                  description="No type was given, please choose from 'add' or 'remove'.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif arg in ("add", "remove"):
            try:
                conn = sqlite3.connect(TICKET_FILE)
                cursor = conn.cursor()
                select = """ SELECT channel_id FROM tickets; """
                cursor.execute(select)
                data = cursor.fetchall()
                conn.commit()
                conn.close()

            except FileNotFoundError as error:
                print(error)
                conn.close()

            except IOError as error:
                print(error)
                conn.close()

            tuples = list(zip(*data))
            channel_ids = [] if tuples == [] else tuples[0]

            if ctx.channel.id in channel_ids:
                if arg == "add":
                    overwrite = discord.PermissionOverwrite()
                    overwrite.update(read_messages=True, read_message_history=True, send_messages=True)
                    await channel.set_permissions(role, overwrite=overwrite)
                    embed = discord.Embed(title="__Success__", description=f"{role.mention} was added to this ticket.",
                                          color=self.colors.get("green"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)

                elif arg == "remove":
                    overwrite = discord.PermissionOverwrite()
                    overwrite.update(read_messages=False, read_message_history=False, send_messages=False)
                    await channel.set_permissions(role, overwrite=overwrite)
                    embed = discord.Embed(title="__Success__",
                                          description=f"{role.mention} was removed from this ticket.",
                                          color=self.colors.get("green"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title="__Error__", description=f"{channel.mention} is not a ticket.",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(help="", description="Upgrades a ticket so only that only admins can view it.",
                      aliases=["upgrade", "ticketupgrade"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def tupgrade(self, ctx):
        """ Ticket command to upgrade a ticket so only admins can view, requires manage channels permissions """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        channel = self.bot.get_channel(ctx.channel.id)
        try:
            conn = sqlite3.connect(TICKET_FILE)
            cursor = conn.cursor()
            select = """ SELECT channel_id FROM tickets; """
            cursor.execute(select)
            data = cursor.fetchall()
            conn.commit()
            conn.close()

        except FileNotFoundError as error:
            print(error)
            conn.close()

        except IOError as error:
            print(error)
            conn.close()

        tuples = list(zip(*data))
        channel_ids = [] if tuples == [] else tuples[0]

        if ctx.channel.id in channel_ids:
            for role in ctx.guild.roles:
                overwrite = discord.PermissionOverwrite()
                overwrite.update(read_messages=False, read_message_history=False, send_messages=False)
                await channel.set_permissions(role, overwrite=overwrite)

            embed = discord.Embed(title="__Success__",
                                  description="Only users with administrator permissions can now view this ticket",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="__Error__", description=f"{channel.mention} is not a ticket.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)


def get_config():
    """ Function to get the config data """
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


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Tickets(bot))
