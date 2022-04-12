# 3rd-Party Packages
from discord import Intents
from discord.ext import commands
from discord_components import DiscordComponents
from discord_slash import SlashCommand

# Local packages
import bot_globals
import checker
import spoilers
import utils

# Built-in packages
import asyncio
import datetime
import json
import os
import sys

# Atmobot
class Atmobot(commands.Bot):

    def __init__(self, command_prefix, case_insensitive, description, intents, help_command):
        commands.Bot.__init__(self, command_prefix=command_prefix, case_insensitive=case_insensitive, description=description, intents=intents, help_command=help_command)
        
        self.startup_time = datetime.datetime.now()
        self.started = False
        self.checker = None

        self.load_settings()

        # We HAVE to load our Cogs here, or else it won't work properly
        SlashCommand(self, sync_commands=True)

        # Public commands
        print("{time} | STARTUP: Loading Public Commands".format(time=utils.get_formatted_time()))
        self.load_extension("cogs.public_commands")

        # Private commands
        print("{time} | STARTUP: Loading Private Commands".format(time=utils.get_formatted_time()))
        self.load_extension("cogs.private_commands")

        # Deprecated commands
        if settings.get("deprecated_commands", False):
            print("{time} | STARTUP: Loading Deprecated Commands".format(time=utils.get_formatted_time()))
            self.load_extension("cogs.deprecated_commands")

    # Used to load the settings file
    def load_settings(self):

        # If we don't have a settings file, generate one
        if not os.path.isfile(bot_globals.settings_path):
            with open(bot_globals.settings_path, "w") as data:
                json.dump(bot_globals.default_settings, data, indent=4)

        # Load our settings
        with open(bot_globals.settings_path) as data:
            __builtins__.settings = json.load(data)

        # Make sure our settings are up-to-date
        changed = False
        for setting in list(bot_globals.default_settings.keys()):

            # Add a setting if we're missing it
            if setting not in settings:
                changed = True
                value = bot_globals.default_settings.get(setting)
                settings[setting] = value

        if changed:
            self.save_settings()

    async def update_setting(self, setting_name, variable_to_replace):

        # We typically shouldn't be updating a setting that doesn't already exist
        if setting_name not in settings:
            print("Updated setting '{}' that does not exist!".format(setting_name))

        # Update the setting
        settings[setting_name] = variable_to_replace

        # Save our settings
        self.save_settings()

    def save_settings(self):

        # Write to the settings file
        with open(bot_globals.settings_path, "w") as data:
            json.dump(settings, data, indent=4)

    async def get_formatted_time(self):
        return utils.get_formatted_time()

    # Runs when the bot has readied up
    async def on_ready(self):

        if not self.started:

            # Start up our other services
            await self.startup()

            # Log that our bot is actually running
            game_longhand = bot_globals.game_longhands.get(settings.get("game_id", -1))
            print(bot_globals.startup_message.format(header="=" * 52,
                                                     username=self.user.name,
                                                     id=self.user.id,
                                                     timestamp=self.startup_time.strftime("%Y-%m-%d-%H-%M-%S"),
                                                     game_longhand=game_longhand,
                                                     footer="=" * 52))

        else:

            print("{time} | RECONNECT: Bot reconnected to Discord API".format(time=await self.get_formatted_time()))

    # Preliminary stuff done when starting up the bot
    async def startup(self):

        self.started = True

        # Setup the Discord Components library
        DiscordComponents(self)

        # Wait for button presses
        asyncio.ensure_future(self.wait_for_button_press())

        # Update startup time
        await self.update_setting("last_startup", self.startup_time.strftime("%Y-%m-%d %H:%M:%S"))

        # Checker class used for checking url and patcher status
        print("{time} | STARTUP: Loading Patch Checker".format(time=await self.get_formatted_time()))
        self.checker = checker.Checker(self)
        await self.checker.startup()

        # Automatic spoiler system
        print("{time} | STARTUP: Loading Spoilers Center".format(time=await self.get_formatted_time()))
        self.spoilers = spoilers.Spoilers(self)
        await self.spoilers.startup()

    async def wait_for_button_press(self):

        # Wait for the button press
        response = await self.wait_for("button_click")

        # Handle buttons differently
        button_name = response.component.label
        
        # Test Realm notification role toggle
        if button_name == "Toggle Role":

            author = response.guild.get_member(response.author.id)

            role_ids = (role.id for role in author.roles)
            role_id = 886396512018501733
            guild = response.guild
            role = guild.get_role(role_id)

            # We already have this role, so we want to remove it
            if role_id in role_ids:
                await author.remove_roles(role)
                await response.respond(content="Removed Test Realm Notifications Role.")

            # We actually don't have the role, so add it
            else:
                await author.add_roles(role)
                await response.respond(content="Added Test Realm Notifications Role.")

        # Approve proposed tweet
        elif button_name == "Approve Tweet":
            return

        # Deny proposed tweet
        elif button_name == "Deny Tweet":
            return

        await self.wait_for_button_press()

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

log_name = "logs/atmobot-log-{timestamp}.log".format(timestamp=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
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
atmobot = Atmobot(command_prefix=_prefix_callable, case_insensitive=True, description=bot_globals.bot_description, intents=Intents.all(), help_command=None)
token = settings.get("bot_token", "")
atmobot.run(token)
