# 3rd-Party Packages
from time import sleep, time
import discord
from PIL import Image
from discord import file
from discord.ext.commands import bot
import nest_asyncio
import twitter
from wizdiff.delta import FileDelta
from wizdiff.update_notifier import UpdateNotifier
from wizdiff.utils import get_revision_from_url
from wizwalker.file_readers.wad import Wad

# Local packages
import bot_globals

# Built-in packages
import asyncio
import errno
import datetime
import json
import os
import threading
import time
import urllib.request
import zlib

# Spoilers
class Spoilers(UpdateNotifier):

    def __init__(self, bot):

        UpdateNotifier.__init__(self)
        
        self.bot = bot
        self.twitter_api = None

        self.spoiler_config = {}
        self.chained_spoilers = {}

        self.last_tweet_id = 0

        self.discord_post_override = False
        self.twitter_post_override = False

    async def startup(self):

        nest_asyncio.apply()

        # Load our spoilers config
        self.load_spoilers()
        
        # Log into our Twitter account so we can post stuff later
        print("{time} | SPOILERS: Logging into the Twitter API".format(time=await self.bot.get_formatted_time()))
        twitter_api_keys = self.bot.bot_settings.get("twitter_api_keys")
        if twitter_api_keys:

            # Grab keys from the settings
            consumer_key = twitter_api_keys[bot_globals.TWITTER_KEY_CONSUMER]
            consumer_secret = twitter_api_keys[bot_globals.TWITTER_KEY_CONSUMER_SECRET]
            access_token_key = twitter_api_keys[bot_globals.TWITTER_KEY_ACCESS_TOKEN]
            access_token_secret = twitter_api_keys[bot_globals.TWITTER_KEY_ACCESS_TOKEN_SECRET]

            # Load the API
            self.twitter_api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)

        # Check if we're logged in and verified
        if self.twitter_api:
            verified = self.twitter_api.VerifyCredentials()

        # Notify about the API
        if not self.twitter_api or not verified:
            print("{time} | SPOILERS: Could not load the Twitter API".format(time=self.get_formatted_time()))
        else:
            print("{time} | SPOILERS: Logged into the Twitter API".format(time=self.get_formatted_time()))

        # Get a new revision for testing purposes
        # TODO: Remove later
        file_list_url, base_url = self.webdriver.get_patch_urls()
        revision = get_revision_from_url(file_list_url)
        self.new_revision(revision, file_list_url, base_url)

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

    def notify_wad_file_update(self, delta: FileDelta):

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
                continue

            # Okay, now we know this is a file we should spoil
            # Let's handle it then pass it off to one of our spoiler components

            # Get the size of the file data depending on whether it's compressed
            if inner_file_info.is_compressed:
                data_size = inner_file_info.compressed_size
            else:
                data_size = inner_file_info.size

            # Determine if this is a chained spoiler
            chained = False
            if file_path.endswith("/"):

                # We're chained
                chained = True

                # Add this file's name to the chained spoiler list
                chained_spoilers = [config]
                if file_path in self.chained_spoilers:
                    chained_spoilers = self.chained_spoilers.get(file_path)
                chained_spoilers.append(inner_file_info.name)
                self.chained_spoilers[file_path] = chained_spoilers

            # Download the file!
            file_data = self.webdriver.get_url_data(delta.url, data_range=(inner_file_info.file_offset, inner_file_info.file_offset + data_size))

            # Decompress if compressed
            if inner_file_info.is_compressed:
                file_data = zlib.decompress(file_data)

            # Save file into cache
            cache_path = "cache/"
            if chained:
                cache_path += "chained/"
            file_name = "{cache_path}/{file_name}".format(cache_path=cache_path, file_name=os.path.basename(inner_file_info.name))
            with self.safe_open_w(file_name) as fp:
                fp.write(file_data)

            # Handle the file right away
            if not chained:

                # Determine file handler
                file_handler = self.determine_file_handler(inner_file_info.name)

                # Handle locale files
                if file_handler == bot_globals.CHANNEL_LOCALE:
                    self.handle_locale_spoiler(spoiler_data=inner_file_info.name, config=config)

                # Handle image files
                elif file_handler == bot_globals.CHANNEL_IMAGES:
                    self.handle_image_spoiler(spoiler_data=inner_file_info.name, config=config)

                # Handle music files
                elif file_handler == bot_globals.CHANNEL_MUSIC:
                    self.handle_music_spoiler(spoiler_data=inner_file_info.name, config=config)

                time.sleep(bot_globals.time_between_posts)

        # Now we can handle the chained files
        # Iterate over all the file directories
        for chained_file_path in list(self.chained_spoilers.keys()):

            # Reset our last tweet ID for sanity purposes
            self.last_tweet_id = None

            chained_spoilers = self.chained_spoilers.get(chained_file_path)

            # First key is always the config
            chained_config = chained_spoilers.pop(0)

            # Determine file handler
            file_handler = self.determine_file_handler(chained_spoilers[0])

            # Create chains of 16 spoilers max
            spoiler_chains = list(self.divide_spoilers(chained_spoilers, bot_globals.spoiler_divide_amount))

            # Pass each individual chain through to their respective handlers
            total_chains = len(spoiler_chains)
            for chain in spoiler_chains:

                # Chain index used for documenting our proegress with this tweet chain
                chain_index = spoiler_chains.index(chain)
    
                # Handle locale files
                if file_handler == bot_globals.CHANNEL_LOCALE:
                    self.handle_locale_spoiler(spoiler_data=chain, config=chained_config, chain_index=chain_index, total_chains=total_chains)

                # Handle image files
                elif file_handler == bot_globals.CHANNEL_IMAGES:
                    self.handle_image_spoiler(spoiler_data=chain, config=chained_config, chain_index=chain_index, total_chains=total_chains)

                # Handle music files
                elif file_handler == bot_globals.CHANNEL_MUSIC:
                    self.handle_music_spoiler(spoiler_data=chain, config=chained_config, chain_index=chain_index, total_chains=total_chains)

                time.sleep(bot_globals.time_between_posts)

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

    def handle_locale_spoiler(self, spoiler_data, config, chain_index=-1, total_chains=-1):
        return
    
    def handle_image_spoiler(self, spoiler_data, config, chain_index=-1, total_chains=-1):
        
        # Unpack our spoiler config
        spoiler_name, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter = self.unpack_spoiler_config(config)

        # Log that we're handling a music spoiler
        print("{time} | SPOILERS: Handling Image spoiler with name of {spoiler_name}".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # We're handling a spoiler chain here
        if type(spoiler_data) == list:

            # Convert all .DDS files to .PNG
            for spoiler in spoiler_data.copy():

                # Grab index for later use
                index = spoiler_data.index(spoiler)

                # Convert to PNG and update the file name in our spoiler data
                if spoiler.endswith(".dds"):
                    file_name = self.convert_to_png("cache/chained/{file_name}".format(file_name=os.path.basename(spoiler)))
                    spoiler_data[index] = file_name

            # If we have 5 or more images in the chain, we want to combine them
            # Another use case is if we're already part of a chain that has combined images
            # In which case, we'll allow for the combination of less than 5 for consistency purposes
            if (len(spoiler_data) >= bot_globals.spoiler_divide_threshold) or (len(spoiler_data) > 1 and chain_index > 0):

                # Open all of the images we're going to chain together
                files_to_chain = [f for f in spoiler_data]
                images_to_chain = [Image.open(file_to_chain) for file_to_chain in files_to_chain]

                # Grab their widths and heights to determine our final image size
                widths, heights = zip(*(image_to_chain.size for image_to_chain in images_to_chain))

                # Get the width and height for our new image
                total_width = sum(widths[:4])
                max_height = sum(heights[::4])

                # Create the new image
                chained_image = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))

                # Misc data for following loop
                x_offset = 0
                y_offset = 0
                every_fourth_image = [3, 7, 11]

                # Iterate over all our images and place them into our new one
                for image_to_chain in images_to_chain:

                    # Place
                    chained_image.paste(image_to_chain, (x_offset, y_offset))

                    # Increase x offset for the next one
                    x_offset += image_to_chain.size[0]

                    # Increase y offset if we need to move down a layer
                    index = images_to_chain.index(image_to_chain)
                    if index in every_fourth_image:
                        x_offset = 0
                        y_offset += image_to_chain.size[1]

                # Save our new image
                chained_image_name = "cache/chained/{spoiler_name}{chain_index}.png".format(spoiler_name=spoiler_name, chain_index=chain_index)
                chained_image.save(chained_image_name)

                # Post the spoiler to Discord if we have channel IDs
                spoiler_channel_ids = self.bot.bot_settings.get("spoiler_channel_ids")
                if spoiler_channel_ids:

                    # Only send the description a single time on Discord
                    discord_post_description = spoiler_post_description
                    if total_chains > 1 and chain_index != 0:
                        discord_post_description = None

                    self.post_spoiler_to_discord(chained_image_name, spoiler_name, discord_post_description, spoiler_channel_to_post, spoiler_channel_ids)

                # Tweet out the spoiler!
                if spoiler_post_to_twitter:

                    # Reply to the former tweet in the chain
                    in_reply_to_status_id = None
                    if total_chains > 1 and chain_index != 0 and self.last_tweet_id:
                        in_reply_to_status_id = self.last_tweet_id

                    # Add counter to descriptions if the chain is more than 1 tweet
                    twitter_post_description = spoiler_post_description
                    if total_chains > 1:
                        chain_counter = bot_globals.twitter_description_extension.format(current=(chain_index + 1), total=total_chains)
                        twitter_post_description = spoiler_post_description + chain_counter
                    
                    self.post_spoiler_to_twitter(chained_image_name, spoiler_name, twitter_post_description, in_reply_to_status_id)

                # Delete our file from cache
                os.remove(chained_image_name)

            # With 4 or less images, we tweet them out individually and just reply in a chain
            else:
                
                # Iterate over the files in our spoiler data
                for file_name in spoiler_data:

                    file_index = spoiler_data.index(file_name)

                    # Format proper file name
                    file_name = "cache/chained/" + os.path.basename(file_name)

                    # Convert .DDS files to .PNG
                    if file_name.endswith(".dds"):
                        file_name = self.convert_to_png(file_name)

                    # Post the spoiler to Discord if we have channel IDs
                    spoiler_channel_ids = self.bot.bot_settings.get("spoiler_channel_ids")
                    if spoiler_channel_ids:

                        # Only send the description once
                        discord_post_description = spoiler_post_description
                        if file_index != 0:
                            discord_post_description = None

                        self.post_spoiler_to_discord(file_name, spoiler_name, discord_post_description, spoiler_channel_to_post, spoiler_channel_ids)

                    # Tweet out the spoiler!
                    if spoiler_post_to_twitter:

                        # Reply to the former tweet in the chain
                        in_reply_to_status_id = None
                        if file_index != 0:
                            in_reply_to_status_id = self.last_tweet_id

                        # Add counter to descriptions if the chain is more than 1 tweet
                        twitter_post_description = spoiler_post_description
                        if len(spoiler_data) > 1:
                            chain_counter = bot_globals.twitter_description_extension.format(current=(file_index + 1), total=len(spoiler_data))
                            twitter_post_description = spoiler_post_description + chain_counter

                        self.post_spoiler_to_twitter(file_name, spoiler_name, twitter_post_description, in_reply_to_status_id)

                    # Delete our file from cache
                    os.remove(file_name)

        # Otherwise we're spoiling a single file
        else:

            # Format proper file name
            file_name = "cache/" + os.path.basename(spoiler_data)

            # Convert .DDS files to .PNG
            if spoiler_data.endswith(".dds"):
                file_name = self.convert_to_png(file_name)

            # Post the spoiler to Discord if we have channel IDs
            spoiler_channel_ids = self.bot.bot_settings.get("spoiler_channel_ids")
            if spoiler_channel_ids:
                self.post_spoiler_to_discord(file_name, spoiler_name, spoiler_post_description, spoiler_channel_to_post, spoiler_channel_ids)

            # Tweet out the spoiler!
            if spoiler_post_to_twitter:
                self.post_spoiler_to_twitter(file_name, spoiler_name, spoiler_post_description)

            # Delete our file from cache
            os.remove(file_name)

    def handle_music_spoiler(self, spoiler_data, config, chain_index=-1, total_chains=-1):

        # Unpack our spoiler config
        spoiler_name, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter = self.unpack_spoiler_config(config)

        # Log that we're handling a music spoiler
        print("{time} | SPOILERS: Handling Music spoiler with name of {spoiler_name}".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # Check to make sure we have the spoiler channel IDs
        spoiler_channel_ids = self.bot.bot_settings.get("spoiler_channel_ids")
        if spoiler_channel_ids:

            # Find which channel to post our spoiler to
            discord_channel_id = spoiler_channel_ids[spoiler_channel_to_post]
            discord_channel = self.bot.get_channel(discord_channel_id)

            # Send our spoiler!
            file_to_send = discord.File(spoiler_data)
            asyncio.run(discord_channel.send(spoiler_post_description, file=file_to_send))

            # Log it
            print("{time} | SPOILERS: Posted Music spoiler with name of {spoiler_name} on Discord".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # Delete our file from cache
        os.remove(spoiler_data)

    def unpack_spoiler_config(self, config):
        spoiler_name = config[bot_globals.SPOILER_NAME]
        spoiler_channel_to_post = config[bot_globals.SPOILER_CHANNEL_TO_POST]
        spoiler_post_description = config[bot_globals.SPOILER_POST_DESCRIPTION]
        spoiler_post_to_twitter = config[bot_globals.SPOILER_POST_TO_TWITTER]

        return spoiler_name, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter

    def divide_spoilers(self, l, n):
        for i in range(0, len(l), n): 
            yield l[i:i + n]

    def convert_to_png(self, file_name):
        old_file_name = file_name
        file_name = file_name.replace(".dds", ".png")

        image_conversion = Image.open(old_file_name)
        image_conversion.save(file_name)

        os.remove(old_file_name)

        # Return our new file name
        return file_name

    def post_spoiler_to_discord(self, file_name, spoiler_name, spoiler_post_description, spoiler_channel_to_post, spoiler_channel_ids):

        if self.discord_post_override:
            return

        # Find which channel to post our spoiler to
        discord_channel_id = spoiler_channel_ids[spoiler_channel_to_post]
        discord_channel = self.bot.get_channel(discord_channel_id)

        # Send our spoiler!
        file_to_send = discord.File(file_name)

        if spoiler_post_description:
            asyncio.run(discord_channel.send(spoiler_post_description, file=file_to_send))
        else:
            asyncio.run(discord_channel.send(file=file_to_send))

        # Log it
        print("{time} | SPOILERS: Posted Image spoiler with name of {spoiler_name} on Discord".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

    def post_spoiler_to_twitter(self, file_name, spoiler_name, spoiler_post_description=None, in_reply_to_status_id=None):

        if self.twitter_post_override:
            return
        
        # Publish the tweet
        if spoiler_post_description:
            twitter_description = self.format_twitter_description(spoiler_post_description)
        else:
            twitter_description = ""
        status = self.twitter_api.PostUpdate(status=twitter_description, media=file_name, in_reply_to_status_id=in_reply_to_status_id)

        # Store the ID of the last tweet made
        self.last_tweet_id = status.id

        # Log it
        print("{time} | SPOILERS: Tweeted Image spoiler with name of {spoiler_name}".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

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

    async def wad_download_demo(self):

        revision = self.bot.bot_settings.get("latest_revision")
        discord_channel = self.bot.get_channel(814900537966329936)

        await discord_channel.send("Starting up! Please wait, this may take a few seconds.")

        # Downloading the wad
        opener = urllib.request.URLopener()
        opener.addheader('User-Agent', 'Mozilla/5.0')
        file_name, headers = opener.retrieve("http://patch.us.wizard101.com/WizPatcher/V_{revision}/LatestBuild/Data/GameData/Root.wad".format(revision=revision), "archive/{revision}/_Wads/Root.wad".format(revision=revision))

        print("done wad download!")
        await discord_channel.send("Second stage done! The next may take around 30 seconds.")

        # Unpacking wads
        root_wad = Wad(path="archive/{revision}/_Wads/Root.wad".format(revision=revision))
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
        file_to_send = discord.File(save_path)
        await discord_channel.send(file=file_to_send)
        print("image sent!")

        await discord_channel.send("There we go!")
