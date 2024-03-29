# 3rd-Party Packages
import backoff
from discord import Embed, File, Color, file
from discord.ext.commands import bot
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw
from numpy import broadcast_to
import tweepy
from wizdiff.delta import FileDelta
from wizdiff.update_notifier import UpdateNotifier
from wizdiff.utils import get_revision_from_url
#from wizwalker.file_readers.wad import Wad

# Local packages
import bot_globals

# Built-in packages
import asyncio
import difflib
import errno
import datetime
import json
import math
import os
import re
import requests
import threading
import time
import traceback
import urllib.request
import zlib

# Spoilers
class Spoilers(UpdateNotifier):

    def __init__(self, bot):

        UpdateNotifier.__init__(self)

        self.bot = bot

        # TODO: Move to main.py
        self.twitter_api_v1 = None
        self.twitter_api_v2 = None

        # TODO: REMOVE
        self.state = False

        # TODO: Keep track of most recent revision somewhere else
        self.revision_data = "r743518.Wizard_1_520"

        # Keep track of spoiler data
        self.important_update = False
        self.spoiler_config = {}
        self.chained_spoilers = {}
        self.last_tweet_ids = {bot_globals.CHANNEL_IMAGES: 0, bot_globals.CHANNEL_MUSIC: 0, bot_globals.CHANNEL_LOCALE: 0}
        self.files_to_tweet = []
        self.chained_tweet_status = {}
        self.goodbye_pending = False
        self.delay_music = True

        # Force disable Discord or Twitter posts
        self.discord_post_override = False
        self.twitter_post_override = False

    async def startup(self):

        # Load our spoilers config
        self.load_spoilers()
        
        # Log into our Twitter account so we can post stuff later
        print("{time} | SPOILERS: Logging into the Twitter API".format(time=await self.bot.get_formatted_time()))
        twitter_api_keys = settings.get("twitter_api_keys")
        if twitter_api_keys:

            # Grab keys from the settings
            consumer_key = twitter_api_keys[bot_globals.TWITTER_KEY_CONSUMER]
            consumer_secret = twitter_api_keys[bot_globals.TWITTER_KEY_CONSUMER_SECRET]
            access_token_key = twitter_api_keys[bot_globals.TWITTER_KEY_ACCESS_TOKEN]
            access_token_secret = twitter_api_keys[bot_globals.TWITTER_KEY_ACCESS_TOKEN_SECRET]
            bearer_token = twitter_api_keys[bot_globals.TWITTER_KEY_BEAR]

            # Load the API
            auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token_key, access_token_secret)
            self.twitter_api_v1 = tweepy.API(auth)
            self.twitter_api_v2 = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_token_key, access_token_secret=access_token_secret)

        # Check if we're logged in and verified
        #if self.twitter_api:
        #    verified = self.twitter_api.VerifyCredentials()

        # Notify about the API
        if not self.twitter_api_v1 and not self.twitter_api_v2:# or not verified:
            print("{time} | SPOILERS: Could not load the Twitter API".format(time=self.get_formatted_time()))
        else:
            print("{time} | SPOILERS: Logged into the Twitter API".format(time=self.get_formatted_time()))

    def load_spoilers(self):

        # If we don't have a spoiler config file, generate one
        if not os.path.isfile(bot_globals.spoilers_path):
            with open(bot_globals.spoilers_path, "w") as data:
                json.dump(bot_globals.spoilers_template, data, indent=4)

        # Load our spoiler config
        with open(bot_globals.spoilers_path) as data:
            self.spoiler_config = json.load(data)

    def get_formatted_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    async def get_state(self):
        return self.state

    async def update_loop(self, state = True):

        state_name = "Enabling" if state else "Disabling"
        print("{time} | SPOILERS: {state} revision check loop".format(time=await self.bot.get_formatted_time(), state=state_name))

        self.state = state

        if state:
            update = False
            while (not update) and self.state:

                try:

                    revision = None

                    # Bruteforce the revision
                    most_recent_version = await self.bot.bruteforcer.most_recent_revision()
                    version_list = [bot_globals.fallback_version_dev, most_recent_version]
                    revisions = await self.bot.bruteforcer.revision_bruteforcer.start(revision_start=most_recent_version, revision_range=bot_globals.default_revision_range, version_list=version_list)
                    
                    # We only care about the most recent revision
                    if revisions:
                        revision = revisions.pop()

                        formatted_revision = "{}.{}".format(revision[bot_globals.REVISION_NUMBER], revision[bot_globals.REVISION_VERSION])

                        if self.db.check_if_new_revision(formatted_revision):
                            print("{time} | SPOILERS: New revision {revision} found! Running file update protocol".format(time=await self.bot.get_formatted_time(), revision=formatted_revision))
                            self.revision_data = formatted_revision
                            await self.handle_revision()
                            update = True
                        else:
                            print("{time} | SPOILERS: No new revision found".format(time=await self.bot.get_formatted_time()))
                except:
                    print("{time} | SPOILERS: Patch server timed out and caused an exception".format(time=await self.bot.get_formatted_time()))

                if not update:
                    print("{time} | SPOILERS: Sleeping for 600 seconds".format(time=await self.bot.get_formatted_time()))
                    await asyncio.sleep(600)

    async def handle_revision(self, revision=None):

        print("{time} | SPOILERS: File updated detected! Handling revision {revision}".format(time=await self.bot.get_formatted_time(), revision=revision))

        # Disable all commands until we're done
        # TODO: Get this working
        #for command in self.bot.commands:
        #    print("command is {}".format(command))
        #    command.update(enable=False)

        # Process the revision through WizDiff
        #file_list_url, base_url = self.webdriver.get_patch_urls()
        #revision = get_revision_from_url(file_list_url)

        if not revision:
            revision = self.revision_data
        #file_list_url, base_url = await self.webdriver.get_patch_urls()
        #print("filelisturl and baseurl are {} and {}".format(file_list_url, base_url))
        file_list_url = "http://testversionec.us.wizard101.com/WizPatcher/V_{}/Windows/LatestFileList.bin".format(revision)
        base_url = "http://testversionec.us.wizard101.com/WizPatcher/V_{}/LatestBuild".format(revision)
        await self.new_revision(revision, file_list_url, base_url)

        # Re-enable commands
        # TODO: Get this working
        #for command in self.bot.commands:
        #    command.update(enable=True)

        # If our revision had something worth spoiling, we need to post our goodbyes once everything's wrapped up
        if self.important_update:

            # Only post our goodbyes if no chained tweets are in the pipeline
            if not self.chained_tweet_status:
                await self.post_goodbye()

            # We can't post goodbye yet, let's queue it up for later
            else:
                self.goodbye_pending = True

        else:

            print("{time} | SPOILERS: Attempted to spoil an update but nothing of interest was added".format(time=await self.bot.get_formatted_time()))

    async def post_introduction(self):

        print("{time} | SPOILERS: New files of interest detected! Posting Atmobot introduction".format(time=await self.bot.get_formatted_time()))

        # Announce a new revision on Discord
        # TODO: Make this a toggle, because for small patches we may not want a ping
        if not self.discord_post_override:

            # Discord channel to send our announcement in
            spoiler_channel_ids = settings.get("spoiler_channels")
            announcement_channel = self.bot.get_channel(spoiler_channel_ids[bot_globals.CHANNEL_ANNOUNCEMENT])

            # Ping all Test Realm Notifications members
            announcement_role_id = settings.get("spoiler_ping_role")
            if announcement_channel and announcement_role_id:
                await announcement_channel.send("<@&{role_id}>".format(role_id=announcement_role_id))

            # Embed structure to work with
            greetings_embed = Embed(title=bot_globals.spoilers_incoming_discord_title, color=Color.green())

            # Add information about Atmobot
            greetings_embed.add_field(name=bot_globals.spoilers_incoming_discord_information_title, value=bot_globals.spoilers_incoming_discord_information, inline=False)

            spoilers_channel = self.bot.get_channel(spoiler_channel_ids[bot_globals.CHANNEL_ANNOUNCEMENT]).mention
            greetings_embed.add_field(name=bot_globals.spoilers_incoming_discord_coming_soon_title, value=bot_globals.spoilers_incoming_discord_coming_soon.format(spoilers_channel=spoilers_channel), inline=False)

            images_channel = self.bot.get_channel(spoiler_channel_ids[bot_globals.CHANNEL_IMAGES]).mention
            music_channel = self.bot.get_channel(spoiler_channel_ids[bot_globals.CHANNEL_MUSIC]).mention
            locale_channel = self.bot.get_channel(spoiler_channel_ids[bot_globals.CHANNEL_LOCALE]).mention
            #formatted_channels = bot_globals.spoilers_incoming_discord_channels.format(images_channel=images_channel, music_channel=music_channel, locale_channel=locale_channel)
            #greetings_embed.add_field(name=bot_globals.spoilers_incoming_discord_channels_title, value=formatted_channels, inline=False)

            # Send the embed
            if announcement_channel:
                await announcement_channel.send(embed=greetings_embed)

        # Announce a new revision on Twitter
        if not self.twitter_post_override:

            # Grab the announcement message for Twitter
            announcement_text = settings.get("spoiler_introduction")

            # Post it to Twitter
            if announcement_text:
                media = self.twitter_api_v1.media_upload(filename = "resources/greetings_wizard.png")
                self.twitter_api_v2.create_tweet(text=announcement_text, media_ids=[media.media_id_string])

    async def post_goodbye(self):

        # Grab the goodbye message
        goodbye_text = settings.get("spoiler_closure")
        if not goodbye_text:
            return

        # Post goodbye message to Discord
        if not self.discord_post_override:

            # Discord channel to send our announcement in
            spoiler_channel_ids = settings.get("spoiler_channels")
            announcement_channel = self.bot.get_channel(spoiler_channel_ids[bot_globals.CHANNEL_ANNOUNCEMENT])

            # Send the message
            if announcement_channel:
                formatted_goodbye = "**{goodbye_text}**".format(goodbye_text=goodbye_text)
                await announcement_channel.send(formatted_goodbye)

        # Post goodbye message to Twitter
        if not self.twitter_post_override:

            # Post the goodbye message
            if goodbye_text:
                media = self.twitter_api_v1.media_upload(filename = "resources/goodbye_wizard.png")
                self.twitter_api_v2.create_tweet(text=goodbye_text, media_ids=[media.media_id_string])

        # Shut off the Discord and Twitter posts just in-case
        #self.discord_post_override = True
        #self.twitter_post_override = True

        print("{time} | SPOILERS: Update has been spoiled. Until next time".format(time=await self.bot.get_formatted_time()))

    async def notify_wad_file_update(self, delta: FileDelta):

        # We want a raw wad name
        delta_name = delta.name.replace("Data/GameData/", "").replace(".wad", "")

        # We don't care about this wad file
        if delta_name not in self.spoiler_config:
            return

        # Grab our interest config
        interest_config = self.spoiler_config.get(delta_name)

        # Grab which paths we should check
        paths_of_interest = []
        for interest in interest_config:
            interest = list(interest.values())
            interest_path = interest[bot_globals.SPOILER_FILE_PATH]
            paths_of_interest.append((interest_path, interest))

        # Iterate over all the changed files
        all_changed_files = delta.changed_inner_files + delta.created_inner_files
        for inner_file_info in all_changed_files:
            await self.handle_changed_files(inner_file_info, paths_of_interest, delta)
        #await asyncio.gather(*[self.handle_changed_files(inner_file_info, paths_of_interest, delta) for inner_file_info in all_changed_files], return_exceptions=True)

        # Now we can handle the chained files
        # Iterate over all the file directories
        all_chained_spoilers = list(self.chained_spoilers.keys())
        for chained_file_path in all_chained_spoilers:
            await self.handle_chained_files(chained_file_path)
        #await asyncio.gather(*[self.handle_chained_files(chained_file_path) for chained_file_path in all_chained_spoilers], return_exceptions=True)

    async def handle_changed_files(self, inner_file_info, paths_of_interest, delta):

        try:

            # Check if one of our paths of interest matches
            file_path = None
            config = None
            for interest_path in paths_of_interest:
                if inner_file_info.name.startswith(interest_path[0]):
                    file_path = interest_path[0]
                    config = interest_path[1]
                    break

            # We aren't a match, so continue with the next file in line
            if not file_path or not config:
                return

            # Don't process this file any further if it should be excluded
            exclusions = config[bot_globals.SPOILER_FILE_EXCLUSIONS]
            if exclusions:
                exclude_file = False
                for exclusion in exclusions:
                    if exclusion in os.path.basename(inner_file_info.name):
                        exclude_file = True
                        break

                if exclude_file:
                    return

            # Don't process this file any further if it isn't in our inclusions
            inclusions = config[bot_globals.SPOILER_FILE_INCLUSIONS]
            if inclusions:
                include_file = False
                for inclusion in inclusions:
                    if inclusion in os.path.basename(inner_file_info.name):
                        include_file = True
                        break

                if not include_file:
                    return

            # Okay, now we know this is a file we should spoil
            # Let's handle it then pass it off to one of our spoiler components

            # We are now marked as an important revision
            if not self.important_update:
                self.important_update = True
                await self.post_introduction()

            # Get the size of the file data depending on whether it's compressed
            if inner_file_info.is_compressed:
                data_size = inner_file_info.compressed_size
            else:
                data_size = inner_file_info.size

            # Determine if this has the possibility of being a chained spoiler
            chained = False
            if True:
            #if file_path.endswith("/"):

                # We may be chained
                chained = True

                # Add this file's name to the chained spoiler list
                chained_spoilers = [config]
                if file_path in self.chained_spoilers:
                    chained_spoilers = self.chained_spoilers.get(file_path)
                chained_spoilers.append(inner_file_info.name)
                self.chained_spoilers[file_path] = chained_spoilers

            # Download the file!
            file_data = await self.download_file(delta.url, data_range=(inner_file_info.file_offset, inner_file_info.file_offset + data_size))

            # Decompress if compressed
            if inner_file_info.is_compressed:
                file_data = zlib.decompress(file_data)

            # Save file into cache
            cache_path = "cache/"
            file_name = "{cache_path}/{file_name}".format(cache_path=cache_path, file_name=os.path.basename(inner_file_info.name))
            with self.safe_open_w(file_name) as fp:
                fp.write(file_data)

            # Determine file handler
            file_handler = self.determine_file_handler(inner_file_info.name)
            if file_handler == bot_globals.CHANNEL_LOCALE:
                chained = False

            # Handle the file right away
            if not chained:

                # Handle locale files
                if file_handler == bot_globals.CHANNEL_LOCALE:
                    await self.handle_locale_spoiler(spoiler_data=inner_file_info.name, config=config)

                # Handle image files
                elif file_handler == bot_globals.CHANNEL_IMAGES:
                    await self.handle_image_spoiler(spoiler_data=inner_file_info.name, config=config)

                # Handle music files
                elif file_handler == bot_globals.CHANNEL_MUSIC:
                    await self.handle_music_spoiler(spoiler_data=inner_file_info.name, config=config)

                await asyncio.sleep(bot_globals.time_between_posts)

        except Exception:
            print(traceback.format_exc())

    async def handle_chained_files(self, chained_file_path):

        try:

            chained_spoilers = self.chained_spoilers.get(chained_file_path)

            # First key is always the config
            chained_config = chained_spoilers.pop(0)

            # Determine file handler
            file_handler = self.determine_file_handler(chained_spoilers[0])

            # Create chains of 16 spoilers max
            spoiler_chains = list(self.divide_spoilers(chained_spoilers, bot_globals.spoiler_divide_amount))

            # Pass each individual chain through to their respective handlers
            total_chains = len(spoiler_chains)
            total_spoilers = len([ele for sub in spoiler_chains for ele in sub])
            for chain in spoiler_chains:

                # Chain index used for documenting our proegress with this tweet chain
                chain_index = spoiler_chains.index(chain)

                # Looks like we're by ourself, so we actually shouldn't be treated as a chain from here on out
                if len(spoiler_chains) == 1 and len(chain) == 1:
                    chain = chain.pop(0)

                # Handle image files
                if file_handler == bot_globals.CHANNEL_IMAGES:
                    await self.handle_image_spoiler(spoiler_data=chain, config=chained_config, chain_index=chain_index, total_chains=total_chains, total_spoilers=total_spoilers)

                # Handle music files
                elif file_handler == bot_globals.CHANNEL_MUSIC:
                    await self.handle_music_spoiler(spoiler_data=chain, config=chained_config, chain_index=chain_index, total_chains=total_chains, total_spoilers=total_spoilers)

                await asyncio.sleep(bot_globals.time_between_posts)

            # Remove file path from chained spoilers since we're now done with it
            del self.chained_spoilers[chained_file_path]

        except Exception:
            print(traceback.format_exc())

    @backoff.on_exception(backoff.expo, requests.exceptions.HTTPError, max_time=60)
    async def download_file(self, url, data_range):
        file_data = await self.webdriver.get_url_data(url, data_range=data_range)
        return file_data

    def determine_file_handler(self, file_name):
        file_handler = bot_globals.CHANNEL_INVALID

        file_name = file_name.lower()
        if file_name.endswith(".lang"):
            file_handler = bot_globals.CHANNEL_LOCALE
        elif file_name.endswith((".dds", ".png", ".jpg")):
            file_handler = bot_globals.CHANNEL_IMAGES
        elif file_name.endswith((".mp3", ".ogg", ".wav")):
            file_handler = bot_globals.CHANNEL_MUSIC

        return file_handler

    async def handle_locale_spoiler(self, spoiler_data, config, chain_index=-1, total_chains=-1, total_spoilers=-1):

        # Unpack our spoiler config
        spoiler_name, spoiler_file_path, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter, spoiler_divide_threshold = self.unpack_spoiler_config(config)

        # Log that we're handling a locale spoiler
        print("{time} | SPOILERS: Handling Locale spoiler with category \"{spoiler_name}\"".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # Path to our new and old locale files
        file_name = "cache/" + os.path.basename(spoiler_data)
        old_file_name = os.path.join(bot_globals.resources_path, bot_globals.locale_path, bot_globals.locale_path_old, os.path.basename(spoiler_data))

        # Open the files for comparison
        new_file = open(file_name, "r", encoding="utf8", errors='ignore')
        new_lines = new_file.readlines()
        try:
            old_file = open(old_file_name, "r", encoding="utf8", errors='ignore')
            old_lines = old_file.readlines()
        except FileNotFoundError:
            old_lines = []

        # Find the differences between the two files
        file_difference = difflib.ndiff(old_lines, new_lines)

        new_lines = []
        file_difference = tuple(x for x in file_difference)

        idx = 0
        fdiff_size = len(file_difference)
        while idx < fdiff_size:
            line = file_difference[idx]
            if line.startswith("- "):
                if idx + 1 < fdiff_size and file_difference[idx + 1].startswith("? "):
                    # this chunk is a change, so ignore this and the next 3 lines
                    idx += 4
                    continue
            elif line.startswith("+ "):
                new_lines.append(line)

            # always iterate after new item or no change
            idx += 1

        # Parse them into a nice list
        parsed_lines = []
        for line in new_lines:

            # We only care about additions
            #if not line.startswith("+ "):
            #    continue

            # Remove anything unnecessary 
            line = line.replace("+ ", "").replace("\x00", "").replace("\n", "")
            
            # Lines that are pure whitespace or digits don't matter
            # Also, we don't care about duplicates either
            if line.isspace() or line.isdigit() or (line in parsed_lines) or not line:
                continue

            parsed_lines.append(line)

        # Output path
        image_name = os.path.basename(spoiler_data).replace(".lang", ".png")
        output_path = os.path.join(bot_globals.resources_path, bot_globals.locale_path, image_name)

        # Divide our new lines up- we can't have too many in one image
        line_chains = list(self.divide_spoilers(parsed_lines, bot_globals.locale_divide_amount))

        # Handle each chain individually
        for chain in line_chains:

            chain_index = line_chains.index(chain)

            # Now to create an image showcasing all of the new locale changes
            # First, we need to open up the template image we're working with
            template_path = os.path.join(bot_globals.resources_path, bot_globals.locale_path, bot_globals.locale_template_path)
            template = Image.open(template_path)

            # Begin editing the template
            editing_template = ImageDraw.Draw(template)

            # Before anything we need to generate a header so that we know which locale file this is referencing
            # Set the font to work with
            font_path = os.path.join(bot_globals.resources_path, bot_globals.font_atmoplex)
            font_size = 72
            font = ImageFont.truetype(font_path, font_size)

            # Generate header based off of the spoiler name
            locale_title = spoiler_name.upper()

            # Calculate coordinates to place header
            width, height = editing_template.textsize(locale_title, font=font)
            x = ((bot_globals.thumbnail_dimensions[0] - width) / 2 + bot_globals.locale_header_offset_x)
            y = ((bot_globals.thumbnail_dimensions[1] - height) / 2 + bot_globals.locale_header_offset_y)

            # Place the header on template
            editing_template.text((x, y), locale_title, (239, 238, 41), font=font)

            # Now set up the font for our individual lines
            font_size = 48
            font = ImageFont.truetype(font_path, font_size)
            smaller_font_size = 40
            smaller_font = ImageFont.truetype(font_path, smaller_font_size)

            # Coordinates to begin placing our lines
            x_offset = bot_globals.locale_line_offset_x
            y_offset = bot_globals.locale_line_offset_y

            # Iterate over every line in the chain
            cutoff = (bot_globals.locale_divide_amount / 2) - 1
            for line in chain:

                # Place our line at the specified position
                font_to_use = font
                if len(line) >= 30:
                    font_to_use = smaller_font
                editing_template.text((x_offset, y_offset), line, (255, 255, 255), font=font_to_use, align="left")

                # Reset our position now that we're in the second column
                index = chain.index(line)
                if index == cutoff:
                    x_offset = bot_globals.locale_line_offset_x_secondary
                    y_offset = bot_globals.locale_line_offset_y

                # The next line should be a bit lower
                else:
                    y_offset += bot_globals.locale_line_offset_y_lower

            # We're done adding all the line, so now we can export the image
            template.save(output_path)

            # Post the spoiler to Discord if we have channel IDs
            spoiler_channel_ids = settings.get("spoiler_channels")
            if spoiler_channel_ids:

                # Only send the description a single time on Discord
                discord_post_description = spoiler_post_description
                if chain_index != 0:
                    discord_post_description = None

                await self.post_spoiler_to_discord(output_path, spoiler_name, discord_post_description, spoiler_channel_to_post, spoiler_channel_ids)

            # Tweet out the spoiler!
            if spoiler_post_to_twitter:

                # Reply to the former tweet in the chain
                in_reply_to_status_id = None
                last_tweet_id = self.last_tweet_ids.get(bot_globals.CHANNEL_LOCALE)
                if chain_index != 0 and last_tweet_id:
                    in_reply_to_status_id = last_tweet_id

                # Add counter to descriptions if the chain is more than 1 tweet
                twitter_post_description = spoiler_post_description
                if len(line_chains) > 1:
                    chain_counter = bot_globals.twitter_description_extension.format(current=(chain_index + 1), total=len(line_chains))
                    twitter_post_description = spoiler_post_description + chain_counter

                await self.post_spoiler_to_twitter([output_path], spoiler_name, bot_globals.CHANNEL_LOCALE, twitter_post_description, in_reply_to_status_id)

            await asyncio.sleep(bot_globals.time_between_posts)

        # Delete our files from cache
        if os.path.exists(file_name):
            os.remove(file_name)
        if os.path.exists(output_path):
            os.remove(output_path)
    
    async def handle_image_spoiler(self, spoiler_data, config, chain_index=-1, total_chains=-1, total_spoilers=-1):
        
        # Unpack our spoiler config
        spoiler_name, spoiler_file_path, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter, spoiler_divide_threshold = self.unpack_spoiler_config(config)

        # Log that we're handling a image spoiler
        print("{time} | SPOILERS: Handling Image spoiler - Name \"{spoiler_name}\" - Number {chain_index} in chain of length {total_chains} - DEBUG {spoiler_data}".format(time=self.get_formatted_time(), spoiler_name=spoiler_name, chain_index=chain_index, total_chains=total_chains, spoiler_data=spoiler_data))

        # We're handling a spoiler chain here
        if type(spoiler_data) == list:

            # Convert all .DDS files to .PNG
            for spoiler in spoiler_data.copy():

                # Grab index for later use
                index = spoiler_data.index(spoiler)

                # Convert to PNG and update the file name in our spoiler data
                if spoiler.endswith(".dds"):
                    file_name = await self.convert_to_png("cache/{file_name}".format(file_name=os.path.basename(spoiler)))
                    spoiler_data[index] = file_name

            # Combine images if we've reached our threshold for combination (or if we are the very last image in the chain)
            if ((len(spoiler_data) >= spoiler_divide_threshold) and spoiler_divide_threshold != -1) or ((len(spoiler_data) >= 1 and chain_index > 0) and spoiler_divide_threshold != -1):

                # Open all of the images we're going to chain together
                files_to_chain = [f for f in spoiler_data]
                images_to_chain = [Image.open("cache/{file_name}".format(file_name=os.path.basename(file_to_chain))) for file_to_chain in files_to_chain]

                # Grab the most common width and height, use them to resize images not adhering to the common size
                widths, heights = zip(*(image_to_chain.size for image_to_chain in images_to_chain))
                common_width = max(set(widths), key=widths.count)
                common_height = max(set(heights), key=heights.count)

                # Resize our images to the common size
                images_to_paste = []
                for image_to_chain in images_to_chain:
                    image_to_paste = image_to_chain.resize((common_width, common_height))
                    images_to_paste.append(image_to_paste)

                # Grab new widths and heights to determine our final image size
                widths, heights = zip(*(image_to_paste.size for image_to_paste in images_to_paste))

                # Get the width and height for our new image
                total_width = sum(widths[:4])
                max_height = sum(heights[::4])

                # Create the new image
                chained_image = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))

                # Misc data for following loop
                x_offset = 0
                y_offset = 0
                every_fourth_image = (3, 7, 11)

                # Iterate over all our images and place them into our new one
                for index in range(len(images_to_chain)):

                    image_to_paste = images_to_paste[index]

                    # Place
                    chained_image.paste(image_to_paste, (x_offset, y_offset))

                    # Increase x offset for the next one
                    x_offset += image_to_paste.size[0]

                    # Increase y offset if we need to move down a layer
                    if index in every_fourth_image:
                        x_offset = 0
                        y_offset += image_to_paste.size[1]

                    # Delete the chained image
                    image_to_chain = images_to_chain[index]
                    os.remove(image_to_chain.filename)

                # Save our new image
                chained_image_name = "cache/{spoiler_name}{chain_index}.png".format(spoiler_name=spoiler_name, chain_index=chain_index)
                chained_image.save(chained_image_name)

                # Post the spoiler to Discord if we have channel IDs
                spoiler_channel_ids = settings.get("spoiler_channels")
                if spoiler_channel_ids:

                    # Only send the description a single time on Discord
                    discord_post_description = spoiler_post_description
                    if total_chains > 1 and chain_index != 0:
                        discord_post_description = None

                    await self.post_spoiler_to_discord(chained_image_name, spoiler_name, discord_post_description, spoiler_channel_to_post, spoiler_channel_ids)

                # Tweet out the spoiler!
                if spoiler_post_to_twitter:

                    # We want to tweet out 4 images at a time, so add this to our queue of files to tweet
                    self.files_to_tweet.append(chained_image_name)

                    # Is this the last tweet in the chain?
                    last_tweet = False
                    if chain_index == total_chains - 1:
                        last_tweet = True

                    # The actual index and total chains, considering we're tweeting out 4 images at a time
                    true_chain_index = math.ceil((chain_index + 1) / bot_globals.spoilers_per_tweet) - 1
                    true_total_chains = math.ceil(total_chains / bot_globals.spoilers_per_tweet)

                    # If this is the 4th image in the tweet OR the last tweet in the chain, pump out all the images in the queue
                    if (len(self.files_to_tweet) >= bot_globals.spoilers_per_tweet) or last_tweet:

                        # Reply to the former tweet in the chain
                        in_reply_to_status_id = None
                        last_tweet_id = self.last_tweet_ids.get(bot_globals.CHANNEL_IMAGES)
                        if total_chains > bot_globals.spoilers_per_tweet and true_chain_index != 0 and last_tweet_id:
                            in_reply_to_status_id = last_tweet_id

                        # Add counter to descriptions if the chain is more than 4 images
                        twitter_post_description = spoiler_post_description
                        if total_chains > bot_globals.spoilers_per_tweet:
                            chain_counter = bot_globals.twitter_description_extension.format(current=(true_chain_index + 1), total=true_total_chains)
                            twitter_post_description = spoiler_post_description + chain_counter
                        
                        files_to_tweet = self.files_to_tweet.copy()
                        self.files_to_tweet = []
                        await self.post_spoiler_to_twitter(files_to_tweet, spoiler_name, bot_globals.CHANNEL_IMAGES, twitter_post_description, in_reply_to_status_id)

                # Delete our file from cache
                #os.remove(chained_image_name)

            else:
                
                # Iterate over the files in our spoiler data
                for file_name in spoiler_data:

                    file_index = spoiler_data.index(file_name)

                    # Format proper file name
                    file_name = "cache/" + os.path.basename(file_name)

                    # Convert .DDS files to .PNG
                    if file_name.endswith(".dds"):
                        file_name = await self.convert_to_png(file_name)

                    # Post the spoiler to Discord if we have channel IDs
                    spoiler_channel_ids = settings.get("spoiler_channels")
                    if spoiler_channel_ids:

                        # Only send the description once
                        discord_post_description = spoiler_post_description
                        if file_index != 0:
                            discord_post_description = None

                        await self.post_spoiler_to_discord(file_name, spoiler_name, discord_post_description, spoiler_channel_to_post, spoiler_channel_ids)

                    # Tweet out the spoiler!
                    if spoiler_post_to_twitter:

                        # We want to tweet out 4 images at a time, so add this to our queue of files to tweet
                        self.files_to_tweet.append(file_name)

                        # Is this the last tweet in the chain?
                        last_tweet = False
                        if file_index == len(spoiler_data) - 1:
                            last_tweet = True

                        # The actual index and total chains, considering we're tweeting out 4 images at a time
                        true_chain_index = math.ceil(chain_index / bot_globals.spoilers_per_tweet) - 1
                        true_total_chains = math.ceil(total_chains / bot_globals.spoilers_per_tweet)

                        # If this is the 4th image in the tweet OR the last tweet in the chain, pump out all the images in the queue
                        if (len(self.files_to_tweet) >= bot_globals.spoilers_per_tweet) or last_tweet:

                            # Reply to the former tweet in the chain
                            # We know if we should reply if:
                            # 1. Our spoiler index is greater than the amount allowed in a single tweet
                            # or
                            # 2. We are not the first chain in the cycle 
                            # And, of course, a last_tweet_id has to exist so we have something to reply to
                            in_reply_to_status_id = None
                            last_tweet_id = self.last_tweet_ids.get(bot_globals.CHANNEL_IMAGES)
                            if ((file_index >= bot_globals.spoilers_per_tweet) or (chain_index > 0)) and last_tweet_id:
                                in_reply_to_status_id = last_tweet_id

                            # Add counter to descriptions if we're making multiple tweets
                            # We know if we should add a counter if:
                            # 1. There is more than 1 chain in the cycle
                            # or
                            # 2. We have more spoilers than the amount allowed in a single tweet
                            twitter_post_description = spoiler_post_description
                            if (total_chains > 1) or (len(spoiler_data) > bot_globals.spoilers_per_tweet):
                                if (total_chains > 1):
                                    current = ((chain_index) * bot_globals.spoilers_per_tweet) + math.ceil((file_index + 1) / bot_globals.spoilers_per_tweet)
                                    total = ((total_chains - 1) * bot_globals.spoilers_per_tweet) + math.ceil(len(spoiler_data) / bot_globals.spoilers_per_tweet)
                                else:
                                    current = math.ceil((file_index + 1) / bot_globals.spoilers_per_tweet)
                                    total = math.ceil(len(spoiler_data) / bot_globals.spoilers_per_tweet)
                                chain_counter = bot_globals.twitter_description_extension.format(current = current, total = total)
                                twitter_post_description = spoiler_post_description + chain_counter

                            files_to_tweet = self.files_to_tweet.copy()
                            self.files_to_tweet = []
                            await self.post_spoiler_to_twitter(files_to_tweet, spoiler_name, bot_globals.CHANNEL_IMAGES, twitter_post_description, in_reply_to_status_id)

                    # Delete our file from cache
                    #os.remove(file_name)

                    await asyncio.sleep(bot_globals.time_between_posts)

        # Otherwise we're spoiling a single file
        else:

            # Format proper file name
            file_name = "cache/" + os.path.basename(spoiler_data)

            # Convert .DDS files to .PNG
            if spoiler_data.endswith(".dds"):
                file_name = await self.convert_to_png(file_name)

            # Post the spoiler to Discord if we have channel IDs
            spoiler_channel_ids = settings.get("spoiler_channels")
            if spoiler_channel_ids:
                await self.post_spoiler_to_discord(file_name, spoiler_name, spoiler_post_description, spoiler_channel_to_post, spoiler_channel_ids)

            # Tweet out the spoiler!
            if spoiler_post_to_twitter:
                await self.post_spoiler_to_twitter([file_name], spoiler_name, bot_globals.CHANNEL_IMAGES, spoiler_post_description)

            # Delete our file from cache
            #os.remove(file_name)

    async def handle_music_spoiler(self, spoiler_data, config, chain_index=-1, total_chains=-1, total_spoilers=-1):

        # Unpack our spoiler config
        spoiler_name, spoiler_file_path, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter, spoiler_divide_threshold = self.unpack_spoiler_config(config)

        # Log that we're handling a music spoiler
        print("{time} | SPOILERS: Handling Music spoiler with category \"{spoiler_name}\"".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # We're handling a spoiler chain here
        if type(spoiler_data) == list:

            # Iterate over the files in our spoiler data
            for file_name in spoiler_data:

                file_index = spoiler_data.index(file_name)

                # Format proper file name
                new_file_name = "cache/" + os.path.basename(file_name)

                # Post the spoiler to Discord if we have channel IDs
                spoiler_channel_ids = settings.get("spoiler_channels")
                if spoiler_channel_ids:

                    # Only send the description once
                    discord_post_description = spoiler_post_description
                    if file_index != 0:
                        discord_post_description = None

                    await self.post_spoiler_to_discord(new_file_name, spoiler_name, discord_post_description, spoiler_channel_to_post, spoiler_channel_ids)

                    # Tweet out the spoiler!
                    if spoiler_post_to_twitter:

                        # Add counter to descriptions if the chain is more than 1 tweet
                        twitter_post_description = spoiler_post_description
                        current_chain_index = (chain_index * bot_globals.spoiler_divide_amount) + file_index
                        chain_counter = bot_globals.twitter_description_extension.format(current=current_chain_index + 1, total=total_spoilers)
                        twitter_post_description = spoiler_post_description + chain_counter

                        # Generate video path
                        video_path = os.path.join(bot_globals.resources_path, bot_globals.video_path, os.path.basename(new_file_name).replace(".ogg", ".mp4"))

                        # All links in the chain should start out as NOT READY, except for the very first
                        current_status = bot_globals.CHAIN_STATUS_NOT_READY
                        if file_index == 0 and chain_index == 0:
                            current_status = bot_globals.CHAIN_STATUS_WAITING

                        # Create an entry for our spoiler name if it doesn't already exist
                        if not self.chained_tweet_status.get(spoiler_name):
                            self.chained_tweet_status[spoiler_name] = {}

                        # Add info regarding this link of the chain
                        self.chained_tweet_status[spoiler_name][current_chain_index] = [current_status, [video_path, spoiler_name, twitter_post_description]]
                        
                        # Thread the creation of the video- it'll take a while so we don't want it to hold us up
                        spoiler_parent_directory = os.path.dirname(file_name)
                        p = threading.Thread(target=self.create_twitter_video, args=(new_file_name, spoiler_name, twitter_post_description, spoiler_parent_directory, current_chain_index))
                        p.start()

                # Delete our file from cache
                # We deal with the file later if posted to Twitter
                if not spoiler_post_to_twitter:
                    os.remove(file_name)

                time_between_posts = bot_globals.time_between_posts
                if spoiler_post_to_twitter:
                    time_between_posts = 3.0
                await asyncio.sleep(time_between_posts)

        # Otherwise we're spoiling a single file
        else:

            # Format proper file name
            if total_chains == 1:
                file_name = "cache/" + os.path.basename(spoiler_data)
            else:
                file_name = "cache/" + os.path.basename(spoiler_data)

            # Post the spoiler to Discord if we have channel IDs
            # TODO: Add check to make sure that the song being sent isn't more than 8 MB, otherwise compress it

            try:

                spoiler_channel_ids = settings.get("spoiler_channels")
                if spoiler_channel_ids:
                    await self.post_spoiler_to_discord(file_name, spoiler_name, spoiler_post_description, spoiler_channel_to_post, spoiler_channel_ids)

            except:

                pass

            # Create a video and post it to twitter
            if spoiler_post_to_twitter:

                # Thread the creation of the video- it'll take a while so we don't want it to hold us up
                spoiler_parent_directory = os.path.dirname(spoiler_data)
                p = threading.Thread(target=self.create_twitter_video, args=(file_name, spoiler_name, spoiler_post_description, spoiler_parent_directory))
                p.start()

            else:

                # Delete our file from cache
                os.remove(file_name)

    def create_twitter_video(self, file_name, spoiler_name, spoiler_post_description, spoiler_parent_directory, current_chain_index=-1):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.ready_twitter_video(file_name, spoiler_name, spoiler_post_description, spoiler_parent_directory, current_chain_index))
        loop.close()

    async def ready_twitter_video(self, file_name, spoiler_name, spoiler_post_description, spoiler_parent_directory, current_chain_index=-1):

        # Generate video path
        video_path = os.path.join(bot_globals.resources_path, bot_globals.video_path, os.path.basename(file_name).replace(".ogg", ".mp4"))

        # Render out a video if we don't already have it saved
        #if os.path.exists(video_path):
        #    success = True
        #else:
        success, title, shortened = await self.create_music_video(file_name, spoiler_parent_directory)

        # Add the title of the track to the description
        spoiler_post_description += "\n\n" + title

        # If we're shortened, add that to the description
        if shortened:
            spoiler_post_description += bot_globals.video_overtime_description

        ready = current_chain_index == -1

        # Grab chain info if we're part of a chain
        if current_chain_index != -1:
            chain_status = self.chained_tweet_status.get(spoiler_name)
            current_link_data = chain_status.get(current_chain_index)
            current_status = current_link_data[bot_globals.LINK_DATA_STATUS]
            ready = current_status == bot_globals.CHAIN_STATUS_WAITING

        # Post videos right away if they're un-chained or ready
        if ready:

            # Only post if the render was successful
            if success:

                # Post on Twitter
                await self.post_twitter_video(video_path, spoiler_name, spoiler_post_description, current_chain_index)

                # Delete the file
                #os.remove(video_path)

            return

        # See if we're allowed to post the next video in our chain
        # We should wait until the prior one has finished uploading to Twitter
        # Grab info for the previous link in the chain
        previous_link_data = chain_status.get(current_chain_index - 1)
        previous_status = previous_link_data[bot_globals.LINK_DATA_STATUS]
        current_config = current_link_data[bot_globals.LINK_DATA_CONFIG]

        # Save new description if shortened
        #if shortened:
        current_config[bot_globals.LINK_CONFIG_DESCRIPTION] = spoiler_post_description
        current_link_data[bot_globals.LINK_DATA_CONFIG] = current_config
        chain_status[current_chain_index] = current_link_data
        self.chained_tweet_status[spoiler_name] = chain_status

        # We aren't ready yet
        if (success and previous_status != bot_globals.CHAIN_STATUS_COMPLETE) or self.delay_music:

            # Put us in a waiting state
            current_link_data[bot_globals.LINK_DATA_STATUS] = bot_globals.CHAIN_STATUS_WAITING
            chain_status[current_chain_index] = current_link_data
            self.chained_tweet_status[spoiler_name] = chain_status
            return

        # We're ready to Tweet it out
        elif success and previous_status == bot_globals.CHAIN_STATUS_COMPLETE:

            await self.post_twitter_video(*current_config, current_chain_index=current_chain_index, reply_to_status=True)

    async def post_twitter_video(self, video_path, spoiler_name, spoiler_post_description, current_chain_index, reply_to_status=False):

        # Grab last tweet ID if we need it
        in_reply_to_status_id = None
        if reply_to_status:
            in_reply_to_status_id = self.last_tweet_ids[bot_globals.CHANNEL_MUSIC]

        # Post the tweet
        await self.post_spoiler_to_twitter([video_path], spoiler_name, bot_globals.CHANNEL_MUSIC, spoiler_post_description, in_reply_to_status_id)

        # Delete the file
        #os.remove(video_path)

        if current_chain_index != -1:

            # Grab info for the current and next link in the chain
            chain_status = self.chained_tweet_status.get(spoiler_name)
            current_link_data = chain_status.get(current_chain_index)
            next_link_data = chain_status.get(current_chain_index + 1)

            # Mark our link as complete
            current_link_data[bot_globals.LINK_DATA_STATUS] = bot_globals.CHAIN_STATUS_COMPLETE
            chain_status[current_chain_index] = current_link_data
            self.chained_tweet_status[spoiler_name] = chain_status

            # The next video in the chain is ready to be posted
            if next_link_data:
                ready, config = next_link_data
                if ready == bot_globals.CHAIN_STATUS_WAITING:
                    await self.post_twitter_video(*config, current_chain_index + 1, True)

            # We are the last video, so this music chain is now complete
            else:

                # Clear this from the chained tweet info
                if self.chained_tweet_status.get(spoiler_name):
                    del self.chained_tweet_status[spoiler_name]

                # If all of our chains have completed and the goodbye is ready for posting, then post it
                if not self.chained_tweet_status and self.goodbye_pending:
                    await self.post_goodbye()

    async def create_music_video(self, file_name, spoiler_parent_directory=None):

        abbreviated_file_name = os.path.basename(file_name)

        print("{time} | SPOILERS: Generating video from file name \"{spoiler_name}\"".format(time=self.get_formatted_time(), spoiler_name=abbreviated_file_name))

        # Grab world prefix from file name
        world_prefix = abbreviated_file_name[:abbreviated_file_name.index("_")]

        # Format header and footer based on file name
        thumbnail_header = re.sub(r'\d+', '', re.sub('([A-Z])', r' \1', abbreviated_file_name.replace("{world_prefix}_".format(world_prefix=world_prefix), "").replace("_", "").replace(".ogg", "")))
        thumbnail_footer = bot_globals.prefix_to_world.get(world_prefix, "")

        # Fallback header if we still don't have one
        if not thumbnail_footer:
            thumbnail_footer = re.sub(r"(\w)([A-Z])", r"\1 \2", spoiler_parent_directory).split('/', 1)[-1]

        # Create a thumbnail for the video
        await self.create_video_thumbnail(file_name=abbreviated_file_name, thumbnail_header=thumbnail_header.upper(), thumbnail_footer=thumbnail_footer.upper())

        # Load audio
        audio_clip = AudioFileClip(file_name)
        duration = audio_clip.duration

        # Shorten longer tracks because Twitter does not allow them
        shortened = False
        total_duration = duration + 0.5
        if total_duration > bot_globals.twitter_video_limit:
            shortened = True
            total_duration = bot_globals.twitter_video_limit - 1

        new_audioclip = CompositeAudioClip([audio_clip])

        # Create a video using the thumbnail
        my_clip = ImageClip(os.path.join(bot_globals.resources_path, bot_globals.video_path, bot_globals.thumbnail_output_path.format(file_name=abbreviated_file_name)))
        my_clip = my_clip.resize(height=bot_globals.video_dimension)

        # Apply the audio clip
        my_clip = my_clip.set_audio(new_audioclip)
        my_clip = my_clip.set_duration(total_duration)

        # Fade out audio if we had to trim our audio earlier
        if shortened:
            my_clip = my_clip.audio_fadeout(bot_globals.video_fade_duration)

        # Write to file
        my_clip.write_videofile(os.path.join(bot_globals.resources_path, bot_globals.video_path, os.path.basename(file_name).replace(".ogg", ".mp4")), fps=24, audio_codec="aac", logger=None, threads=4)

        # Delete our audio file from cache
        my_clip.close()
        audio_clip.close()
        new_audioclip.close()
        os.remove(file_name)

        # Log and acknowledge success
        print("{time} | SPOILERS: Exported video from file name \"{spoiler_name}\"".format(time=self.get_formatted_time(), spoiler_name=abbreviated_file_name))

        return True, thumbnail_header, shortened

    async def create_video_thumbnail(self, file_name, thumbnail_header, thumbnail_footer, thumb_type=None):

        # If no thumbnail type was provided, use Wizard101
        if not thumb_type:
            thumb_id = 0
            thumb_type = bot_globals.game_longhands.get(thumb_id)

        # Info to help craft the thumbnail for this particular type
        thumb_info = bot_globals.command_thumbnail_extras.get(thumb_type)
        
        # File path for the template we're going to load
        template_name = bot_globals.thumbnail_template_name.format(thumb_type=thumb_info[bot_globals.COMMAND_THUMBNAIL_NAME])
        template_path = os.path.join(bot_globals.resources_path, bot_globals.video_path, template_name)
        template = Image.open(template_path)

        # Begin editing the template
        editing_template = ImageDraw.Draw(template)

        # Set the font to work with
        font_name = thumb_info[bot_globals.COMMAND_THUMBNAIL_FONT]
        font_size = thumb_info[bot_globals.COMMAND_THUMBNAIL_FONT_SIZE]
        font_path = os.path.join(bot_globals.resources_path, font_name)
        font = ImageFont.truetype(font_path, font_size)

        # Offset and color info
        thumbnail_offsets = (thumb_info[bot_globals.COMMAND_THUMBNAIL_HEADER_OFFSET], thumb_info[bot_globals.COMMAND_THUMBNAIL_FOOTER_OFFSET])
        thumbnail_colors = (thumb_info[bot_globals.COMMAND_THUMBNAIL_HEADER_COLOR], thumb_info[bot_globals.COMMAND_THUMBNAIL_FOOTER_COLOR])

        # Place both our header and footer
        text_pieces = (thumbnail_header, thumbnail_footer)
        for text_to_place in text_pieces:

            # Index
            index = text_pieces.index(text_to_place)

            # Set x and y coordinates
            width, height = editing_template.textsize(text_to_place, font=font)
            offsetX = thumb_info[bot_globals.COMMAND_THUMBNAIL_X_OFFSET]
            if offsetX:
                x = offsetX
            else:
                x = (bot_globals.thumbnail_dimensions[0] - width) / 2
            offsetY = thumbnail_offsets[index]
            y = ((bot_globals.thumbnail_dimensions[1] - height) / 2 + offsetY)

            # Grab text color
            color = thumbnail_colors[index]

            # Place the text
            editing_template.text((x, y), text_to_place, color, font=font)

        # Save the thumbnail
        output_path = os.path.join(bot_globals.resources_path, bot_globals.video_path, bot_globals.thumbnail_output_path.format(file_name=file_name))
        template.save(output_path)

    def unpack_spoiler_config(self, config):

        spoiler_name = config[bot_globals.SPOILER_NAME]
        spoiler_file_path = config[bot_globals.SPOILER_FILE_PATH]
        spoiler_channel_to_post = config[bot_globals.SPOILER_CHANNEL_TO_POST]
        spoiler_post_description = config[bot_globals.SPOILER_POST_DESCRIPTION]
        spoiler_post_to_twitter = config[bot_globals.SPOILER_POST_TO_TWITTER]
        spoiler_divide_threshold = config[bot_globals.SPOILER_DIVIDE_THRESHOLD]

        return spoiler_name, spoiler_file_path, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter, spoiler_divide_threshold

    def divide_spoilers(self, l, n):
        for i in range(0, len(l), n): 
            yield l[i:i + n]

    async def convert_to_png(self, file_name):
        old_file_name = file_name
        file_name = file_name.replace(".dds", ".png")

        image_conversion = Image.open(old_file_name)
        image_conversion.save(file_name)

        os.remove(old_file_name)

        # Return our new file name
        return file_name

    async def post_spoiler_to_discord(self, file_name, spoiler_name, spoiler_post_description, spoiler_channel_to_post, spoiler_channel_ids):

        if self.discord_post_override:
            return

        # Find which channel to post our spoiler to
        discord_channel_id = spoiler_channel_ids[spoiler_channel_to_post]
        discord_channel = self.bot.get_channel(discord_channel_id)

        # Format description
        if spoiler_post_description:
            spoiler_post_description = "**{description}**".format(description=spoiler_post_description)

        # Send our spoiler!
        file_to_send = File(file_name)

        if spoiler_post_description:
            await discord_channel.send(spoiler_post_description, file=file_to_send)
        else:
            await discord_channel.send(file=file_to_send)

        # Log it
        print("{time} | SPOILERS: Posted spoiler \"{spoiler_name}\" on Discord".format(time=self.get_formatted_time(), spoiler_name=os.path.basename(file_name)))

    async def post_spoiler_to_twitter(self, file_names, spoiler_name, spoiler_type, spoiler_post_description=None, in_reply_to_status_id=None):

        if self.twitter_post_override:
            return

        media_ids = []
        
        # Format description
        twitter_description = ""
        if spoiler_post_description:
            twitter_description += self.format_twitter_description(spoiler_post_description)

        for file_name in file_names:

            # Handle uploading MP4s
            if file_name.endswith(".mp4"):
                video = self.twitter_api_v1.media_upload(filename = file_name, media_category = 'tweet_video')

                # Sleep so that our uploaded video has some time to process
                # We're using time.sleep() here because asyncio.sleep() doesn't work in a thread
                time.sleep(bot_globals.twitter_video_process_time)

                media_ids.append(video.media_id_string)
                continue

            media = self.twitter_api_v1.media_upload(filename = file_name)
            media_ids.append(media.media_id_string)

        # Publish the tweet
        status = self.twitter_api_v2.create_tweet(text=twitter_description, in_reply_to_tweet_id=in_reply_to_status_id, media_ids=media_ids)

        # Store the ID of the last tweet made
        self.last_tweet_ids[spoiler_type] = status.data['id']

        # Tweet logging
        for x in range(len(media_ids)):
            spoiler_name = file_names[x]
            print("{time} | SPOILERS: Tweeted spoiler \"{spoiler_name}\"".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))
        return

    def format_twitter_description(self, description, current=1, total=1):

        # Format description
        twitter_description = bot_globals.twitter_description_format.format(description=description)

        # Show if we're on a tweet chain
        if total > 1:
            twitter_description += bot_globals.twitter_description_extension.format(current=current, total=total)

        return twitter_description

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    def safe_open_w(self, path):
        self.mkdir_p(os.path.dirname(path))
        return open(path, 'wb+')

    async def text_compare_demo(self):

        # Open our old and new file
        file1 = open("resources/locale/QuestTitleOld.lang", "r")
        file2 = open("resources/locale/QuestTitleNew.lang", "r")

        # Find the differences
        diff = difflib.ndiff(file1.readlines(), file2.readlines())

        # Parse the differences into a nice list
        new_zones = []
        for line in diff:

            # We only care about additions
            if not line.startswith("+ "):
                continue

            # Remove anything unnecessary 
            line = line.replace("+ ", "")
            line = line.replace("\x00", "")
            line = line.replace("\n", "")
            
            # Whitespace additions don't matter
            if line.isspace() or not line:
                continue

            # Nor do digits
            if line.isdigit():
                continue

            if line in new_zones:
                continue

            new_zones.append(line)

        # Open our template
        template_path = os.path.join(bot_globals.resources_path, bot_globals.locale_path, bot_globals.locale_template_path)
        template = Image.open(template_path)

        # Begin editing the template
        editing_template = ImageDraw.Draw(template)

        # Set the font to work with
        font_path = os.path.join(bot_globals.resources_path, bot_globals.font_atmoplex)
        font = ImageFont.truetype(font_path, 84)
        x_offset = 532
        y_offset = 454
        color = (239, 238, 41)
        locale_title = "QUEST TITLES"
        width, height = editing_template.textsize(locale_title, font=font)
        x = ((1920 - width) / 2 + x_offset)
        y = ((1080 - height) / 2 + y_offset)

        editing_template.text((x, y), locale_title, color, font=font)

        font = ImageFont.truetype(font_path, 48)
        x_offset = 250
        y_offset = 175
        color = (255, 255, 255)
        for line in new_zones[:12]:

            index = new_zones.index(line)

            width, height = editing_template.textsize(line, font=font)

            editing_template.text((x_offset, y_offset), line, color, font=font, align="left")

            y_offset += 125

            if index == 5:
                y_offset = 175
                x_offset += 825

        # Save our thumbnail
        output_path = os.path.join(bot_globals.resources_path, bot_globals.locale_path, "locale_test.png")
        template.save(output_path)

    async def wad_download_demo(self):

        revision = settings.get("latest_revision")
        discord_channel = self.bot.get_channel(814900537966329936)

        await discord_channel.send("Starting up! Please wait, this may take a few seconds.")

        # Downloading the wad
        opener = urllib.request.URLopener()
        opener.addheader('User-Agent', 'Mozilla/5.0')
        file_name, headers = opener.retrieve("http://patch.us.wizard101.com/WizPatcher/V_{revision}/LatestBuild/Data/GameData/Root.wad".format(revision=revision), "archive/{revision}/_Wads/Root.wad".format(revision=revision))

        print("done wad download!")
        await discord_channel.send("Second stage done! The next may take around 30 seconds.")

        # Unpacking wads
        #root_wad = Wad(path="archive/{revision}/_Wads/Root.wad".format(revision=revision))
        await root_wad.open()

        await root_wad.unarchive("archive/{revision}/Root".format(revision=revision))

        print("done unpack!")
        await discord_channel.send("Third stage done! We're almost done here...")

        # Converting DDS to PNG
        image_path = "archive/{revision}/Root/GUI/DeckConfig/Spell_Complete_Color16.dds".format(revision=revision)
        deck_config = Image.open(image_path)

        if not os.path.exists("archive/{revision}/_FilesOfInterest".format(revision=revision)):
            os.mkdir("archive/{revision}/_FilesOfInterest".format(revision=revision))

        save_path = "archive/{revision}/_FilesOfInterest/Spell_Complete_Color16.png".format(revision=revision)
        deck_config.save(save_path)

        print("done conversion!")

        # Sending the image to a channel
        print("channel is {} and bot is {}".format(discord_channel, self.bot))
        file_to_send = File(save_path)
        await discord_channel.send(file=file_to_send)
        print("image sent!")

        await discord_channel.send("There we go!")
