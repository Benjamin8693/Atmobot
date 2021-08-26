# 3rd-Party Packages
from sys import exc_info
from discord import Intents, Embed, Color, file
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

# Local packages
import bot_globals
import checker
import spoilers

# Built-in packages
import asyncio
import datetime
import json
import os
import sys

# Atmobot
class Atmobot(commands.Bot):

    def __init__(self, command_prefix, description, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, description=description, intents=intents)
        
        self.startup_time = datetime.datetime.now()
        self.bot_settings = None

        self.checker = None

    # Preliminary stuff done when starting up the bot
    def startup(self):

        # Load our settings and update startup time
        self.load_settings()
        self.update_setting("last_startup", self.startup_time.strftime("%Y-%m-%d %H:%M:%S"))

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

    def update_setting(self, setting_name, variable_to_replace):

        # We typically shouldn't be updating a setting that doesn't already exist
        if setting_name not in self.bot_settings:
            print("Updated setting '{}' that does not exist!".format(setting_name))

        # Update the setting
        self.bot_settings[setting_name] = variable_to_replace

        # Write it to the settings file
        with open("settings.json", "w") as data:
            json.dump(self.bot_settings, data, indent=4)

    async def on_ready(self):

        # Setup the Discord Components library
        DiscordComponents(self)

        # Proof that our bot is actually running
        game_longhand = bot_globals.game_longhands.get(self.bot_settings.get("game", -1))
        service_name = bot_globals.service_names.get(self.bot_settings.get("service", -1))
        print(bot_globals.startup_message.format(header="=" * 52,
                                                 username=self.user.name,
                                                 id=self.user.id,
                                                 timestamp=self.startup_time.strftime("%Y-%m-%d-%H-%M-%S"),
                                                 game_longhand=game_longhand,
                                                 service=service_name.capitalize(),
                                                 service_suffix=bot_globals.service_suffix,
                                                 footer="=" * 52))

        # Testing
        self.spoilers = spoilers.Spoilers(self)
        #await self.spoilers.unpack()

# Setup logging
if not os.path.exists("logs/"):
    os.mkdir("logs/")

class LogOutput:

    def __init__(self, orig, log):
        self.orig = orig
        self.log = log

    def write(self, out):
        if isinstance(out, str):
            out_bytes = out.encode('utf-8', 'ignore')
        else:
            out_bytes = out
            out = out.decode('utf-8', 'ignore')
        self.log.write(out_bytes)
        self.log.flush()
        if self.console:
            self.orig.write(out)
            self.orig.flush()

    def flush(self):
        self.log.flush()
        self.orig.flush()

log_name = "logs/atmobot-log-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
log = open(log_name, "ab")
logOut = LogOutput(sys.__stdout__, log)
logErr = LogOutput(sys.__stderr__, log)
sys.stdout = logOut
sys.stderr = logErr
sys.stdout.console = True
sys.stderr.console = True

# What prefix are we going to use?
def _prefix_callable(bot, msg):
    
    # Prefixes we can use for the bot
    prefixes = []

    # Right now we only care if we're mentioned
    bot_id = bot.user.id
    mention = (f"<@!{bot_id}> ", f"<@{bot_id}> ")
    prefixes.extend(mention)

    # If we don't have any other prefixes to use, default to ">"
    if len(prefixes) < 1:
        prefixes.append(">")
    
    # Return available prefixes
    return prefixes

# Run the bot
intents = Intents.default()
intents.members = True
atmobot = Atmobot(command_prefix=_prefix_callable, description=bot_globals.bot_description, intents=intents)
atmobot.startup()
