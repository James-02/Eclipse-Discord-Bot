""" Admin Commands cog that defines all the admin commands """
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import methods


class Admin(commands.Cog):
    """ Admin class is used to create all the admin commands and methods """

    def __init__(self, bot):
        """ Initialization method to define all the attributes required for the class """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff, "blue": 0x0080c0}
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

    @commands.command(help="", description="Reloads the bot's cogs.")
    @has_permissions(administrator=True)
    async def reload(self, ctx):
        """ Admin command to reload all the bot's cogs, updates the files if they have been edited """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        for extension in self.cogs:
            self.bot.unload_extension(extension)
            self.bot.load_extension(extension)

        embed = discord.Embed(title="**__Reload Successful__**", description="All cogs were reloaded.",
                              color=self.colors.get("green"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="<@user>", description="Blacklists a user from using the bot.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def blacklist(self, ctx, member: discord.Member):
        """ Admin command to blacklist a user from using the bot's commands """
        blacklisted = methods.get_blacklisted()
        if member.guild_permissions.administrator:
            description = "Cannot blacklist a user with administrator permissions."
            await ctx.send(methods.return_error(self, ctx, error=description))

        elif f"{member}" not in blacklisted["user"]:
            blacklisted["user"].append(f"{member}")
            methods.set_blacklisted(blacklisted)
            title = "**__Blacklist__**"
            description = f"{member.mention} was blacklisted from using all bot commands."
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        else:
            description = f"{member.mention} is already blacklisted."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="<@user>", description="Removes a player from the bot's blacklist.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def unblacklist(self, ctx, member: discord.Member):
        """ Admin command to unblacklist a user from the bot """
        blacklisted = methods.get_blacklisted()
        if f"{member}" in blacklisted["user"]:
            index = blacklisted["user"].index(f"{member}")
            del blacklisted["user"][index]
            methods.set_blacklisted(blacklisted)
            title = "**__Blacklist__**"
            description = f"{member.mention} was removed from the blacklist."
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        else:
            await ctx.send(embed=methods.return_error(self, ctx, error=f"{member.mention} isn't blacklisted."))

    @commands.command(help="<message>", description="DM's all users in the discord the message.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def messageall(self, ctx, *, message):
        """ Sends the message to all members in the server with the role """
        members = set(ctx.message.guild.members)
        for user in members:
            try:
                await user.send(embed=methods.return_embed(self, ctx, title="**__Announcement__**", description=message,
                                                           color="pink"))
            except discord.errors.Forbidden:
                pass

        title = "**__Success__**"
        description = "Message sent to all users."
        await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<status>", description="Admin command to change the bot's online status.")
    @has_permissions(administrator=True)
    async def status(self, ctx, status=None):
        """ Admin command to change the bot's 'online' status """
        statuses = ["online", "dnd", "idle", "invisible", "offline"]
        if (status is None) or (status not in statuses):
            description = f"Invalid status. Please choose from: {', '.join(statuses)}"
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif status in statuses:
            activity = ctx.guild.get_member(self.bot.user.id).activity
            await self.bot.change_presence(activity=activity, status=status, afk=True)
            title = "__Status Changed__"
            description = f"Online status changed to '{status}'"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))
            config = methods.get_config()
            config["online_status"] = f"{status}"
            methods.set_config(config)

        else:
            description = f"Invalid status. Please choose from: {', '.join(statuses)}"
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="<status>", description="Admin command to change the bot's playing status.")
    @has_permissions(administrator=True)
    async def playing(self, ctx, *, message=None):
        """ Admin command to change the bot's 'playing' status """
        if message is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No status given."))
        else:
            activity = discord.Activity(name=message, type=discord.ActivityType.playing)
            online_status = ctx.guild.get_member(self.bot.user.id).status
            await self.bot.change_presence(status=online_status, activity=activity)

            title = "__Status Changed__"
            description = f"Status changed to: 'Playing {message}'"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            config = methods.get_config()
            config["playing_status"] = f"{message}"
            methods.set_config(config)

    @commands.command(help="<status>", description="Admin command to change the bot's listening status.")
    @has_permissions(administrator=True)
    async def listening(self, ctx, *, message=None):
        """ Admin command to change the bot's 'listening' status """
        if message is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No status given."))
        else:
            activity = discord.Activity(name=message, type=discord.ActivityType.listening)
            online_status = ctx.guild.get_member(self.bot.user.id).status
            await self.bot.change_presence(status=online_status, activity=activity)

            title = "__Status Changed__"
            description = f"Status changed to: 'Playing {message}'"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            config = methods.get_config()
            config["playing_status"] = f"{message}"
            methods.set_config(config)

    @commands.command(help="<status>", description="Admin command to change the bot's watching status.")
    @has_permissions(administrator=True)
    async def watching(self, ctx, *, message=None):
        """ Admin command to change the bot's 'watching' status """
        if message is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No status given."))
        else:
            activity = discord.Activity(name=message, type=discord.ActivityType.watching)
            online_status = ctx.guild.get_member(self.bot.user.id).status
            await self.bot.change_presence(status=online_status, activity=activity)

            title = "__Status Changed__"
            description = f"Status changed to: 'Playing {message}'"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            config = methods.get_config()
            config["playing_status"] = f"{message}"
            methods.set_config(config)

    @commands.command(help="<name> <content>",
                      description="Creates a custom command that when called will send an embed of the content.",
                      aliases=["createcommand", "customcmd", "customcommand", "cmdcreate"])
    @has_permissions(administrator=True)
    async def createcmd(self, ctx, command, *, message=None):
        """ Admin command to add a custom command to the json """
        command = command.lower()
        cmds = methods.get_cmds()
        if command is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No command name given."))
        elif message is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No command content given."))

        elif command not in cmds["commands"]:
            cmds["commands"].update({f"{command}": f"{message}"})
            methods.set_cmds(cmds)
            title = "__Success__"
            description = f"Added the custom command '{command}'"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        else:
            await ctx.send(embed=methods.return_error(self, ctx, error=f"'{command}' is already a custom command."))

    @commands.command(help="<name>", description="Deletes a custom command from the json file.",
                      aliases=["delcommand", "delcustomcmd", "delcustomcommand", "deletecommand", "deletecmd"])
    @has_permissions(administrator=True)
    async def delcmd(self, ctx, command):
        """ Admin command to remove a custom command from the json """
        command = command.lower()
        cmds = methods.get_cmds()
        if command is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No command name given."))

        elif command in cmds["commands"]:
            del cmds["commands"][command]
            methods.set_cmds(cmds)
            title = "__Success__"
            description = f"Deleted the custom command '{command}'"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        else:
            await ctx.send(embed=methods.return_error(self, ctx, error=f"'{command}' could not be found."))

    @commands.command(help="<word>", description="Sets words to be auto-deleted when they are sent in the discord.")
    @has_permissions(administrator=True)
    async def filteradd(self, ctx, word=None):
        """ Admin command to add a word to the filter list """
        if word is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No word given to filter."))
        else:
            config = methods.get_config()
            config["filtered_words"].append(word)
            methods.set_config(config)
            title = "__Filter Added__"
            description = f"'{word}' was added to the filtered list."
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<word>", description="Sets words to be auto-deleted when they are sent in the discord.")
    @has_permissions(administrator=True)
    async def filterremove(self, ctx, word=None):
        """ Admin command to remove a word from the filter list """
        if word is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No word given to remove from the filter list."))
        else:
            config = methods.get_config()
            if word in config["filtered_words"]:
                index = config["filtered_words"].index(word)
                del config["filtered_words"][index]
                methods.set_config(config)
                title = "__Filter Removed__"
                description = f"'{word}' was removed from the filtered list."
                await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

            else:
                description = f"'{word}' is not currently filtered."
                await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(help="", description="Shows the list of words that get auto-deleted.",
                      aliases=["filteredwords", "filterlist"])
    @has_permissions(administrator=True)
    async def filtered(self, ctx):
        """ Admin command to return a list of the filtered words """
        config = methods.get_config()
        words = config["filtered_words"]
        title = "__Filtered Words__"
        description = f"{', '.join(words)}"
        await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<channel> <id>",
                      description="Set's the channel for the features related to send their messages into "
                                  "instead of using the config.json.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def setid(self, ctx, channel=None, channel_id: int = None):
        """ Admin command to set the id of the specified channel required for certain commands """
        channels = ["logging", "giveaways", "suggestions", "welcome"]
        channel_ids = []
        if channel is None or channel not in channels:
            description = f"Invalid channel please choose from: {', '.join(channels)}"
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        elif channel_id is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="Please enter that channel's ID."))
        else:
            try:
                for channels in ctx.guild.text_channels:
                    channel_ids.append(channels.id)

                if channel_id in channel_ids:
                    channel_type = None
                    channel_type = "logging_channel_id" if channel == "logging" else channel_type
                    channel_type = "giveaways_channel_id" if channel == "giveaways" else channel_type
                    channel_type = "welcome_channel_id" if channel == "welcome" else channel_type
                    channel_type = "suggestions_channel_id" if channel == "suggestions" else channel_type

                    config = methods.get_config()
                    config[f"{channel_type}"] = channel_id
                    methods.set_config(config)
                    channel_name = self.bot.get_channel(channel_id)

                    title = "__Success__"
                    description = f"{channel_name.mention} has been set as your `{channel}` channel."
                    await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

                else:
                    description = "That ID does not link to a channel in this server."
                    await ctx.send(embed=methods.return_error(self, ctx, error=description))

            except AttributeError as e:
                print(e)
                description = "An error occurred, make sure the ID and channel are both correct."
                await ctx.send(embed=methods.return_error(self, ctx, error=description))

    @commands.command(
        help="<message>\n\nUse '<member>' to mention the member that joins in the message.\n"
             "e.g: Welcome <member> to the server!",
        description="Set's the welcome message to send when a member joins the server by saving it to the config.json")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def setwelcome(self, ctx, *, message=None):
        """ Admin command to change the welcome message """
        if message is None:
            await ctx.send(embed=methods.return_error(self, ctx, error="No message was given to set."))
        else:
            config = methods.get_config()
            config["welcome_message"] = f"{message}"
            methods.set_config(config)
            title = "__Success__"
            description = f"Successfully changed this guild's welcome message to:\n`{message}`"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

    @commands.command(help="<prefix>", description="Changes the bot's prefix")
    @has_permissions(administrator=True)
    async def setprefix(self, ctx, prefix=None):
        """ Admin command to change the bot's prefix """
        if prefix is not None:
            config = methods.get_config()
            config["prefix"] = f"{prefix}"
            methods.set_config(config)

            title = "**__Prefix Changed__**"
            description = f"Prefix was successfully changed to {prefix}"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="green"))

        else:
            await ctx.send(embed=methods.return_error(self, ctx, error="No prefix was given to set."))


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Admin(bot))
