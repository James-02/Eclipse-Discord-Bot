""" Events cog that catches all events and checks if they are used or not """
import discord
from discord.ext import commands
from discord.utils import get, find
import methods


class Events(commands.Cog):
    """ Main Events class to setup attributes and methods to be called on each event """

    def __init__(self, bot):
        """ Main initializing method called when the class is initialized """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff}
        self.cogs = [
            "cogs.errors",
            "cogs.events",
            "cogs.users",
            "cogs.tickets",
            "cogs.moderation",
            "cogs.help",
            "cogs.admin"
        ]
        print(f"{self.__class__.__name__} cog loaded.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """ Event method called when a user joins the guild """
        timestamp = member.joined_at.strftime(self.time_format)
        config = methods.get_config()
        channel_id = config["welcome_channel_id"]
        message = config["welcome_message"]
        join_role = config["on_join_role"]
        channel = self.bot.get_channel(channel_id)

        if channel is not None:
            for word in message.split(" "):
                message = message.replace(word, member.mention) if word == "<member>" else message

            embed = discord.Embed(title="**__Welcome__**", description=f"{message}", color=self.colors.get("green"))
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await channel.send(embed=embed)

            if join_role != "":
                role = get(member.guild.roles, name=join_role)
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """ Event method called when a reaction is added to any message,
            checks all data to see if it needs to be used """
        if payload.user_id != self.bot.user.id:
            config = methods.get_config()
            ticket_setup_id = config["ticket_setup_id"]
            guild = find(lambda g: g.id == payload.guild_id, self.bot.guilds)

            if payload.message_id == ticket_setup_id and payload.emoji.name == "✅":
                user = self.bot.get_user(payload.user_id)
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                await message.remove_reaction(str(payload.emoji), user)

                select = """ SELECT ticket_id, user_id FROM tickets; """
                data = methods.send_query(select)

                tuples = list(zip(*data))
                tickets = [] if tuples == [] else tuples[0]
                user_ids = [] if tuples == [] else tuples[1]
                ticket_number = int(max(tickets)) if tickets != [] else 1000
                category_check = bool(get(guild.categories, name="tickets"))

                if user.id in user_ids:
                    description = """You already have a ticket open, 
                                    this ticket must be closed before you can open another."""
                    await user.send(embed=methods.return_error(self, message, error=description))

                elif not category_check:
                    description = """There is no category named `tickets` for the channel to be created, 
                                    please create one and set your permissions correctly."""
                    await user.send(embed=methods.return_error(self, message, error=description))

                elif user.id not in user_ids and (ticket_number + 1) not in tickets:
                    ticket_number += 1
                    ticket_channel = f"ticket-{ticket_number}"
                    category = get(guild.categories, name="tickets")

                    ticket = await guild.create_text_channel(ticket_channel, category=category)
                    channel = self.bot.get_channel(ticket.id)
                    overwrite = discord.PermissionOverwrite(send_messages=True, read_messages=True,
                                                            read_message_history=True)
                    await channel.set_permissions(user, overwrite=overwrite)

                    msg = ("**__Ticket Support__**\n\n"
                           "**Please describe your issue in detail and a staff member should assist you shortly.**")
                    await channel.send(f"{msg}\n{user.mention}")
                    title = "**__Ticket Created__**"
                    description = f"**A ticket channel has been created for you in** `{guild.name}`"
                    await user.send(embed=methods.return_embed(self, message, title, description, color="green"))

                    insert = f""" INSERT INTO tickets(ticket_id, user_id, channel_id)
                                VALUES({ticket_number}, {user.id}, {channel.id}) """
                    methods.send_query(insert)

            elif payload.message_id == ticket_setup_id and payload.emoji.name != "✅":
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                user = self.bot.get_user(payload.user_id)
                await message.remove_reaction(str(payload.emoji), user)

            else:
                reactions = (methods.get_reaction_roles())["reaction_messages"]
                for message in reactions:
                    if payload.message_id == message.get("message_id"):
                        roles = message.get("reaction_roles")
                        emojis = message.get("reaction_emojis")

                        if payload.emoji.name in emojis:
                            index = index_emojis(payload, emojis)

                            for role in roles:
                                if roles.index(role) == index:
                                    add_role = get(guild.roles, name=role)
                                    await payload.member.add_roles(add_role)

                        else:
                            channel = self.bot.get_channel(payload.channel_id)
                            message = await channel.fetch_message(payload.message_id)
                            user = self.bot.get_user(payload.user_id)
                            await message.remove_reaction(str(payload.emoji), user)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """ Method event called when a reaction is removed """
        reactions = (methods.get_reaction_roles())["reaction_messages"]
        guild = find(lambda g: g.id == payload.guild_id, self.bot.guilds)
        member = guild.get_member(payload.user_id)
        for message in reactions:
            if payload.message_id == message.get("message_id") and payload.user_id != self.bot.user.id:
                roles = message.get("reaction_roles")
                emojis = message.get("reaction_emojis")

                if payload.emoji.name in emojis:
                    index = index_emojis(payload, emojis)

                    for role in roles:
                        if roles.index(role) == index:
                            remove_role = get(guild.roles, name=role)
                            await member.remove_roles(remove_role)

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Method called when a message is received in a guild, has multiple uses, mainly for cleanup and anti-spam """
        if message.guild is not None:
            msgs = message.content.split(" ")
            config = methods.get_config()
            if not message.author.guild_permissions.administrator:
                for word in msgs:
                    if word in methods.get_filtered():
                        await message.delete()

                if ('https://discord.gg/' in message.content) or ('https://discord.com/invite/' in message.content):
                    await message.delete()

                if len(message.mentions) >= 4:
                    await message.delete()
                    role = config["muted_role"]
                    if role != "":
                        try:
                            await message.author.add_roles(get(message.author.guild.roles, name=role))

                        except AttributeError:
                            print(f"Error while trying to add '{role}' role to user, role does not exist in the guild.")

            if f"<@!{self.bot.user.id}>" == message.content:
                await message.channel.send(f"For help type: **{config['prefix']}help**")

            if message.content.startswith(config["prefix"]):
                cmds = methods.get_cmds()
                if config['prefix'] in message.content:
                    msg = message.content.replace(f"{config['prefix']}", "")

                else:
                    msg = message.content

                msg = (msg.lower().split(" "))[0]
                bot_commands = []
                for cog in self.bot.cogs.keys():
                    for command in self.bot.get_cog(cog).get_commands():
                        bot_commands.append(command.name)

                channel_id = config["logging_channel_id"]
                channel = self.bot.get_channel(channel_id)
                if msg in cmds:
                    title = f"**__{msg.capitalize()}__**"
                    description = f"{cmds.get(msg)}"
                    await message.channel.send(embed=methods.return_embed(self, message, title, description,
                                                                          color="green"))

                elif msg in bot_commands and channel_id is not None:
                    embed = methods.return_embed(self, message, title="__Logged Command__", color="green")
                    embed.add_field(name="**User**", value=message.author.mention)
                    embed.add_field(name="**Command**", value=message.content)
                    await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """ Cleanup method called when a channel is deleted to check if it is a ticket and remove any ticket data """
        select = """ SELECT channel_id FROM tickets; """
        data = methods.send_query(select)
        tuples = list(zip(*data))
        channel_ids = [] if tuples == [] else tuples[0]

        if channel.id in channel_ids:
            delete = f""" DELETE FROM tickets WHERE channel_id = {channel.id}; """
            methods.send_query(delete)


def index_emojis(payload, emojis):
    """ Function to fetch the index of an emoji """
    for idx, emoji in enumerate(emojis):
        if ":" in emoji:
            emoji_final = (emoji.split(":"))[1]
            emojis[idx] = emoji_final

    for emoji in emojis:
        if payload.emoji.name == emoji:
            return emojis.index(emoji)


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Events(bot))
