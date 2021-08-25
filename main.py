# 3rd-Party Packages
from discord import Intents, Embed, Color
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

# Local packages
import checker
import bot_globals

# Built-in packages
import datetime
import json
import os

class Atmobot(commands.Bot):

    def __init__(self, command_prefix, description, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, description=description, intents=intents)
        
        self.startup_time = datetime.datetime.now()
        self.bot_settings = None

        self.checker = None

    # Preliminary stuff done when starting up the bot
    def startup(self):

        # Load up our settings
        self.load_settings()

        # Checker class used for checking url and patcher status
        self.checker = checker.Checker(self)
        self.checker.startup()

        # Hub for all our command logic
        self.load_extension("cogs.command_center")

        # Run the bot
        token = self.bot_settings.get("bot_token", "")
        self.run(token)

    # Used to load the settings file
    def load_settings(self):

        # If we don't have a prior settings.json, generate one
        if not os.path.isfile("settings.json"):
            with open("settings.json", "w") as data:
                data.write(bot_globals.default_settings)
                data.close()

        # Load our settings
        with open("settings.json") as data:
            self.bot_settings = json.load(data)

    async def on_ready(self):

        # Setup the Discord Components library
        DiscordComponents(self)

        # Proof that our bot is actually running
        print("----------\nBot logged in as {} with user ID of {}\n----------".format(self.user.name, self.user.id))

intents = Intents.default()
intents.members = True

def _prefix_callable(bot, msg):
    prefixes = []
    bot_id = bot.user.id
    mention = (f"<@!{bot_id}> ", f"<@{bot_id}> ")
    prefixes.extend(mention)
    if len(prefixes) < 1:
        # if we're *still* empty, default to ">"
        prefixes.append(">")
    return prefixes

# Run the bot
atmobot = Atmobot(command_prefix=_prefix_callable, description=bot_globals.bot_description, intents=intents)
atmobot.startup()
