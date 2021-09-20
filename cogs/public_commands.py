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
import traceback
import typing
import uuid

class CommandsCooldown:

    def __init__(self, rate, per, alter_rate, alter_per, bucket, bot_channel_id, nitro_role_id):

        self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
        self.alter_mapping = commands.CooldownMapping.from_cooldown(alter_rate, alter_per, bucket)

        self._bucket_type = bucket

        self.bot_channel_id = bot_channel_id
        self.nitro_role_id = nitro_role_id

    def __call__(self, ctx):

        # Match the channel sent to the appropriate cooldown
        current_channel = ctx.channel.id
        role_ids = (x.id for x in ctx.author.roles)

        try:

            # Bot commmands channel gets a lower cooldown
            # Also give an exception to Nitro Boosters
            if (current_channel == self.bot_channel_id) or (self.nitro_role_id in role_ids):
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

    subscribed_guilds = settings.get("subscribed_guilds", [])
    bot_channel_id = settings.get("bot_channel_id", 0)
    nitro_role_id = settings.get("nitro_role_id", 0)

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

    @cog_ext.cog_slash(name=bot_globals.command_remco_name, description=bot_globals.command_remco_description, guild_ids=subscribed_guilds)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id, nitro_role_id))
    async def remco(self, ctx):

        # Logging
        print("{time} | REMCO: {user} requested Remco ascii art".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))
        
        # Send the amount of days
        await ctx.send(bot_globals.command_remco_art)

        # Log the result
        print("{time} | REMCO: Ascii art posted".format(time=await self.bot.get_formatted_time()))

    author_choices = []
    for author_name in list(bot_globals.command_quote_authors.keys()):
        choice = create_choice(name=author_name.capitalize(), value=author_name)
        author_choices.append(choice)
    author_option = create_option(name=bot_globals.command_quote_arg_author_name, description=bot_globals.command_quote_arg_author_description, option_type=3, required=True, choices=author_choices)
    @cog_ext.cog_slash(name=bot_globals.command_quote_name, description=bot_globals.command_quote_description, guild_ids=subscribed_guilds, options=[author_option])
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id, nitro_role_id))
    async def quote(self, ctx, author: str):

        # Grab author details
        author_data = bot_globals.command_quote_authors.get(author)
        author_id = author_data[bot_globals.COMMAND_QUOTE_AUTHOR_ID]
        date_range = author_data[bot_globals.COMMAND_QUOTE_DATE_RANGE]
        author_username = author.capitalize()

        # Logging
        print("{time} | QUOTE: {user} requested quote of user {author}".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author), author=author_username))

        # Generate chat history for the author if it doesn't exist
        if author not in self.message_history:

            history = []
            self.message_history[author] = history

            # Notify that we're generating the quote library
            await ctx.send("Generating Quote library for {author_name}. This could take a few minutes.".format(author_name=author_username))

            # Grab the past 10,000 messages from the quote channel
            reference_channel = self.bot.get_channel(bot_globals.command_quote_channel_id)
            if date_range:
                reference_time = datetime.datetime(*date_range)
            else:
                reference_time = datetime.datetime.now()
            async for message in reference_channel.history(limit=bot_globals.command_quote_message_limit, before=reference_time.replace(tzinfo=None)):
                if message.author.id == author_id:
                    if len(message.content) > 10 and (not "<@" in message.content) and (not "<:" in message.content):
                        history.append(message.content)

            # Add them to history
            self.message_history[author] = history

            # Quote library finished generating
            print("{time} | QUOTE: Quote library generated".format(time=await self.bot.get_formatted_time()))
            return

        # Grab chat history from this author
        history = self.message_history.get(author)

        # We don't have any chat history to grab a quote from quite yet
        if not history:
            await ctx.send("Quote library has not yet finished generating. Check back in a few minutes.")
            print("{time} | QUOTE: Still generating quote library".format(time=await self.bot.get_formatted_time()))
            return

        # Pick a random messgae from the history and send it
        random_message = random.choice(history)
        await ctx.send("**{author_name}:** \"{message}\"".format(author_name=author_username, message=random_message))

        # Log the result
        print("{time} | QUOTE: Quote \"{quote}\" from {author_name} posted".format(time=await self.bot.get_formatted_time(), quote=random_message, author_name=author_username))

    @cog_ext.cog_slash(name=bot_globals.command_days_name, description=bot_globals.command_days_description, guild_ids=subscribed_guilds)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id, nitro_role_id))
    async def days(self, ctx):

        # Logging
        print("{time} | DAYS: {user} requested days until Test Realm Watch".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        today = datetime.date.today()
        future = datetime.date(2021, 10, 18)
        diff = future - today
        
        # Send the amount of days
        formatted_days = bot_globals.command_days_formatted.format(days=diff.days)
        await ctx.send(formatted_days)

        # Log the result
        print("{time} | DAYS: {days} days until Test Realm Watch".format(time=await self.bot.get_formatted_time(), days=diff.days))

    @cog_ext.cog_slash(name=bot_globals.command_testrealm_name, description=bot_globals.command_testrealm_description, guild_ids=subscribed_guilds)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id, nitro_role_id))
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

    header_option = create_option(name=bot_globals.command_thumbnail_arg_header_name, description=bot_globals.command_thumbnail_arg_header_description, option_type=3, required=True)
    footer_option = create_option(name=bot_globals.command_thumbnail_arg_footer_name, description=bot_globals.command_thumbnail_arg_footer_description, option_type=3, required=True)
    game_option = create_option(name=bot_globals.command_thumbnail_arg_game_name, description=bot_globals.command_thumbnail_arg_game_description, option_type=3, required=False, choices=list(bot_globals.longhand_to_game.keys()))
    @cog_ext.cog_slash(name=bot_globals.command_thumbnail_name, description=bot_globals.command_thumbnail_description, guild_ids=subscribed_guilds, options=[header_option, footer_option, game_option])
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id, nitro_role_id))
    async def thumbnail(self, ctx, header: str, footer: str, game: str = None):

        # Logging
        print("{time} | THUMBNAIL: {user} requested custom thumbnail with title {thumbnail_header} and footer {thumbnail_footer}".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author), thumbnail_header=header, thumbnail_footer=footer))

        # Send the uptime
        file_name = bot_globals.thumbnail_command_name.format(str(uuid.uuid4())[:8])

        game_id = None
        if game:
            game_id = bot_globals.longhand_to_game.get(game)
        await self.bot.spoilers.create_video_thumbnail(file_name, header.upper(), footer.upper(), game_id=game_id)
        file_path = os.path.join(os.getcwd(), bot_globals.resources_path, bot_globals.video_path, bot_globals.thumbnail_output_path.format(file_name=file_name))
        file_to_send = File(file_path)
        await ctx.send(file=file_to_send)

        # Delete the file
        os.remove(file_path)

        # Log the result
        print("{time} | THUMBNAIL: Custom thumbnail with header {thumbnail_header} and footer {thumbnail_footer} uploaded".format(time=await self.bot.get_formatted_time(), thumbnail_header=header, thumbnail_footer=footer))

    @cog_ext.cog_slash(name=bot_globals.command_uptime_name, description=bot_globals.command_uptime_description, guild_ids=subscribed_guilds)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id, nitro_role_id))
    async def uptime(self, ctx):

        # Logging
        print("{time} | UPTIME: {user} requested bot uptime".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        # Find how much time has elasped since we started the bot
        current_time = datetime.datetime.now()
        elasped_time = current_time - self.bot.startup_time

        # Format the elasped time properly
        days_formatted = elasped_time.days
        hours_formatted = elasped_time.seconds // 3600
        minutes_formatted = elasped_time.seconds // 60 % 60
        seconds_formatted = elasped_time.seconds % 60

        # Send the uptime
        await ctx.send("Bot Uptime: {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds.".format(days=days_formatted, hours=hours_formatted, minutes=minutes_formatted, seconds=seconds_formatted))

        # Log the result
        print("{time} | UPTIME: Bot has been up for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds".format(time=await self.bot.get_formatted_time(), days=days_formatted, hours=hours_formatted, minutes=minutes_formatted, seconds=seconds_formatted))

    @cog_ext.cog_slash(name=bot_globals.command_meme_name, description=bot_globals.command_meme_description, guild_ids=subscribed_guilds)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id, nitro_role_id))
    async def meme(self, ctx):

        # Logging
        print("{time} | MEME: {user} requested a meme.".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        # Path to get our memes from
        current_path = os.path.join(os.getcwd(), bot_globals.resources_path, bot_globals.memes_path)

        # Pick a random file
        all_files = [x for x in list(os.scandir(current_path)) if x.is_file()]
        random_file = random.choice(all_files).name

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
    @cog_ext.cog_slash(name=bot_globals.command_deepfake_name, description=bot_globals.command_deepfake_description, guild_ids=subscribed_guilds, options=[directory_option])
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id, nitro_role_id))
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
