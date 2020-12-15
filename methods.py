import json
import discord
import sqlite3

CONFIG_FILE = "data/config.json"
BLACKLISTED_FILE = "data/blacklisted.json"
COMMANDS_FILE = "data/custom_cmds.json"
REACTIONS_FILE = "data/reaction_roles.json"
TICKET_FILE = "data/tickets.db"


def get_cmds():
    """ Function to get the custom commands from the json file """
    try:
        with open(COMMANDS_FILE, "r") as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def set_cmds(data):
    """ Function to add a new custom command to the json file """
    try:
        with open(COMMANDS_FILE, "w") as i:
            json.dump(data, i, indent=4, ensure_ascii=False)

    except FileNotFoundError as error:
        print(error)


def get_config():
    """ Function to get the config data """
    try:
        with open(CONFIG_FILE, "r", encoding="UTF-8") as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def set_config(data):
    """ Function to write the config data """
    try:
        with open(CONFIG_FILE, "w") as i:
            json.dump(data, i, indent=4, ensure_ascii=False)

    except FileNotFoundError as error:
        print(error)


def get_blacklisted():
    """ Function to get the blacklisted users list """
    try:
        with open(BLACKLISTED_FILE) as i:
            return json.load(i)

    except FileNotFoundError as error:
        print(error)


def set_blacklisted(data):
    """ Function to append a user to the blacklisted users """
    try:
        with open(BLACKLISTED_FILE, "w") as i:
            json.dump(data, i, indent=4)

    except FileNotFoundError as error:
        print(error)


def get_reaction_roles():
    """ Function to get the reaction-roles file's data """
    try:
        with open(REACTIONS_FILE, "r", encoding="UTF-8") as i:
            reaction_roles = json.load(i)
            return reaction_roles

    except FileNotFoundError as error:
        print(error)


def get_filtered():
    """ Function to get the filter words """
    try:
        with open(CONFIG_FILE, "r") as i:
            filter_data = json.load(i)
            return filter_data["filtered_words"]

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


def send_query(select):
    """ Function to connect and query the tickets database with sqlite3 """
    conn = sqlite3.connect(TICKET_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute(select)
        conn.commit()
        return cursor.fetchall()

    except sqlite3.OperationalError:
        print("Database or table not found.")


def return_error(self, ctx, title="__Error__", error=None):
    """ Function to create and return the embed for the error."""
    if isinstance(ctx, discord.message.Message):
        timestamp = ctx.created_at.strftime(self.time_format)
    else:
        timestamp = ctx.message.created_at.strftime(self.time_format)
    embed = discord.Embed(title=title, description=error, color=self.colors.get("red"))
    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
    return embed


def return_embed(self, ctx, title=None, description=None, color=None, thumbnail=None, image=None):
    """ Function to create and return the embed for the command that calls it."""
    if isinstance(ctx, discord.message.Message):
        timestamp = ctx.created_at.strftime(self.time_format)
    else:
        timestamp = ctx.message.created_at.strftime(self.time_format)
    embed = discord.Embed(title=title, description=description, color=self.colors.get(color))
    embed.set_footer(text=f"{self.bot.user.name} | {timestamp}", icon_url=self.bot.user.avatar_url)
    embed.set_thumbnail(url=thumbnail) if thumbnail is not None else None
    embed.set_image(url=image) if image is not None else None
    return embed
