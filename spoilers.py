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

        delta_name = delta.name.replace("Data/GameData/", "")
        delta_name = delta_name.replace(".wad", "")

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
        for inner_file_info in delta.changed_inner_files:

            # Check if one of our paths of interest matches
            match = False
            config = None
            for interest_path in paths_of_interest:
                if inner_file_info.name.startswith(interest_path[0]):
                    match = True
                    config = interest_path[1]
                    break

            # We aren't a match, so continue with the next file in line
            if not match or not config:
                continue

            # Okay, now we know this is a file we should spoil
            # Let's handle it then pass it off to one of our spoiler components

            # Get the size of the file data depending on whether it's compressed
            if inner_file_info.is_compressed:
                data_size = inner_file_info.compressed_size
            else:
                data_size = inner_file_info.size

            # Download the file!
            file_data = self.webdriver.get_url_data(delta.url, data_range=(inner_file_info.file_offset, inner_file_info.file_offset + data_size))

            # Decompress if compressed
            if inner_file_info.is_compressed:
                file_data = zlib.decompress(file_data)

            # Lowercase file name to check extension
            lower_file_name = inner_file_info.name.lower()

            # Handle locale files
            if lower_file_name.endswith(".lang"):
                self.handle_locale_spoiler(file_data, inner_file_info.name, config)

            # Handle image files
            elif lower_file_name.endswith((".dds", ".png", ".jpg")):
                self.handle_image_spoiler(file_data, inner_file_info.name, config)

            # Handle music files
            elif lower_file_name.endswith((".mp3", ".ogg", ".wav")):
                self.handle_music_spoiler(file_data, inner_file_info.name, config)

            time.sleep(bot_globals.time_between_posts)

    def handle_locale_spoiler(self, file_data, file_name, config):
        return
    
    def handle_image_spoiler(self, file_data, file_name, config):
        
        # Unpack our spoiler config
        spoiler_name, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter = self.unpack_spoiler_config(config)

        # Log that we're handling a music spoiler
        print("{time} | SPOILERS: Handling Image spoiler with name of {spoiler_name}".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # Save spoiler into cache
        file_name = os.path.basename(file_name)
        file_name = "cache/" + file_name
        with self.safe_open_w(file_name) as fp:
            fp.write(file_data)

        # Convert any .DDS files to .PNG
        if file_name.endswith(".dds"):

            old_file_name = file_name
            file_name = file_name.replace(".dds", ".png")

            image_conversion = Image.open(old_file_name)
            image_conversion.save(file_name)

            os.remove(old_file_name)

        # Check to make sure we have the spoiler channel IDs
        spoiler_channel_ids = self.bot.bot_settings.get("spoiler_channel_ids")
        if spoiler_channel_ids:

            # Find which channel to post our spoiler to
            discord_channel_id = spoiler_channel_ids[spoiler_channel_to_post]
            discord_channel = self.bot.get_channel(discord_channel_id)

            # Send our spoiler!
            file_to_send = discord.File(file_name)
            asyncio.run(discord_channel.send(spoiler_post_description, file=file_to_send))

            # Log it
            print("{time} | SPOILERS: Posted Image spoiler with name of {spoiler_name} on Discord".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # Tweet out the spoiler!
        if spoiler_post_to_twitter:
            twitter_description = self.format_twitter_description(spoiler_post_description)
            self.twitter_api.PostUpdate(status=twitter_description, media=file_name)

            # Log it
            print("{time} | SPOILERS: Tweeted Image spoiler with name of {spoiler_name}".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # Delete our file from cache
        os.remove(file_name)

    def handle_music_spoiler(self, file_data, file_name, config):

        # Unpack our spoiler config
        spoiler_name, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter = self.unpack_spoiler_config(config)

        # Log that we're handling a music spoiler
        print("{time} | SPOILERS: Handling Music spoiler with name of {spoiler_name}".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # Save spoiler into cache
        file_name = os.path.basename(file_name)
        file_name = "cache/" + file_name
        with self.safe_open_w(file_name) as fp:
            fp.write(file_data)

        # Check to make sure we have the spoiler channel IDs
        spoiler_channel_ids = self.bot.bot_settings.get("spoiler_channel_ids")
        if spoiler_channel_ids:

            # Find which channel to post our spoiler to
            discord_channel_id = spoiler_channel_ids[spoiler_channel_to_post]
            discord_channel = self.bot.get_channel(discord_channel_id)

            # Send our spoiler!
            file_to_send = discord.File(file_name)
            asyncio.run(discord_channel.send(spoiler_post_description, file=file_to_send))

            # Log it
            print("{time} | SPOILERS: Posted Music spoiler with name of {spoiler_name} on Discord".format(time=self.get_formatted_time(), spoiler_name=spoiler_name))

        # Delete our file from cache
        os.remove(file_name)

    def unpack_spoiler_config(self, config):
        spoiler_name = config[bot_globals.SPOILER_NAME]
        spoiler_channel_to_post = config[bot_globals.SPOILER_CHANNEL_TO_POST]
        spoiler_post_description = config[bot_globals.SPOILER_POST_DESCRIPTION]
        spoiler_post_to_twitter = config[bot_globals.SPOILER_POST_TO_TWITTER]

        return spoiler_name, spoiler_channel_to_post, spoiler_post_description, spoiler_post_to_twitter

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

    async def join_images_demo(self):

        discord_channel = self.bot.get_channel(814900537966329936)
        await discord_channel.send("Start @ {time}".format(time=self.get_formatted_time()))

        npc_portaits = os.listdir("join_test/")
        images = [Image.open("join_test/{}".format(x)) for x in npc_portaits]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths[:4])
        max_height = sum(heights[::4])

        new_im = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        y_offset = 0
        every_fourth_image = [images[3], images[7], images[11]]
        for im in images:
            new_im.paste(im, (x_offset, y_offset))
            x_offset += im.size[0]
            if im in every_fourth_image:
                x_offset = 0
                y_offset += im.size[1]

        new_im.save('test.png')

        file_to_send = discord.File('test.png')
        await discord_channel.send(file=file_to_send)
        await discord_channel.send("Finish @ {time}".format(time=self.get_formatted_time()))

        return

    async def patcher_file_demo(self):
        discord_channel = self.bot.get_channel(814900537966329936)
        await discord_channel.send("Start @ {time}".format(time=datetime.datetime.now().strftime("%H:%M:%S")))

        revision = "V_r702235.Wizard_1_460"
        file_list_url = "http://testversionec.us.wizard101.com/WizPatcher/V_r702235.Wizard_1_460/Windows/LatestFileList.bin"
        base_url = "http://testversionec.us.wizard101.com/WizPatcher/V_r702235.Wizard_1_460/LatestBuild"
        p = threading.Thread(target=self.new_revision, args=(revision, file_list_url, base_url))
        p.start()
        p.join()

        # Wait for file to exist
        image_path = "Button_World_Karamelle.dds"
        while not os.path.isfile(image_path):
            sleep(1)

        # Convert
        deck_config = Image.open(image_path)
        save_path = "Button_World_Karamelle.png"
        deck_config.save(save_path)

        # Send
        file_to_send = discord.File(save_path)
        await discord_channel.send(file=file_to_send)
        await discord_channel.send("Finish @ {time}".format(time=datetime.datetime.now().strftime("%H:%M:%S")))

        #self.twitter_api.PostUpdate(status="Testing! :)", media=save_path)

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
