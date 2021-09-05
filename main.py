# 3rd-Party Packages
from sys import exc_info
from discord import Intents
from discord.ext import commands
from discord.ext.commands import bot
from discord_components import DiscordComponents
from discord_slash import SlashCommand

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

    def __init__(self, command_prefix, case_insensitive, description, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, case_insensitive=case_insensitive, description=description, intents=intents)
        
        self.startup_time = datetime.datetime.now()
        self.bot_settings = None

        self.started = False

        self.checker = None

        self.load_settings()

    # Used to load the settings file
    def load_settings(self):

        # If we don't have a settings file, generate one
        if not os.path.isfile(bot_globals.settings_path):
            with open(bot_globals.settings_path, "w") as data:
                json.dump(bot_globals.default_settings, data, indent=4)

        # Load our settings
        with open(bot_globals.settings_path) as data:
            self.bot_settings = json.load(data)

        # Make sure our settings are up-to-date
        changed = False
        for setting in list(bot_globals.default_settings.keys()):

            # Add a setting if we're missing it
            if setting not in self.bot_settings:
                changed = True
                value = bot_globals.default_settings.get(setting)
                self.bot_settings[setting] = value

        if changed:
            self.save_settings()

    async def update_setting(self, setting_name, variable_to_replace):

        # We typically shouldn't be updating a setting that doesn't already exist
        if setting_name not in self.bot_settings:
            print("Updated setting '{}' that does not exist!".format(setting_name))

        # Update the setting
        self.bot_settings[setting_name] = variable_to_replace

        # Save our settings
        self.save_settings()

    def save_settings(self):

        # Write to the settings file
        with open(bot_globals.settings_path, "w") as data:
            json.dump(self.bot_settings, data, indent=4)

    async def get_formatted_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    # Runs when the bot has readied up
    async def on_ready(self):

        if not self.started:

            # Start up our other services
            await self.startup()

            # Log that our bot is actually running
            game_longhand = bot_globals.game_longhands.get(self.bot_settings.get("game_id", -1))
            print(bot_globals.startup_message.format(header="=" * 52,
                                                     username=self.user.name,
                                                     id=self.user.id,
                                                     timestamp=self.startup_time.strftime("%Y-%m-%d-%H-%M-%S"),
                                                     game_longhand=game_longhand,
                                                     footer="=" * 52))

            # Simulate a file update
            # TODO: Remove this
            await self.spoilers.test_file_update()

        else:

            print("{time} | RECONNECT: Bot reconnected to Discord API".format(time=await self.get_formatted_time()))

    # Preliminary stuff done when starting up the bot
    async def startup(self):

        self.started = True

        # Setup the Discord Components library
        DiscordComponents(self)

        # Update startup time
        await self.update_setting("last_startup", self.startup_time.strftime("%Y-%m-%d %H:%M:%S"))

        # Checker class used for checking url and patcher status
        print("{time} | STARTUP: Loading Patch Checker".format(time=await self.get_formatted_time()))
        self.checker = checker.Checker(self)
        await self.checker.startup()

        # Hub for all our command logic
        print("{time} | STARTUP: Loading Commands Center".format(time=await self.get_formatted_time()))
        self.load_extension("cogs.commands_center")

        # Automatic spoiler system
        print("{time} | STARTUP: Loading Spoilers Center".format(time=await self.get_formatted_time()))
        self.spoilers = spoilers.Spoilers(self)
        await self.spoilers.startup()

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
atmobot = Atmobot(command_prefix=_prefix_callable, case_insensitive=True, description=bot_globals.bot_description, intents=Intents.all())
slash = SlashCommand(atmobot, sync_commands=True)
token = atmobot.bot_settings.get("bot_token", "")
atmobot.run(token)
