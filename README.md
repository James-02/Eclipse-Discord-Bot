



# Eclipse Discord Bot
To run the bot:
1. Download python 3.6+ and add to PATH (https://www.python.org/downloads/)
2. Paste your bot token into the config file (https://www.writebots.com/discord-bot-token/)
3. cd to the directory in terminal and run `pip install -r requirements.txt`
4. run `python bot.py` in terminal or run start.bat

- If you need help filling in the config.json or have any troubles, please message Jam#0191 on discord or make a ticket in https://discord.gg/N6xA3JZ

# To Invite The Bot To Your Server
- https://discordpy.readthedocs.io/en/latest/discord.html
- Log into discord developer portal: https://discordapp.com/developers and create a new application
- Go to "Bot" on the side and click "add a bot" name it whatever you want it to be called and add a profile picture.
- Under "Token" you will see click to reveal and copy. You will need to copy and paste that token into the config.json file.
- Go To 0Auth2 on the side, select "bot" in the scopes section and copy the link and paste it into the browser, then select your server and the bot will join.
- To turn the bot online you will still need to put the token into config.json and run the bot, you will need python and the modules installed to run the bot if you are running the bot regularly.

# Requirements (Versions Tested)
python 3.6+
- discord.py==1.5.1
- async-timeout==3.0.1
- aiohttp==3.6.3
- datetime==4.3

If you have any issues please message Jam#0191 on discord.