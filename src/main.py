# 3rd-Party Packages
from discord import Intents
from discord.ext import commands

# Local packages
import bot_globals
import bruteforcer
import scheduler
import spoilers
import utils

# Built-in packages
import asyncio
import datetime
import inspect
import json
import os
import sys
import time


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

        # TEMP HACK
        self.running_tasks = []

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

            print("{time} | RECONNECT: Bot reconnected to Discord API".format(time=utils.get_formatted_time()))

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

        # Bruteforcer class used for checking url and patcher status
        print("{time} | STARTUP: Loading Bruteforcer".format(time=await self.get_formatted_time()))
        self.bruteforcer = bruteforcer.Bruteforcer(self)
        await self.bruteforcer.startup()

        # Automatic spoiler system
        print("{time} | STARTUP: Loading Spoilers Center".format(time=await self.get_formatted_time()))
        self.spoilers = spoilers.Spoilers(self)
        await self.spoilers.startup()

        await self.load_scheduler()

        # Set up Discord logging
        sys.stdout.bot = self
        sys.stdout.load_log_channel()
        sys.stderr.bot = self
        sys.stderr.load_log_channel()

    async def load_scheduler(self):

        # If we don't have a scheduler config file, generate one with default options
        if not os.path.isfile(bot_globals.scheduler_path):
            with open(bot_globals.scheduler_path, "w") as data:
                json.dump(bot_globals.scheduler_template, data, indent=4)

        # Load our scheduler config
        with open(bot_globals.scheduler_path) as data:
            self.scheduler_config = json.load(data)

        # Load all scheduled tasks
        await self.load_scheduled_functions()
        await self.populate_tasks()

    async def load_scheduled_functions(self):

        self.all_scheduled_functions = {}

        classes_to_inspect = (self, self.bruteforcer, self.spoilers)
        for inspection in classes_to_inspect:
            
            all_methods = inspect.getmembers(inspection, predicate = inspect.ismethod)
            for method_pair in all_methods:

                method_name = method_pair[0]
                method = method_pair[1]

                # If this method name has already been registered, rename it using it's class name
                if method_name in self.all_scheduled_functions:
                    class_name = inspection.__class__.__name__
                    method_name = "{class_name}_{method_name}".format(class_name = class_name, method_name = method_name)
                
                self.all_scheduled_functions[method_name] = method

    async def populate_tasks(self):

        if not self.scheduler_config:
            return

        # Load all our scheduled tasks
        date_tasks = self.scheduler_config.get("date")
        tick_tasks = self.scheduler_config.get("tick")
        manual_tasks = self.scheduler_config.get("manual")

        # Handle date tasks
        for task in date_tasks:
            date_task_name = task.get("name")
            date_task_time = task.get("initial_time")
            date_task_method = task.get("method")
            date_task_args = task.get("args")
            if date_task_time and date_task_method and date_task_name not in self.running_tasks:
                self.running_tasks.append(date_task_name)
                await scheduler.DateEvent.create(date_task_time, date_task_method, *date_task_args)

        # Handle tick tasks
        for task in tick_tasks:
            date_task_name = task.get("name")
            tick_task_initial_time = task.get("initial_time")
            tick_task_delay = task.get("delay")
            tick_task_method = task.get("method")
            tick_task_args = task.get("args")
            if tick_task_delay and tick_task_method and date_task_name not in self.running_tasks:
                self.running_tasks.append(date_task_name)
                await scheduler.TickEvent.create(tick_task_initial_time, tick_task_delay, tick_task_method, *tick_task_args)

    async def add_scheduled_task(self, task_name, method_name, method_args = None, initial_time = None, delay = None):

        # No initial time? How about now! 
        if not initial_time:
            initial_time = int(round((datetime.datetime.now() + datetime.timedelta(seconds = 5)).timestamp()))
        
        if delay:
            task_type = "tick"
            task_data = {"name": task_name,
                         "active": True,
                         "initial_time": initial_time,
                         "delay": delay,
                         "method": method_name,
                         "args": [] if not method_args else method_args}

        elif initial_time:
            task_type = "date"
            task_data = {}

        else:
            task_type = "manual"
            task_data = {}

        task_type_data = self.scheduler_config.get(task_type)
        task_type_data.append(task_data)

        await self.update_scheduler_config(task_type, task_type_data)
        await self.populate_tasks()
    
    async def update_scheduler_config(self, config_name, variable_to_replace):

        # We typically shouldn't be updating a config variable that doesn't already exist
        if config_name not in self.scheduler_config:
            print("Updated config variable '{}' that does not exist!".format(config_name))

        # Update the config variable
        self.scheduler_config[config_name] = variable_to_replace

        # Save our config
        await self.save_scheduler_config()

    async def save_scheduler_config(self):

        # Write to the scheduler config file
        with open(bot_globals.scheduler_path, "w") as data:
            json.dump(self.scheduler_config, data, indent=4)

    def get_scheduled_function(self, function_name):

        scheduled_function = self.all_scheduled_functions.get(function_name)
        if not scheduled_function:
            return self.scheduled_message_error

        return scheduled_function

    async def scheduled_message_error(self, *args):
        print("Attempted to run a scheduled task but a function could not be found!")

    async def send_to_discord(self, channel_id, message, files = None):

        # Get the channel from it's ID
        discord_channel = self.get_channel(channel_id)
        if not discord_channel:
            return False

        # Send the message and any files
        try:
            await discord_channel.send(message, file = files)

        # TODO: Should only error out if the file you're sending is too large.
        except Exception as error:
            print(error)
            print("Failed to send discord image!")

    async def send_to_twitter(self, message, files = None):
        
        # By default, the media we're going to upload is just the list of file names
        media = files

        # For uploading mp4 files, we need to upload ahead of time and then provide a media ID
        if type(files) == str and files.endswith(".mp4"):

            # TODO: Move Twitter API loading to main.py instead of spoilers.py
            media: int = self.spoilers.twitter_api.UploadMediaChunked(media = files, media_category = 'tweet_video')

            # Sleep so that our uploaded video has some time to process
            # We're using time.sleep() here because asyncio.sleep() doesn't work in a thread
            #time.sleep(bot_globals.twitter_video_process_time)

        if not media:
            return

        # Publish the tweet
        # TODO: Re-add "in_reply_to_status_id"
        try:
            status = self.spoilers.twitter_api.PostUpdate(status = message, media = media)

        # TODO: Should only error out if the file you're sending is too large.
        except Exception as error:
            print(error)
            print("Failed to send twitter image!")

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
if sys.platform in ("linux", "linux2"):
    os.environ['TZ'] = "America/Chicago"
    time.tzset()
atmobot = Atmobot(command_prefix = _prefix_callable, case_insensitive = True, description = bot_globals.bot_description, intents = Intents.all(), help_command = None, startup_time = datetime.datetime.now())
token = settings.get("bot_token", "")
atmobot.run(token)
