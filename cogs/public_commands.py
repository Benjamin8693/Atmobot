# 3rd-Party Packages
from discord import Color, File, Embed
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

# Local packages
import bot_globals

# Built-in packages
import datetime
import os
import random
import sys
import time
import traceback
import typing
import uuid

class CommandsCooldown:

    def __init__(self, rate, per, alter_rate, alter_per, bucket, cooldown_exempt_channel_ids, cooldown_exempt_role_ids):

        self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
        self.alter_mapping = commands.CooldownMapping.from_cooldown(alter_rate, alter_per, bucket)

        self._bucket_type = bucket

        self.cooldown_exempt_channel_ids = cooldown_exempt_channel_ids
        self.cooldown_exempt_role_ids = cooldown_exempt_role_ids

    def __call__(self, ctx):

        # Match the channel sent to the appropriate cooldown
        current_channel = ctx.channel.id
        role_ids = (x.id for x in ctx.author.roles)

        try:

            # Exempt channels and roles get lower cooldowns
            if (current_channel in self.cooldown_exempt_channel_ids) or any(check in self.cooldown_exempt_role_ids for check in role_ids):
                bucket = self.alter_mapping.get_bucket(ctx)

            # Everything else gets a regular cooldown
            else:
                bucket = self.default_mapping.get_bucket(ctx)

        except Exception as e:
            print(e)

        # Handle normal cooldown stuff
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)

        return True

