# 3rd-Party Packages
from discord import Intents
from discord.ext import commands

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

class Atmobot(commands.Bot):

    def __init__(self, command_prefix, case_insensitive, description, intents, help_command, startup_time):
        commands.Bot.__init__(self, command_prefix=command_prefix, case_insensitive=case_insensitive, description=description, intents=intents, help_command=help_command)
        
        self.startup_time = startup_time

        self.load_settings()

        self.started = False

        self.guild_id = settings.get("guild_id", 0)
        self.guild = None

        self.reduced_cooldown_channels = []
        self.reduced_cooldown_roles = []

        # Create a builtin to reference our bot object at any time
        __builtins__.bot = self

        # Public commands
        print("{time} | STARTUP: Loading Public Commands".format(time=utils.get_formatted_time()))
        self.load_extension("cogs.public_commands")

        # Private commands
        print("{time} | STARTUP: Loading Private Commands".format(time=utils.get_formatted_time()))
        self.load_extension("cogs.private_commands")

        # Music commands
        print("{time} | STARTUP: Loading Music Commands".format(time=utils.get_formatted_time()))
        self.load_extension("cogs.music_commands")

        # Deprecated commands
        if settings.get("deprecated_commands", False):
            print("{time} | STARTUP: Loading Deprecated Commands".format(time=utils.get_formatted_time()))
            self.load_extension("cogs.deprecated_commands")

    # Used to load the settings file
    def load_settings(self):

        # If we don't have a settings file, generate one
        if not os.path.isfile(bot_globals.settings_path):
            with open(bot_globals.settings_path, "w") as data:

                # Create a dictonary with our defaults
                default_settings = {}
                for setting in bot_globals.bot_settings:
                    setting_info = bot_globals.bot_settings.get(setting)
                    setting_value = setting_info[bot_globals.BOT_SETTINGS_DEFAULT]
                    default_settings[setting] = setting_value
                
                # Save it to json
                json.dump(default_settings, data, indent=4)

        # Load our settings
        with open(bot_globals.settings_path) as data:
            __builtins__.settings = json.load(data)

        # Make sure our settings are up-to-date
        updated = False
        for setting in bot_globals.bot_settings:

            # Grab setting info
            setting_info = bot_globals.bot_settings.get(setting)

            # Add a setting if we're missing it
            if setting not in settings:
                updated = True
                setting_value = setting_info[bot_globals.BOT_SETTINGS_DEFAULT]
                settings[setting] = setting_value

            # TODO: Add setting versioning

        # Our settings have been updated, let's be sure to save them
        if updated:
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
            print(bot_globals.startup_message.format(header="=" * 52,
                                                     username=self.user.name,
                                                     id=self.user.id,
                                                     timestamp=self.startup_time.strftime("%Y-%m-%d-%H-%M-%S"),
                                                     footer="=" * 52))

        else:

            print("{time} | RECONNECT: Bot reconnected to Discord API".format(time=await utils.get_formatted_time()))

    # Preliminary stuff done when starting up the bot
    async def startup(self):

        self.started = True

        # Load the guild we'll be serving
        self.guild = self.get_guild(self.guild_id)

        # Load channel and role info for cooldowns
        reduced_cooldown_channel_ids = settings.get("reduced_cooldown_channels", [])
        for channel_id in reduced_cooldown_channel_ids:
            channel = self.get_channel(channel_id)
            self.reduced_cooldown_channels.append(channel)
        reduced_cooldown_role_ids = settings.get("reduced_cooldown_roles", [])
        for role_id in reduced_cooldown_role_ids:
            role = self.guild.get_role(role_id)
            self.reduced_cooldown_roles.append(role)

        # Wait for button presses
        asyncio.ensure_future(self.wait_for_button_press())

        # Update startup time
        #await self.update_setting("last_startup", self.startup_time.strftime("%Y-%m-%d %H:%M:%S"))

        # Checker class used for checking url and patcher status
        print("{time} | STARTUP: Loading Patch Checker".format(time=await self.get_formatted_time()))
        #self.checker = checker.Checker(self)
        #await self.checker.startup()

        # Automatic spoiler system
        print("{time} | STARTUP: Loading Spoilers Center".format(time=await self.get_formatted_time()))
        self.spoilers = spoilers.Spoilers(self)
        await self.spoilers.startup()

        # Set up Discord logging
        sys.stdout.bot = self
        sys.stdout.load_log_channel()
        sys.stderr.bot = self
        sys.stderr.load_log_channel()

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

    # Used to output log information to a channel on Discord
    def handle_log(self, output, log_channel):

        # Send log output to our channel if it exists
        if log_channel:
            self.loop.create_task(log_channel.send(output))

# Log class 
class LogOutput:

    def __init__(self, orig, log):

        self.orig = orig
        self.log = log

        self.bot = None
        self.log_channel = None

    def load_log_channel(self):

        # Grab the ID for our logging channel
        log_channel_id = settings.get("log_channel")

        # We can only write our logs to Discord if we have a channel ID to hook up to
        if log_channel_id:

            # Grab the channel from it's ID0
            self.log_channel = self.bot.get_channel(log_channel_id)

    def write(self, out):

        # Preserve the original output for Discord
        discord_out = out

        # Strip the output for log and console
        chars_to_replace = ("*",)
        for char_to_replace in chars_to_replace:
            out = out.replace(char_to_replace, "")

        # Encode our string to utf8
        if isinstance(out, str):
            out_bytes = out.encode('utf-8', 'ignore')

        # Get a decoded version of our string
        else:
            out_bytes = out
            out = out.decode('utf-8', 'ignore')

        # Write to log
        self.log.write(out_bytes)
        self.log.flush()

        # Write to console
        if self.console:
            self.orig.write(out)
            self.orig.flush()

        # We want to try and print out our log via Discord as well
        if self.bot and out and out != "\n":
            try:
                self.bot.handle_log(discord_out, self.log_channel)
            except:
                pass

    def flush(self):
        self.log.flush()
        self.orig.flush()

# Create logging directory
if not os.path.exists("logs/"):
    os.mkdir("logs/")

# Create a new log and hook up our log class
log_name = "logs/atmobot-log-{timestamp}.log".format(timestamp=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
log = open(log_name, "ab")
logOut = LogOutput(sys.__stdout__, log)
logErr = LogOutput(sys.__stderr__, log)
sys.stdout = logOut
sys.stderr = logErr
sys.stdout.console = True
sys.stderr.console = True

# Set up prefixes that can be used to call the bot
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

# Create the Atmobot class and run the bot
atmobot = Atmobot(command_prefix = _prefix_callable, case_insensitive = True, description = bot_globals.bot_description, intents = Intents.all(), help_command = None, startup_time = datetime.datetime.now())
token = settings.get("bot_token", "")
atmobot.run(token)
