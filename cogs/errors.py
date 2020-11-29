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
        timestamp = ctx.message.created_at.strftime(self.time_format)
        config = get_config()
        msg = ctx.message.content.replace(config["prefix"], "").lower()

        if msg in get_cmds():
            pass

        elif isinstance(error, commands.errors.CommandNotFound):
            embed = discord.Embed(title="**__Command Not Found__**",
                                  description=f"**Use {config['prefix']}help for the command list.**",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.CheckFailure):
            embed = discord.Embed(title="**__Permission Denied__**",
                                  description="**You don't have permission to use this command.**",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="**__Permission Denied__**",
                                  description=f"**This command is on cooldown for another {int(error.retry_after)}s.**",
                                  color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            embed = discord.Embed(title="**__Error__**", description=f"**{error}**", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(title="**__Error__**", description=f"**{error}**", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.NoPrivateMessage):
            embed = discord.Embed(title="**__Error__**", description=f"**{error}**", color=self.colors.get("red"))
            embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)

        else:
            raise error


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
