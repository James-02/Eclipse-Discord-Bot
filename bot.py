""" Main bot file, run this file to start the bot """
import json

import discord
from discord.ext import commands


def get_config():
    """ Loads the config data. """
    try:
        with open(CONFIG_FILE) as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def get_prefix(_bot, _message):
    """ Function to get the prefix for dynamic updating """
    try:
        with open(CONFIG_FILE) as i:
            prefix_data = json.load(i)
            return prefix_data["prefix"]

    except FileNotFoundError as error:
        print(error)


bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, reconnect=True, check="blacklist_check")
bot.remove_command("help")
CONFIG_FILE = "data/config.json"
BLACKLISTED_FILE = "data/blacklisted.json"
data = get_config()

cogs = [
    "cogs.events",
    "cogs.errors",
    "cogs.users",
    "cogs.tickets",
    "cogs.moderation",
    "cogs.help",
    "cogs.admin"
]


@bot.event
async def on_ready():
    """ Event that is called once bot is up and running, changes status and activity """
    config = get_config()
    prefix = config["prefix"]
    status = config["playing_status"]
    online_status = config["online_status"]

    if status != "" and online_status != "":
        activity = discord.Activity(name=status, type=discord.ActivityType.playing)
        await bot.change_presence(status=discord.Status(f"{online_status}"), activity=activity, afk=True)

    elif status != "" and online_status == "":
        activity = discord.Activity(name=status, type=discord.ActivityType.playing)
        await bot.change_presence(activity=activity, afk=True)

    elif online_status != "" and status == "":
        await bot.change_presence(status=discord.Status(f"{online_status}"), afk=True)

    print(f"Logged in as {bot.user.name}, type {prefix}help for more information.")


@bot.check
async def blacklist_check(ctx):
    """ Check that bot uses every time it is called to see if a user is blacklisted """
    with open(BLACKLISTED_FILE) as blacklisted_file:
        blacklisted = json.load(blacklisted_file)
    return f"{ctx.message.author}" not in blacklisted["user"]


if __name__ == '__main__':
    for extension in cogs:
        bot.load_extension(extension)

bot.run(data["token"])
