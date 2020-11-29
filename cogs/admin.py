""" Admin Commands cog that defines all the admin commands """
import json
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

CONFIG_FILE = "data/config.json"
BLACKLISTED_FILE = "data/blacklisted.json"


class Admin(commands.Cog):
    """ Admin class is used to create all the admin commands and methods """

    def __init__(self, bot):
        """ Initialization method to define all the attributes required for the class """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.data = get_config()
        self.blacklisted = get_blacklisted()
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
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if member.guild_permissions.administrator:
            embed = discord.Embed(title="**__Error__**",
                                  description="Cannot blacklist a user with administrator permissions.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif f"{member}" not in self.blacklisted["user"]:
            self.blacklisted["user"].append(f"{member}")
            with open(BLACKLISTED_FILE, "w") as i:
                json.dump(self.blacklisted, i, indent=4)

            embed = discord.Embed(title="**__Blacklist__**",
                                  description=f"{member.mention} was blacklisted from using all bot commands.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="**__Error__**", description=f"{member.mention} is already blacklisted.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<@user>", description="Removes a player from the bot's blacklist.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def unblacklist(self, ctx, member: discord.Member):
        """ Admin command to unblacklist a user from the bot """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if f"{member}" in self.blacklisted["user"]:
            index = self.blacklisted["user"].index(f"{member}")
            del self.blacklisted["user"][index]
            with open(BLACKLISTED_FILE, "w") as i:
                json.dump(self.blacklisted, i, indent=4)

            embed = discord.Embed(title="**__Blacklist__**",
                                  description=f"{member.mention} was removed from the blacklist.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="**__Error__**", description=f"{member.mention} isn't blacklisted.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<message>", description="DM's all users in the discord the message.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def messageall(self, ctx, *, message):
        """ Sends the message to all members in the server with the role """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        members = set(ctx.message.guild.members)
        for user in members:
            try:
                embed = discord.Embed(title="**__Announcement__**", description=message, color=self.colors.get("pink"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await user.send(embed=embed)
            except:
                pass

            embed = discord.Embed(title="**__Success__**", description="Message sent to all users.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<status>", description="Admin command to change the bot's online status.")
    @has_permissions(administrator=True)
    async def status(self, ctx, status=None):
        """ Admin command to change the bot's 'online' status """
        statuses = ["online", "dnd", "idle", "invisible", "offline"]
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if (status is None) or (status not in statuses):
            embed = discord.Embed(title="__Error__",
                                  description=f"Invalid status. Please choose from: {', '.join(statuses)}",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif status in statuses:
            activity = ctx.guild.get_member(self.bot.user.id).activity
            await self.bot.change_presence(activity=activity, status=status, afk=True)
            embed = discord.Embed(title="__Status Changed__", description=f"Online status changed to '{status}'",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

            self.data["online_status"] = f"{status}"
            with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                json.dump(self.data, i, indent=4, ensure_ascii=False)

        else:
            embed = discord.Embed(title="__Error__",
                                  description=f"Invalid status. Please choose from: {', '.join(statuses)}",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<status>", description="Admin command to change the bot's playing status.")
    @has_permissions(administrator=True)
    async def playing(self, ctx, *, message=None):
        """ Admin command to change the bot's 'playing' status """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if message is None:
            embed = discord.Embed(title="__Error__", description="No status given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            activity = discord.Activity(name=message, type=discord.ActivityType.playing)
            online_status = ctx.guild.get_member(self.bot.user.id).status
            await self.bot.change_presence(status=online_status, activity=activity)

            embed = discord.Embed(title="__Status Changed__", description=f"Status changed to: 'Playing {message}'",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

            self.data["playing_status"] = f"{message}"
            with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                json.dump(self.data, i, indent=4, ensure_ascii=False)

    @commands.command(help="<status>", description="Admin command to change the bot's listening status.")
    @has_permissions(administrator=True)
    async def listening(self, ctx, *, message=None):
        """ Admin command to change the bot's 'listening' status """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if message is None:
            embed = discord.Embed(title="__Error__", description="No status given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            activity = discord.Activity(name=message, type=discord.ActivityType.listening)
            online_status = ctx.guild.get_member(self.bot.user.id).status
            await self.bot.change_presence(status=online_status, activity=activity)

            embed = discord.Embed(title="__Status Changed__",
                                  description=f"Status changed to: 'Listening to {message}'",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

            self.data["playing_status"] = f"{message}"
            with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                json.dump(self.data, i, indent=4, ensure_ascii=False)

    @commands.command(help="<status>", description="Admin command to change the bot's watching status.")
    @has_permissions(administrator=True)
    async def watching(self, ctx, *, message=None):
        """ Admin command to change the bot's 'watching' status """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if message is None:
            embed = discord.Embed(title="__Error__", description="No status given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            activity = discord.Activity(name=message, type=discord.ActivityType.watching)
            online_status = ctx.guild.get_member(self.bot.user.id).status
            await self.bot.change_presence(status=online_status, activity=activity)

            embed = discord.Embed(title="__Status Changed__", description=f"Status changed to: 'Watching {message}'",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

            self.data["playing_status"] = f"{message}"
            with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                json.dump(self.data, i, indent=4, ensure_ascii=False)

    @commands.command(help="<name> <content>",
                      description="Creates a custom command that when called will send an embed of the content.",
                      aliases=["createcommand", "customcmd", "customcommand", "cmdcreate"])
    @has_permissions(administrator=True)
    async def createcmd(self, ctx, command, *, message=None):
        """ Admin command to add a custom command to the json """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        command = command.lower()
        cmds = get_cmds()
        if command is None:
            embed = discord.Embed(title="__Error__", description="No command name given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif message is None:
            embed = discord.Embed(title="__Error__", description="No command content given.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif command not in cmds["commands"]:
            try:
                cmds["commands"].update({f"{command}": f"{message}"})
                with open("data/custom_cmds.json", "w") as i:
                    json.dump(cmds, i, indent=4)

                embed = discord.Embed(title="__Success__", description=f"Added the custom command '{command}'",
                                      color=self.colors.get("green"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

            except FileNotFoundError as error:
                print(error)

        else:
            embed = discord.Embed(title="__Error__", description=f"'{command}' is already a custom command.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<name>", description="Deletes a custom command from the json file.",
                      aliases=["delcommand", "delcustomcmd", "delcustomcommand", "deletecommand", "deletecmd"])
    @has_permissions(administrator=True)
    async def delcmd(self, ctx, command):
        """ Admin command to remove a custom command from the json """
        command = command.lower()
        timestamp = ctx.message.created_at.strftime(self.time_format)
        cmds = get_cmds()
        if command is None:
            embed = discord.Embed(title="__Error__", description="No command name given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif command in cmds["commands"]:
            try:
                del cmds["commands"][command]
                with open("data/custom_cmds.json", "w") as i:
                    json.dump(cmds, i, indent=4)

                embed = discord.Embed(title="__Success__", description=f"Deleted the custom command '{command}'",
                                      color=self.colors.get("green"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

            except FileNotFoundError as error:
                print(error)

        else:
            embed = discord.Embed(title="__Error__", description=f"'{command}' could not be found.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<word>", description="Sets words to be auto-deleted when they are sent in the discord.")
    @has_permissions(administrator=True)
    async def filteradd(self, ctx, word=None):
        """ Admin command to add a word to the filter list """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if word is None:
            embed = discord.Embed(title="__Error__", description="No word given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            self.data["filtered_words"].append(word)
            with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                json.dump(self.data, i, indent=4)

            embed = discord.Embed(title="__Filter Added__", description=f"'{word}' was added to the filtered list.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="<word>", description="Sets words to be auto-deleted when they are sent in the discord.")
    @has_permissions(administrator=True)
    async def filterremove(self, ctx, word=None):
        """ Admin command to remove a word from the filter list """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if word is None:
            embed = discord.Embed(title="__Error__", description="No word given.", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            index = self.data["filtered_words"].index(word)
            del self.data["filtered_words"][index]
            with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                json.dump(self.data, i, indent=4)

            embed = discord.Embed(title="__Filter Removed__",
                                  description=f"'{word}' was removed from the filtered list.",
                                  color=self.colors.get("green"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(help="", description="Shows the list of words that get auto-deleted.",
                      aliases=["filteredwords", "filterlist"])
    @has_permissions(administrator=True)
    async def filtered(self, ctx):
        """ Admin command to return a list of the filtered words """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        config = get_config()
        words = config["filtered_words"]
        embed = discord.Embed(title="__Filtered Words__", description=f"{', '.join(words)}",
                              color=self.colors.get("green"))
        embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="<channel> <id>",
                      description="Set's the channel for the features related to send their messages into instead of using the config.json.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def setid(self, ctx, channel=None, channel_id=None):
        """ Admin command to set the id of the specified channel required for certain commands """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        channels = ["logging", "giveaways", "suggestions", "welcome"]
        channel_ids = []
        if channel is None or channel not in channels:
            embed = discord.Embed(title="__Error__",
                                  description=f"Invalid channel please choose from: {', '.join(channels)}",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif channel_id is None:
            embed = discord.Embed(title="__Error__", description="Please enter that channel's ID.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            try:
                int(channel_id)
                for channels in ctx.guild.text_channels:
                    channel_ids.append(channels.id)

                if channel_id in channel_ids:
                    channel_type = None
                    channel_type = "logging_channel_id" if channel == "logging" else channel_type
                    channel_type = "giveaways_channel_id" if channel == "giveaways" else channel_type
                    channel_type = "welcome_channel_id" if channel == "welcome" else channel_type
                    channel_type = "suggestions_channel_id" if channel == "suggestions" else channel_type

                    self.data[f"{channel_type}"] = channel_id
                    with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                        json.dump(self.data, i, indent=4, ensure_ascii=False)

                    channel_name = self.bot.get_channel(channel_id)

                    embed = discord.Embed(title="__Success__",
                                          description=f"{channel_name.mention} has been set as your `{channel}` channel.",
                                          color=self.colors.get("green"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)

                else:
                    embed = discord.Embed(title="__Error__",
                                          description="That ID does not link to a channel in this server.",
                                          color=self.colors.get("red"))
                    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                    await ctx.send(embed=embed)

            except:
                embed = discord.Embed(title="__Error__",
                                      description="An error occured, make sure the ID and channel are both correct.",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(
        help="<message>\n\nUse '<member>' to mention the member that joins in the message.\ne.g: Welcome <member> to the server!",
        description="Set's the welcome message to send when a member joins the server by saving it into the config.json.")
    @commands.guild_only()
    @has_permissions(administrator=True)
    async def setwelcome(self, ctx, *, message=None):
        """ Admin command to change the welcome message """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if message is None:
            embed = discord.Embed(title="__Error__", description="No message was given to set.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            try:
                self.data["welcome_message"] = f"{message}"
                with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                    json.dump(self.data, i, indent=4, ensure_ascii=False)

                embed = discord.Embed(title="__Success__",
                                      description=f"Successfully changed this guild's welcome message to:\n`{message}`",
                                      color=self.colors.get("green"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

            except FileNotFoundError as error:
                embed = discord.Embed(title="__Error__",
                                      description="An error occured, please check the console. (File Not Found)",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)
                print(error)

            except IOError as error:
                embed = discord.Embed(title="__Error__",
                                      description="An error occured, please check the console. (Writing to file error)",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)
                print(error)

    @commands.command(help="<prefix>", description="Changes the bot's prefix")
    @has_permissions(administrator=True)
    async def setprefix(self, ctx, prefix=None):
        """ Admin command to change the bot's prefix """
        timestamp = ctx.message.created_at.strftime(self.time_format)
        if prefix is not None:
            try:
                self.data["prefix"] = f"{prefix}"
                with open(CONFIG_FILE, "w", encoding="UTF-8") as i:
                    json.dump(self.data, i, indent=4)

                embed = discord.Embed(title="**__Prefix Changed__**",
                                      description=f"Prefix was successfully changed to {prefix}",
                                      color=self.colors.get("green"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

            except IOError:
                embed = discord.Embed(title="**__Error__**", description="An error occured while changing prefix.",
                                      color=self.colors.get("red"))
                embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="**__Error__**", description="No prefix was given.",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)


def get_cmds():
    """ Function to get the custom commands from the json file """
    try:
        with open("data/custom_cmds.json", "r") as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def get_config():
    """ Function to get the config data """
    try:
        with open(CONFIG_FILE, "r", encoding="UTF-8") as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def get_blacklisted():
    """ Function to get the blacklisted users list """
    try:
        with open(BLACKLISTED_FILE) as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Admin(bot))
