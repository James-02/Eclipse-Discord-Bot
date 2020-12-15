""" Help cog which defines the help and reload commands """
from discord.ext import commands
import methods


class Help(commands.Cog):
    """ Main Help class to setup attributes and methods to be called on each event """

    def __init__(self, bot):
        """ Class initialization method to define class attributes """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff, "blue": 0x0080c0}
        print(f"{self.__class__.__name__} cog loaded.")

    @commands.command(help="<command/page>\n\nDont't provide any arguments to show the 1st help page.",
                      description="Shows the commands list and their descriptions.")
    async def help(self, ctx, arg=None):
        """ User command to show a list of available commands """
        config = methods.get_config()
        commands_list = f"*Use **{config['prefix']}help <command>** for help with usage.*\n" \
                        f"*Use **{config['prefix']}help 2** to view the second help page.*\n"
        commands_list_2 = f"*Use **{config['prefix']}help <command>** for help with usage.*\n"
        bot_commands = []
        for cog in self.bot.cogs.keys():
            commands_list += f"\n**__{cog}__**\n" if cog in ("Users", "Tickets") else ""
            commands_list_2 += f"\n**__{cog}__**\n" if cog in ("Moderation", "Help") else ""

            if str(cog) != "Admin":
                cog_commands = self.bot.get_cog(cog).get_commands()
                for command in cog_commands:
                    bot_commands.append(command.name)
                    commands_list += f"**{config['prefix']}{command.name}** - *{command.description}*\n" if cog in [
                        "Users", "Tickets"] else ""
                    commands_list_2 += f"**{config['prefix']}{command.name}** - *{command.description}*\n" if cog in [
                        "Moderation", "Help"] else ""

        if arg is None or arg == "1":
            title = "**__Help Page: 1__**"
            description = f"**__Commands:__**\n{commands_list}"
            await ctx.author.send(embed=methods.return_embed(self, ctx, title, description, color="blue"))
            await ctx.send(embed=return_help(self, ctx))

        elif arg == "2":
            title = "**__Help Page: 2__**"
            description = f'**__Commands:__**\n{commands_list_2}'
            await ctx.author.send(embed=methods.return_embed(self, ctx, title, description, color="blue"))
            await ctx.send(embed=return_help(self, ctx))

        elif arg not in bot_commands:
            description = "Invalid command, it could be an admin command."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        else:
            command, aliases, usage = fetch_commands(self, arg)
            title = "**__Usage__**"
            description = f"**{config['prefix']}{command.name}** {usage}\n\nOther Aliases: **{aliases}**"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="blue"))

    @commands.command(help="<command>\n\nDon't include any arguments to show the whole command list.",
                      description="Shows the admin commands list and their descriptions.")
    async def adminhelp(self, ctx, arg=None):
        """ Command to show the commands that require administrator permissions """
        config = methods.get_config()
        commands_list = f"*Use **{config['prefix']}adminhelp <command>** for help with usage.*\n"
        bot_commands = []
        for cog in self.bot.cogs.keys():
            if str(cog) == "Admin":
                commands_list += f"\n**__{cog}__**\n"
                cog_commands = self.bot.get_cog(cog).get_commands()
                for command in cog_commands:
                    bot_commands.append(command.name)
                    commands_list += f"**{config['prefix']}{command.name}** - *{command.description}*\n"

        if arg is None:
            title = "**__Admin Help__**"
            description = f"**__Commands:__**\n{commands_list}"
            await ctx.author.send(embed=methods.return_embed(self, ctx, title, description, color="blue"))
            await ctx.send(embed=return_help(self, ctx))

        elif arg not in bot_commands:
            description = "Invalid command, it may not be an admin command."
            await ctx.send(embed=methods.return_error(self, ctx, error=description))

        else:
            command, aliases, usage = fetch_commands(self, arg)
            title = "**__Usage__**"
            description = f"**{config['prefix']}{command.name}** {usage}\n\nOther Aliases: **{aliases}**"
            await ctx.send(embed=methods.return_embed(self, ctx, title, description, color="blue"))


def return_help(self, ctx):
    """ Function to respond to user in context of their command """
    title = "**__Help__**"
    description = "Sent Help in DM's."
    embed = methods.return_embed(self, ctx, title, description, color="green")
    return embed


def fetch_commands(self, arg):
    """ Function to fetch aliases and usage of a given command """
    for cog in self.bot.cogs.keys():
        cog_commands = self.bot.get_cog(cog).get_commands()
        for command in cog_commands:
            if command.name == arg:
                aliases = ", ".join(command.aliases) if command.aliases != [] else "None"
                usage = "" if command.help == "" else f"*{command.help}*"
                return command, aliases, usage


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Help(bot))
