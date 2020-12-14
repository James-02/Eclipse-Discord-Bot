""" Errors cog that catches all errors and handles them """
import json
import discord
from discord.ext import commands

CONFIG_FILE = "data/config.json"


class Errors(commands.Cog):
    """ Main Errors class that defines the attributes and methods """

    def __init__(self, bot):
        """ Initialization method to define the class' attributes """
        self.bot = bot
        self.time_format = "%d/%B/%Y %H:%M:%S UTC"
        self.colors = {"red": 0xff5959, "green": 0x00ff40, "pink": 0xff00ff}
        print(f"{self.__class__.__name__} cog loaded.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ Event to catch any errors that are caused when a command is called """
        config = get_config()
        msg = ctx.message.content.replace(config["prefix"], "").lower()

        if msg in get_cmds():
            pass

        elif isinstance(error, commands.errors.CommandNotFound):
            description = f"**Use {config['prefix']}help for the command list.**"
            await ctx.send(embed=return_error(self, ctx, title="__Command Not Found__", error=description))

        elif isinstance(error, commands.errors.CheckFailure):
            description = "**You don't have permission to use this command.**"
            await ctx.send(embed=return_error(self, ctx, title="__Permission Denied__", error=description))

        elif isinstance(error, commands.errors.CommandOnCooldown):
            description = f"**This command is on cool-down for another {int(error.retry_after)}s.**"
            await ctx.send(embed=return_error(self, ctx, error=description))

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(embed=return_error(self, ctx, error=str(error)))

        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(embed=return_error(self, ctx, error=str(error)))

        elif isinstance(error, commands.errors.NoPrivateMessage):
            await ctx.send(embed=return_error(self, ctx, error=str(error)))

        else:
            raise error


def return_error(self, ctx, title="__Error__", error=None):
    """ Function to create and return the embed for the error."""
    timestamp = ctx.message.created_at.strftime(self.time_format)
    embed = discord.Embed(title=title, description=error, color=self.colors.get("red"))
    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
    return embed


def get_config():
    """ Function to get the prefix data """
    try:
        with open(CONFIG_FILE) as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def get_cmds():
    """ Function to get the cmds data """
    try:
        with open("data/custom_cmds.json") as i:
            cmds = json.load(i)
            return cmds["commands"]

    except FileNotFoundError as error:
        print(error)


def setup(bot):
    """ Function to setup this config and add the cog to the main bot """
    bot.add_cog(Errors(bot))
