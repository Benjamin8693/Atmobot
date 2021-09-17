# 3rd-Party Packages
from discord import Color, File, Embed
from discord.ext import commands
from discord.ext.commands import bot
from discord.ext.commands.core import command
from discord_components import Button, ButtonStyle, InteractionType
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

    def __init__(self, rate, per, alter_rate, alter_per, bucket, bot_channel_id):

        self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
        self.alter_mapping = commands.CooldownMapping.from_cooldown(alter_rate, alter_per, bucket)

        self._bucket_type = bucket

        self.bot_channel_id = bot_channel_id

    def __call__(self, ctx):

        # Match the channel sent to the appropriate cooldown
        current_channel = ctx.channel.id

        try:
            if current_channel == self.bot_channel_id:
                bucket = self.alter_mapping.get_bucket(ctx)
            else:
                bucket = self.default_mapping.get_bucket(ctx)
        except Exception as e:
            print(e)

        # Handle normal cooldown stuff
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)

        return True

class CommandsCenter(commands.Cog):

    # TODO: Research a way so that it pulls these from the config
    subscribed_guilds = [231218732440092675, 602983865237372958]
    bot_channel_id = 372517147068596225

    def __init__(self, bot):

        self.bot = bot

        self.patcher_historicals = []
        self.website_historicals = []

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
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
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
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
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
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
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
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
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
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
    async def spoilers(self, ctx):
        await self.bot.spoilers.test_file_update()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
    async def clear(self, ctx, amount: typing.Optional[str] = "1"):

        # Logging
        print("{time} | CLEAR: {user} requested to clear {amount} messages from {channel_name}".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author), amount=amount, channel_name=ctx.message.channel.name))

        # Make sure an actual digit was provided
        if not amount.isdigit():
            return
        amount = int(amount)

        # Delete the messages
        await ctx.channel.purge(limit=amount)

        # Send notification in the channel that the messages were deleted
        await ctx.send("{amount} messages cleared.".format(amount=amount), delete_after=5)

        # Log the result
        print("{time} | CLEAR: Cleared {amount} messages from {channel_name}".format(time=await self.bot.get_formatted_time(), amount=amount, channel_name=ctx.message.channel.name))

    @cog_ext.cog_slash(name=bot_globals.command_uptime_name, description=bot_globals.command_uptime_description, guild_ids=subscribed_guilds)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
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
        await ctx.send("Atmobot uptime: {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds.".format(days=days_formatted, hours=hours_formatted, minutes=minutes_formatted, seconds=seconds_formatted))

        # Log the result
        print("{time} | UPTIME: Bot has been up for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds".format(time=await self.bot.get_formatted_time(), days=days_formatted, hours=hours_formatted, minutes=minutes_formatted, seconds=seconds_formatted))

    @cog_ext.cog_slash(name=bot_globals.command_meme_name, description=bot_globals.command_meme_description, guild_ids=subscribed_guilds)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
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
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.check(CommandsCooldown(1, bot_globals.default_command_cooldown, 1, bot_globals.extended_command_cooldown, commands.BucketType.channel, bot_channel_id))
    async def website(self, ctx):
        website_change = await self.bot.checker.check_url_status()

        if not website_change:
            await ctx.send("No website change.")
        else:
            await ctx.send("Website change!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def patcher(self, ctx):
        response_code = await self.bot.checker.check_patcher()

        await ctx.send("Patcher error code is {}.".format(response_code))

    # Generates a set of buttons users can click on to check Test Realm status manually
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def status(self, ctx):

        # Embed header
        initial_embed = Embed(title="Wizard101 Test Realm Status", color=Color.blurple())

        # Disclaimer so people don't flip their shit and take the bot as gospel
        initial_embed.add_field(name="Notice",
                                value=f"This bot is experimental! Do not take any response given as an absolute indicator of Test Realm. While the intended purpose of Atmobot is to check for Test Realm activity, at the end of the day we're all just having fun!",
                                inline=False)

        # Explains what the patcher status actually is
        initial_embed.add_field(name="Patcher Status",
                                value=f"If the game patcher is being modified, it is possible (but not certain) Test Realm could be releasing soon. Once the patcher is completely up, The Atmoplex will begin datamining the new update, and posts will be made to Twitter momentarily.",
                                inline=False)

        # Likewise with website status
        initial_embed.add_field(name="Website Status",
                                value=f"There are various websites that contain information regarding Test Realm. If any of these see a change, it is likely Test Realm could be releasing soon.",
                                inline=False)

        # Buttons to check the patcher status (technically there are two, but one is always invisible)
        patcher_button_normal = Button(style=ButtonStyle.blue, label="Patcher Status")
        patcher_button_cooldown = Button(style=ButtonStyle.blue, label="Patcher Status (Cooldown)", disabled=True)
        patcher_button_state = patcher_button_normal

        # Likewise with patcher buttons
        website_button_normal = Button(style=ButtonStyle.green, label="Website Status")
        website_button_cooldown = Button(style=ButtonStyle.green, label="Website Status (Cooldown)", disabled=True)
        website_button_state = website_button_normal

        # Send the embed
        message = await ctx.send(embed=initial_embed, components=[patcher_button_state, website_button_state])

        # Set up a loop that waits for users to press a button
        await self.handle_button_press(ctx, initial_embed, message, patcher_button_normal, patcher_button_cooldown, website_button_normal, website_button_cooldown, patcher_button_state, website_button_state, patcher_message=None, website_message=None, patcher_processed=0, website_processed=0)

    async def handle_button_press(self, ctx, initial_embed, message, patcher_button_normal, patcher_button_cooldown, website_button_normal, website_button_cooldown, patcher_button_state, website_button_state, patcher_message, website_message, patcher_processed, website_processed):

        # We only care about button presses in the channel our message was sent in
        def check(response):
            return response.channel == ctx.channel

        # Wait for the button press
        res = await self.bot.wait_for("button_click", check=check)

        # Handle the patcher button
        if res.component.label.startswith("Patcher"):

            patcher_processed += 1

            message_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            patcher_embed = Embed(title="Patcher Status", color=Color.orange())
            patcher_embed.add_field(name="Please Wait",
                                    value="Attempting to fetch the patcher error code.",
                                    inline=False)

            await res.respond(type=InteractionType.DeferredUpdateMessage)

            if patcher_message:
                await patcher_message.edit(embed=patcher_embed)
            else:
                patcher_message = await ctx.send(embed=patcher_embed)

            # Disable patcher button
            patcher_button_state = patcher_button_cooldown
            website_button_state = website_button_cooldown
            await message.edit(embed=initial_embed, components=[patcher_button_state, website_button_state])

            # Color the embed based on the response code we've obtained
            embed_color = Color.red()
            response_code = await self.bot.checker.check_patcher()
            if response_code in list(bot_globals.patcher_tips.keys()):
                embed_color = Color.green()

            author_name = res.user

            patcher_embed = Embed(title="Patcher Status", color=embed_color)

            if patcher_processed > 1:
                patcher_footer = "Pressed a total of {} times. Check below for the 3 most recent error codes.".format(patcher_processed)
            else:
                patcher_footer = "Pressed a total of {} time. Check below for the 3 most recent error codes.".format(patcher_processed)
            patcher_embed.add_field(name="Overview",
                                    value=patcher_footer,
                                    inline=False)

            patcher_info = (response_code, author_name, message_timestamp)
            if len(self.patcher_historicals) >= 3:
                del self.patcher_historicals[0]
            self.patcher_historicals.append(patcher_info)

            for historical in self.patcher_historicals:
                index = self.patcher_historicals.index(historical)

                response_code = historical[0]
                author_name = historical[1]
                message_timestamp = historical[2]
                patcher_tip = bot_globals.patcher_tips.get(response_code)
                if not patcher_tip:
                    patcher_tip = "The Patcher is offline"
                patcher_embed.add_field(name="Error code {}".format(response_code),
                                        value="{}.\nRequested by {} @ {} ET".format(patcher_tip, author_name, message_timestamp),
                                        inline=False)

            # Send response
            if patcher_message:
                await patcher_message.edit(embed=patcher_embed)

            # In 30 seconds re-enable patcher button
            time.sleep(15)
            patcher_button_state = patcher_button_normal
            website_button_state = website_button_normal
            await message.edit(embed=initial_embed, components=[patcher_button_state, website_button_state])

        # Handle the website button
        elif res.component.label.startswith("Website"):

            website_processed += 1

            message_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            website_embed = Embed(title="Website Status", color=Color.orange())
            website_embed.add_field(name="Please Wait",
                                    value="Attempting to check the website status.",
                                    inline=False)

            await res.respond(type=InteractionType.DeferredUpdateMessage)

            if website_message:
                await website_message.edit(embed=website_embed)
            else:
                website_message = await ctx.send(embed=website_embed)

            # Disable website button
            patcher_button_state = patcher_button_cooldown
            website_button_state = website_button_cooldown
            await message.edit(embed=initial_embed, components=[patcher_button_state, website_button_state])

            website_change = await self.bot.checker.check_url_status()
            if website_change:
                embed_color = Color.green()
            else:
                embed_color = Color.red()

            author_name = res.user

            website_embed = Embed(title="Website Status", color=embed_color)

            if website_processed > 1:
                website_footer = "Pressed a total of {} times. Check below for the 3 most recent website checks.".format(website_processed)
            else:
                website_footer = "Pressed a total of {} time. Check below for the 3 most recent website checks.".format(website_processed)
            website_embed.add_field(name="Overview",
                                    value=website_footer,
                                    inline=False)

            website_info = (website_change, author_name, message_timestamp)
            if len(self.website_historicals) >= 3:
                del self.website_historicals[0]
            self.website_historicals.append(website_info)

            for historical in self.website_historicals:
                index = self.website_historicals.index(historical)

                website_change = historical[0]
                author_name = historical[1]
                message_timestamp = historical[2]

                if website_change:
                    change_header = "Website Updated"
                    change_footer = "A Test Realm related website page updated!. Go check to see if the update notes are out, or if the launcher has updated!"
                else:
                    change_header = "No Update"
                    change_footer = "There have been no Test Realm website changes."

                website_embed.add_field(name=change_header,
                                        value="{}\nRequested by {} @ {} ET".format(change_footer, author_name, message_timestamp),
                                        inline=False)

            # Send response
            if website_message:
                await website_message.edit(embed=website_embed)

            # In 30 seconds re-enable website button
            time.sleep(15)
            patcher_button_state = patcher_button_normal
            website_button_state = website_button_normal
            await message.edit(embed=initial_embed, components=[patcher_button_state, website_button_state])

        # Loop back around and wait for the next time the button is pressed
        await self.handle_button_press(ctx, initial_embed, message, patcher_button_normal, patcher_button_cooldown, website_button_normal, website_button_cooldown, patcher_button_state, website_button_state, patcher_message, website_message, patcher_processed, website_processed)

# Used for connecting the Command Center to the rest of the bot
def setup(bot):
    bot.add_cog(CommandsCenter(bot=bot))