class PublicCommands(commands.Cog):

    subscribed_guild_ids = settings.get("subscribed_guild_ids", [])
    cooldown_exempt_channel_ids = settings.get("cooldown_exempt_channel_ids", [])
    cooldown_exempt_role_ids = settings.get("cooldown_exempt_role_ids", [])

    def __init__(self, bot):

        self.bot = bot

        # Quote command history
        self.message_history = {}

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        await self.handle_error(ctx, error)

    async def cog_command_error(self, ctx, error):
        await self.handle_error(ctx, error)

    async def handle_error(self, ctx, error):

        # Errors to ignore
        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return

        # Cooldown error
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_embed = Embed(title=f"You are on cooldown.", description=f"Try again in {error.retry_after:.2f}s.", color=Color.red())
            await ctx.send(embed=cooldown_embed)

        # Print traceback
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def get_full_username(self, user):
        user_name = user.name
        user_discriminator = user.discriminator

        full_username = "{user_name}#{user_discriminator}".format(user_name=user_name, user_discriminator=user_discriminator)
        return full_username

    @cog_ext.cog_slash(name=bot_globals.command_hero101_name, description=bot_globals.command_hero101_description, guild_ids=subscribed_guild_ids)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    async def hero101(self, ctx):

        # Logging
        print("{time} | HERO101: {user} requested a Hero101 asset.".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        # Path to get our Hero101 assets from
        current_path = os.path.join(os.getcwd(), bot_globals.resources_path, bot_globals.hero101_path)

        # Pick a random file
        all_files = [x for x in list(os.scandir(current_path)) if x.is_file()]
        random_file = random.choice(all_files).name

        # Generate a file path and send the file
        file_path = os.path.join(current_path, random_file)
        file_to_send = File(file_path)
        await ctx.send(file=file_to_send)

        # Log the result
        print("{time} | HERO101: Random Hero101 asset '{file_path}' uploaded".format(time=await self.bot.get_formatted_time(), file_path=random_file))

    @cog_ext.cog_slash(name=bot_globals.command_remco_name, description=bot_globals.command_remco_description, guild_ids=subscribed_guild_ids)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    async def remco(self, ctx):

        # Logging
        print("{time} | REMCO: {user} requested Remco ascii art".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))
        
        # Send the amount of days
        await ctx.send(bot_globals.command_remco_art)

        # Log the result
        print("{time} | REMCO: Ascii art posted".format(time=await self.bot.get_formatted_time()))

    user_choices = []
    available_users = {}
    quote_users = settings.get("quote_users", [])
    for quote_user in quote_users:
        user_name = quote_user[bot_globals.COMMAND_QUOTE_USER_NAME]
        user_id = quote_user[bot_globals.COMMAND_QUOTE_USER_ID]
        date_range = quote_user[bot_globals.COMMAND_QUOTE_DATE_RANGE]
        available_users[user_name] = [user_id, date_range]
        choice = create_choice(name=user_name.capitalize(), value=user_name)
        user_choices.append(choice)
    user_option = create_option(name=bot_globals.command_quote_arg_user_name, description=bot_globals.command_quote_arg_user_description, option_type=3, required=True, choices=user_choices)
    @cog_ext.cog_slash(name=bot_globals.command_quote_name, description=bot_globals.command_quote_description, guild_ids=subscribed_guild_ids, options=[user_option])
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    async def quote(self, ctx, user: str):

        # Grab user details
        user_data = self.available_users.get(user)
        user_id = user_data[bot_globals.COMMAND_QUOTE_USER_ID - 1]
        date_range = user_data[bot_globals.COMMAND_QUOTE_DATE_RANGE - 1]
        formatted_user = user.capitalize()

        # Logging
        print("{time} | QUOTE: {requester} requested quote of user {user}".format(time=await self.bot.get_formatted_time(), requester=await self.get_full_username(ctx.author), user=formatted_user))

        # Generate chat history for the author if it doesn't exist
        if user not in self.message_history:

            history = []
            self.message_history[user] = history

            # Notify that we're generating the quote library
            await ctx.send("Generating Quote library for {user}. Please wait a little bit, then try again.".format(user=formatted_user))

            # Grab the past x messages from the quote channel
            channel_id = settings.get("quote_channel_id", 0)
            if not channel_id:
                await ctx.send("Quote channel ID not set!")
                print("{time} | QUOTE: Quote channel ID not set".format(time=await self.bot.get_formatted_time()))
                return

            reference_channel = self.bot.get_channel(channel_id)
            if date_range:
                reference_time = datetime.datetime(*date_range)
            else:
                reference_time = datetime.datetime.now()
            async for message in reference_channel.history(limit=bot_globals.command_quote_message_history, before=reference_time.replace(tzinfo=None)):
                if message.author.id == user_id:
                    if len(message.content) > bot_globals.command_quote_message_threshold and (not "<@" in message.content) and (not "<:" in message.content):
                        history.append(message.content)

            # Add them to history
            self.message_history[user] = history

            # Quote library finished generating
            print("{time} | QUOTE: Quote library for {user} generated".format(time=await self.bot.get_formatted_time(), user=formatted_user))
            return

        # Grab chat history from this user
        history = self.message_history.get(user)

        # We don't have any chat history to grab a quote from
        if not history:
            await ctx.send("There are no available quotes  for {user}.".format(user=formatted_user))
            print("{time} | QUOTE: No available quotes for {user}".format(time=await self.bot.get_formatted_time(), user=formatted_user))
            return

        # Pick a random messgae from the history and send it
        random_message = random.choice(history)
        await ctx.send("**{user}:** \"{message}\"".format(user=formatted_user, message=random_message))

        # Log the result
        print("{time} | QUOTE: Quote \"{quote}\" from {user} posted".format(time=await self.bot.get_formatted_time(), quote=random_message, user=formatted_user))

    @cog_ext.cog_slash(name=bot_globals.command_testrealm_name, description=bot_globals.command_testrealm_description, guild_ids=subscribed_guild_ids)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    #@commands.command()
    #@commands.has_permissions(manage_messages=True)
    async def testrealm(self, ctx):

        # Logging
        print("{time} | TESTREALM: {user} requested Test Realm information".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        # Embed structure to work with
        test_embed = Embed(title=bot_globals.command_testrealm_embed_title, color=Color.gold())

        # Add information about Test Realm
        test_embed.add_field(name=bot_globals.command_testrealm_embed_intro_title, value=bot_globals.command_testrealm_embed_intro_description, inline=False)
        test_embed.add_field(name=bot_globals.command_testrealm_embed_historicals_title, value=bot_globals.command_testrealm_embed_historicals_description, inline=False)
        test_embed.add_field(name=bot_globals.command_testrealm_embed_summary_title, value=bot_globals.command_testrealm_embed_summary_description, inline=False)
        test_embed.add_field(name=bot_globals.command_testrealm_embed_estimation_title, value=bot_globals.command_testrealm_embed_estimation_description, inline=False)

        # Send the embed
        await ctx.send(embed=test_embed)

        # Log the result
        print("{time} | TESTREALM: Test Realm information posted".format(time=await self.bot.get_formatted_time()))
    
    @cog_ext.cog_slash(name=bot_globals.command_days_name, description=bot_globals.command_days_description, guild_ids=subscribed_guild_ids)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    async def days(self, ctx):

        # Logging
        print("{time} | DAYS: {user} requested days until Test Realm Watch".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        today = datetime.date.today()
        future = datetime.date(2022, 7, 5)
        diff = future - today

        # Days plural
        s = ""
        verb = "is"
        if diff.days > 1:
            s = "s"
            verb = "are"

        # Format month and day
        month_name = future.strftime("%B")
        if 4 <= future.day <= 20 or 24 <= future.day <= 30:
            day_suffix = "th"
        else:
            day_suffix = ["st", "nd", "rd"][future.day % 10 - 1]
        formatted_day = "{month_name} {day}{day_suffix}".format(month_name=month_name, day=future.day, day_suffix=day_suffix)

        # Send the amount of days
        if diff.days > 0:
            formatted_days = bot_globals.command_days_formatted.format(verb=verb, days=diff.days, s=s, date=formatted_day)
            await ctx.send(formatted_days)
        else:
            await ctx.send(bot_globals.command_days_watch)

        # Log the result
        print("{time} | DAYS: {days} day{s} until Test Realm Watch".format(time=await self.bot.get_formatted_time(), days=diff.days, s=s))

    header_option = create_option(name=bot_globals.command_thumbnail_arg_header_name, description=bot_globals.command_thumbnail_arg_header_description, option_type=3, required=True)
    footer_option = create_option(name=bot_globals.command_thumbnail_arg_footer_name, description=bot_globals.command_thumbnail_arg_footer_description, option_type=3, required=True)
    game_option = create_option(name=bot_globals.command_thumbnail_arg_type_name, description=bot_globals.command_thumbnail_arg_type_description, option_type=3, required=False, choices=list(bot_globals.command_thumbnail_extras.keys()))
    @cog_ext.cog_slash(name=bot_globals.command_thumbnail_name, description=bot_globals.command_thumbnail_description, guild_ids=subscribed_guild_ids, options=[header_option, footer_option, game_option])
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    async def thumbnail(self, ctx, header: str, footer: str, type: str = None):

        # Logging
        print("{time} | THUMBNAIL: {user} requested custom thumbnail with header \"{thumbnail_header}\", footer \"{thumbnail_footer}\", and type \"{thumbnail_type}\"".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author), thumbnail_header=header, thumbnail_footer=footer, thumbnail_type=type))

        # If no thumbnail type was provided, use the game the bot is currently set up for
        if not type:
            thumb_id = settings.get("game_id", -1)
            type = bot_globals.game_longhands.get(thumb_id)

        # Capitalize our header and footer if the thumbnail type calls for it
        thumb_info = bot_globals.command_thumbnail_extras.get(type)
        capitalize = thumb_info[bot_globals.COMMAND_THUMBNAIL_UPPERCASE]
        if capitalize:
            header = header.upper()
            footer = footer.upper()

        # Generate a thumbnail from the creator we have in our spoilers submodule
        file_name = bot_globals.command_thumbnail_file_name.format(str(uuid.uuid4())[:8])
        await self.bot.spoilers.create_video_thumbnail(file_name, header, footer, thumb_type=type)

        # Upload our completed thumbnail so long as it successfully generated
        file_path = os.path.join(os.getcwd(), bot_globals.resources_path, bot_globals.video_path, bot_globals.thumbnail_output_path.format(file_name=file_name))
        file_to_send = File(file_path)
        await ctx.send(file=file_to_send)

        # Delete the file
        os.remove(file_path)

        # Log the result
        print("{time} | THUMBNAIL: Custom thumbnail with header {thumbnail_header} and footer {thumbnail_footer} uploaded".format(time=await self.bot.get_formatted_time(), thumbnail_header=header, thumbnail_footer=footer))

    @cog_ext.cog_slash(name=bot_globals.command_stats_name, description=bot_globals.command_stats_description, guild_ids=subscribed_guild_ids)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    async def stats(self, ctx):

        # Logging
        print("{time} | STATS: {user} requested bot stats".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        # Find how much time has elasped since we started the bot
        current_time = datetime.datetime.now()
        elasped_time = current_time - self.bot.startup_time

        # Format the elasped time properly
        days_formatted = elasped_time.days
        hours_formatted = elasped_time.seconds // 3600
        minutes_formatted = elasped_time.seconds // 60 % 60
        seconds_formatted = elasped_time.seconds % 60

        # Gather version and release notes from settings
        release_info = settings.get("release_info", [])
        if release_info:
            release_version = release_info[bot_globals.COMMAND_STATS_RELEASE_VERSION]
            release_notes = release_info[bot_globals.COMMAND_STATS_RELEASE_NOTES]
        else:
            release_version = bot_globals.command_stats_release_version_unknown
            release_notes = None

        version = bot_globals.command_stats_version.format(version=release_version)
        if release_notes:
            formatted_notes = ""
            for release_note in release_notes:
                note = bot_globals.command_stats_release_note.format(note=release_note)
                formatted_notes += note
            notes = bot_globals.command_stats_notes.format(notes=formatted_notes)
            release = version + bot_globals.command_stats_newline + notes
        else:
            release = version + bot_globals.command_stats_newline
        
        uptime = bot_globals.command_stats_uptime.format(days=days_formatted, hours=hours_formatted, minutes=minutes_formatted, seconds=seconds_formatted)

        # Send the stats
        await ctx.send(release + bot_globals.command_stats_newline + uptime)

        # Log the result
        print("{time} | STATS: Bot has been up for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds".format(time=await self.bot.get_formatted_time(), days=days_formatted, hours=hours_formatted, minutes=minutes_formatted, seconds=seconds_formatted))

    @cog_ext.cog_slash(name=bot_globals.command_meme_name, description=bot_globals.command_meme_description, guild_ids=subscribed_guild_ids)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    async def meme(self, ctx):

        # Logging
        print("{time} | MEME: {user} requested a meme.".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        # Path to get our memes from
        current_path = os.path.join(os.getcwd(), bot_globals.resources_path, bot_globals.memes_path)

        # Pick a random file
        all_files = [x for x in list(os.scandir(current_path)) if x.is_file()]
        random_file = random.choice(all_files).name

        # Small chance of replacing this with a hidden meme
        hidden_memes = settings.get("hidden_memes", [])
        for hidden_meme in hidden_memes:
            meme_name = hidden_meme[bot_globals.COMMAND_MEME_HIDDEN_NAME]
            meme_rarity = hidden_meme[bot_globals.COMMAND_MEME_HIDDEN_RARITY]
            random.seed(len(meme_name) + time.time())
            if random.random() < 1.0 / meme_rarity:
                print("{time} | MEME: Hidden meme '{file_path}' activated".format(time=await self.bot.get_formatted_time(), file_path=meme_name))
                random_file = os.path.join(bot_globals.memes_hidden_path, meme_name)
                break

        # Generate a file path and send the file
        file_path = os.path.join(current_path, random_file)
        file_to_send = File(file_path)
        await ctx.send(file=file_to_send)

        # Log the result
        print("{time} | MEME: Random meme '{file_path}' uploaded".format(time=await self.bot.get_formatted_time(), file_path=random_file))

    def get_directories_from_path(self, current_path, return_as_strings=False):
        directories_to_return = []

        all_directories = [(x) for x in list(os.scandir(current_path)) if x.is_dir()]

        if return_as_strings:
            for directory in all_directories:
                directories_to_return.append(directory.name)
        else:
            directories_to_return = all_directories

        return directories_to_return

    deepfake_directories = get_directories_from_path(None, os.path.join(bot_globals.resources_path, bot_globals.deepfakes_path), return_as_strings=True)
    directory_choices = []
    for directory in deepfake_directories:
        choice = create_choice(name=directory.capitalize(), value=directory)
        directory_choices.append(choice)
    directory_option = create_option(name=bot_globals.command_deepfake_arg_directory_name, description=bot_globals.command_deepfake_arg_directory_description, option_type=3, required=False, choices=directory_choices)
    @cog_ext.cog_slash(name=bot_globals.command_deepfake_name, description=bot_globals.command_deepfake_description, guild_ids=subscribed_guild_ids, options=[directory_option])
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, cooldown_exempt_channel_ids, cooldown_exempt_role_ids))
    async def deepfake(self, ctx, directory: typing.Optional[str] = None):

        # Logging
        print("{time} | DEEPFAKE: {user} requested a deepfake with directory {directory}".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author), directory=directory))

        # Path to get our deepfakes from
        current_path = os.path.join(os.getcwd(), bot_globals.resources_path, bot_globals.deepfakes_path)

        # The user wants to know about our deepfake categories
        if directory and directory.lower() == "list":

            # Grab all the directories
            all_directories = self.get_directories_from_path(current_path, return_as_strings=True)
            categories_string = ", ".join(all_directories)

            # Relay our categories back to them
            await ctx.send("Deepfake categories: {}.".format(categories_string))

            # Log the result
            print("{time} | DEEPFAKE: Deepfake categories requested, returning category list '{category_list}'".format(time=await self.bot.get_formatted_time(), category_list=categories_string))

            return

        # If the user specifies a directory that doesn't exist, let them know
        elif directory and not os.path.exists(os.path.join(bot_globals.resources_path, bot_globals.deepfakes_path, directory)):

            # Send the message
            await ctx.send("Deepfake category '{}' does not exist!".format(directory))

            # Log the result
            print("{time} | DEEPFAKE: Deepfake category '{category}' requested, but does not exist".format(time=await self.bot.get_formatted_time(), category=directory))

            return

        # But if they specify a directory and it DOES exist, pick a random file from it
        elif directory and os.path.exists(os.path.join(bot_globals.resources_path, bot_globals.deepfakes_path, directory)):

            # Pick a random file
            all_files = [x for x in list(os.scandir(os.path.join(current_path, directory)))]
            random_file = random.choice(all_files).name

        # Otherwise just pick a random file AND directory
        else:

            # Pick a random directory
            all_directories = self.get_directories_from_path(current_path)
            directory = random.choice(all_directories).name

            # Pick a random file
            all_files = [x for x in list(os.scandir(os.path.join(current_path, directory)))]
            random_file = random.choice(all_files).name

        # Generate a file path and send the file
        file_path = os.path.join(current_path, directory, random_file)
        file_to_send = File(file_path)
        await ctx.send(file=file_to_send)

        # Log the result
        print("{time} | DEEPFAKE: Deepfake '{file_path}' uploaded".format(time=await self.bot.get_formatted_time(), file_path=random_file))

# Used for connecting the Command Center to the rest of the bot
def setup(bot):
    bot.add_cog(PublicCommands(bot=bot))
