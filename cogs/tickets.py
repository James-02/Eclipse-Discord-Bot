""" Tickets cog that defines all the ticket commands """
import os

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get
import methods


def get_channel_id():
    """ Function to fetch the channel_id column from the tickets table. """
    select = """ SELECT channel_id FROM tickets; """
    data = methods.send_query(select)
    tuples = list(zip(*data))
    channel_ids = [] if tuples == [] else tuples[0]
    return channel_ids


class Tickets(commands.Cog):
    """ Main Ticket class to setup attributes and methods to be called on each event """

    def __init__(self, bot):
        """ Class initialization method to define class attributes """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff, "blue": 0x0080c0}
        print(f"{self.__class__.__name__} cog loaded.")

    @commands.command(help="",
                      description="Creates a ticket to ask for support, users may only open 1 ticket at a time.",
                      aliases=["new", "createticket"])
    @commands.guild_only()
    async def ticket(self, ctx):
        """ Creates a ticket channel in the ticket category and mentions the user
            (MAKE SURE THERE IS A TICKET CATEGORY) """
        select = """ SELECT ticket_id, user_id FROM tickets; """
        data = methods.send_query(select)
        tuples = list(zip(*data))
        tickets = [] if tuples == [] else tuples[0]
        user_ids = [] if tuples == [] else tuples[1]
        ticket_number = int(max(tickets)) if tickets != [] else 1000
        category_check = get(ctx.guild.categories, name="tickets")

        if ctx.author.id in user_ids:
            description = "You already have a ticket open, this ticket must be closed before you can open another."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif category_check not in ctx.guild.categories:
            description = """There is no category named 'tickets' for the channel to be created, 
                            please create one and set your permissions correctly."""
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif ctx.author.id not in user_ids and (ticket_number + 1) not in tickets:
            ticket_number += 1
            ticket_channel = f"ticket-{ticket_number}"

            category = get(ctx.guild.categories, name="tickets")

            ticket = await ctx.message.guild.create_text_channel(ticket_channel, category=category)
            channel = self.bot.get_channel(ticket.id)
            overwrite = discord.PermissionOverwrite()
            overwrite.update(read_messages=True, read_message_history=True, send_messages=True)
            await channel.set_permissions(ctx.author, overwrite=overwrite)

            msg = ("**__Ticket Support__**\n\n"
                   "**Please describe your issue in detail and a staff member should assist you shortly.**")

            await channel.send(f"{msg}\n{ctx.author.mention}")
            title = "**__Ticket Created__**"
            description = "**A ticket channel has been created for you.**"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            insert = f""" INSERT INTO tickets(ticket_id, user_id, channel_id)             
                        VALUES({ticket_number}, {ctx.author.id}, {channel.id}) """
            methods.send_query(insert)

    @commands.command(help="<@user>", description="Adds a user to the ticket.", aliases=["add", "ticket_add", "tadd"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def ticketadd(self, ctx, user: discord.Member = None):
        """ Ticket command to add a user to the ticket channel, requires manage channel permissions """
        if user is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No user given"))

        else:
            channel_ids = get_channel_id()

            if ctx.channel.id in channel_ids:
                channel = self.bot.get_channel(ctx.channel.id)
                overwrite = discord.PermissionOverwrite()
                overwrite.update(read_messages=True, read_message_history=True, send_messages=True)
                await channel.set_permissions(user, overwrite=overwrite)
                title = "__Success__"
                description = f"Added {user.mention} to ticket."
                await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            else:
                await ctx.send(embed=methods.return_error(self, ctx, error="This channel is not a ticket."))

    @commands.command(help="<@user>", description="Removes a user from a ticket.",
                      aliases=["remove", "ticket_remove", "remove_user", "tremove"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def ticketremove(self, ctx, user: discord.Member = None):
        """ Ticket command to remove a user from the ticket channel, requires manage channel permissions """
        if user is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No user given."))

        else:
            channel_ids = get_channel_id()

            if ctx.channel.id in channel_ids:
                channel = self.bot.get_channel(ctx.channel.id)
                overwrite = discord.PermissionOverwrite()
                overwrite.update(read_messages=False, read_message_history=False, send_messages=False)
                await channel.set_permissions(user, overwrite=overwrite)

                title = "__Success__"
                description = f"Removed {user.mention} from the ticket."
                await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            else:
                await ctx.send(embed=methods.return_error(self, ctx, error="This channel is not a ticket."))

    @commands.command(help="<reason>", description="Closes the ticket with a final message.")
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def close(self, ctx, *, message=None):
        """ Ticket command to close the ticket, requires manage channel permissions """
        select = """ SELECT user_id, channel_id FROM tickets; """
        data = methods.send_query(select)
        tuples = list(zip(*data))
        channel_ids = [] if tuples == [] else tuples[1]
        user_ids = [] if tuples == [] else tuples[0]
        user_id = None

        for channel_id in channel_ids:
            if ctx.channel.id == channel_id:
                index = channel_ids.index(channel_id)
                user_id = user_ids[index]
                break

        if ctx.channel.id not in channel_ids:
            await ctx.send(embed=methods.return_error(self, ctx, error="This channel is not a ticket."))
        else:
            try:
                transcript = {}
                member = self.bot.get_user(user_id)
                config = methods.get_config()
                await ctx.send(f"Ticket Closed by {ctx.message.author}\nReason: {message}")
                headers = {"Authorization": f"Bot {config['token']}"}
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
                                with open(f"{ctx.channel}.txt", "a", encoding="UTF-16") as f:
                                    f.write(f"{key} {value}")

                            file = discord.File(f"{ctx.channel}.txt", filename=f"{ctx.channel}.txt")
                            await member.send("Your ticket was closed, here is the transcript.", file=file)
                            os.remove(f"{ctx.channel}.txt")
                            delete = f""" DELETE FROM tickets WHERE channel_id = {ctx.channel.id}; """
                            methods.send_query(delete)
                            await ctx.channel.delete()

            except Exception as error:
                print(error)

    @commands.command(help="",
                      description="""Creates an embed where users can react to open a ticket, 
                                    only one of these messages can be active at a time.""")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def setuptickets(self, ctx):
        """ Ticket command to create a reaction embed where users can create tickets by reacting,
            requires administrator permissions """
        await ctx.message.delete()
        category_check = bool(get(ctx.guild.categories, name="tickets"))

        if not category_check:
            description = """There is no category named 'tickets' for the channel to be created in, 
                            a staff member must create one and set their desired permissions."""
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        else:
            title = "__Create a ticket__"
            description = f"**React here to open a ticket or type {methods.get_prefix()}ticket.**"
            message = await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))
            await message.add_reaction("✅")

            config = methods.get_config()
            config["ticket_setup_id"] = message.id
            methods.set_config(config)

    @commands.command(help="<name>", description="Renames a ticket channel.", aliases=["ticketrename", "rename"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def trename(self, ctx, *, name=None):
        """ Ticket command to rename a ticket, requires manage channel permissions """
        channel = self.bot.get_channel(ctx.channel.id)
        if name is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No name was given."))
        else:
            channel_ids = get_channel_id()

            if ctx.channel.id in channel_ids:
                await channel.edit(name=name)
                title = "__Channel Renamed__"
                description = f"This ticket channel was renamed to {channel.mention}"
                await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            else:
                description = f"{channel.mention} is not a ticket."
                await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="<role>", description="Ability to add or remove roles from viewing the ticket.",
                      aliases=["ticketrole"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def trole(self, ctx, method=None, role: discord.Role = None):
        """ Ticket command to add/remove a role's ability to interact with a ticket,
            requires manage channel permissions """
        channel = self.bot.get_channel(ctx.channel.id)
        if method is None:
            description = "No type was given, please choose from 'add' or 'remove'."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        if role is None or role not in ctx.guild.roles:
            await ctx.send(embed=methods.return_error(self, ctx, error="Invalid Role"))

        elif method in ("add", "remove"):
            channel_ids = get_channel_id()
            overwrite = discord.PermissionOverwrite()

            if ctx.channel.id in channel_ids:
                if method == "add":
                    overwrite.update(read_messages=True, read_message_history=True, send_messages=True)
                    await channel.set_permissions(role, overwrite=overwrite)
                    title = "__Success__"
                    description = f"{role.mention} was added to this ticket."
                    await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

                elif method == "remove":
                    overwrite.update(read_messages=False, read_message_history=False, send_messages=False)
                    await channel.set_permissions(role, overwrite=overwrite)
                    title = "__Success__"
                    description = f"{role.mention} was removed from this ticket."
                    await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            else:
                description = f"{channel.mention} is not a ticket."
                await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="", description="Upgrades a ticket so only that only admins can view it.",
                      aliases=["upgrade", "ticketupgrade"])
    @commands.guild_only()
    @has_permissions(manage_channels=True)
    async def tupgrade(self, ctx):
        """ Ticket command to upgrade a ticket so only admins can view, requires manage channels permissions """
        channel = self.bot.get_channel(ctx.channel.id)
        channel_ids = get_channel_id()

        if ctx.channel.id in channel_ids:
            for role in ctx.guild.roles:
                overwrite = discord.PermissionOverwrite()
                overwrite.update(read_messages=False, read_message_history=False, send_messages=False)
                await channel.set_permissions(role, overwrite=overwrite)

            title = "__Success__"
            description = "Only users with administrator permissions can now view this ticket"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        else:
            description = f"{channel.mention} is not a ticket."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Tickets(bot))
