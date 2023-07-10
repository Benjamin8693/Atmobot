# 3rd Party Packages
from code import interact
import dis
from sys import intern
from discord import ButtonStyle, Color, Embed, Interaction, Optional, File
from discord.ui import InputText, Modal, Item, View, Button, button
from discord.ext import tasks

# Local packages
import bot_globals
import utils

# Build-in packages
import asyncio
import datetime
import hashlib
import re
import requests
import struct
import os
import json
import math
import time
import queue
import threading
from multiprocessing import Process
from socket import create_connection
from urllib.request import urlopen, Request
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


def bruteforce_list(patch_url, revision_list, version_list, q):

    # Iterate over all the versions we want to check
    for version in version_list:

        # And all of the revisions in our list
        for revision in revision_list:

            # Generate a patch link to test with
            # TODO: Be able to change automatically between test and live
            link = patch_url.format(revision=revision, version=version)
            
            # Only report back if we get a valid error code
            if requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}).status_code == 200:
                new_revision = ["V_r{revision}".format(revision=revision), version]
                q.put(new_revision)

# Bruteforce a revision from the patcher
async def bruteforce_revision(patch_url, revision_start, revision_range, version_list, q):

    # Range of revisions to bruteforce
    revision_end = revision_start + revision_range
    revision_list = list(range(revision_start, revision_end))

    # Divide our revisions between 16 processes
    revision_lists = [[] for i in range(16)]
    list_length = len(revision_lists)

    i = 0
    while revision_list:
        revision_lists[i].append(revision_list.pop(0))
        i = (i + 1) % list_length

    # Execute all our processes
    processes = []
    for i, l in enumerate(revision_lists):
        p = threading.Thread(target=bruteforce_list, args=(patch_url, l, version_list, q))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()


class Bruteforcer:

    def __init__(self, bot):
        
        self.bot = bot

        self.bruteforcer_config = None
        self.current_profiles = []

        self.embed_comments = bot_globals.bruteforce_embed_comments_idle

        self.time_estimation_threshold = 3

        # Variables for the current bruteforce operation
        self.ongoing_operation = False
        self.loop_operation = False
        self.cancel_operation = False
        self.pause_operation = False
        self.total_queries = 0
        self.current_query = 0
        self.total_terms = 0
        self.current_term = 0
        self.recent_timestamps = []
        self.error_count = 0

        self.http_client = AsyncHTTPClient()
       
    async def startup(self):

        await self.load_bruteforcer()

        return

        # Hash current website info
        print("{time} | CHECKER: Hashing website info".format(time=await self.bot.get_formatted_time()))
        important_urls = await self.get_important_urls()
        for url in important_urls:
            url_request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            url_response = urlopen(url_request).read()
            url_hash = hashlib.sha224(url_response).hexdigest()

            self.url_cache[url] = [url_request, url_hash]

        # Get live and test revisions
        if settings.get("fetch_revision_on_startup", False):

            print("{time} | CHECKER: Fetching Live Realm revision".format(time=await self.bot.get_formatted_time()))
            live_revision = await self.grab_revision(bot_globals.LIVE_REALM)
            if live_revision:
                live_revision = live_revision.split(".")
                await self.bot.update_setting("revision_info_live", live_revision)
                live_revision = await self.full_revision(live_revision)

            print("{time} | CHECKER: Fetching Test Realm revision".format(time=await self.bot.get_formatted_time()))
            test_revision = await self.grab_revision(bot_globals.TEST_REALM)
            if test_revision:
                await self.bot.update_setting("revision_info_test", test_revision)
                test_revision = await self.full_revision(test_revision)
            
            print("{time} | CHECKER: Revisions fetched".format(time=await self.bot.get_formatted_time()))

        else:

            live_revision = settings.get("revision_info_live", [])
            if live_revision:
                live_revision = await self.full_revision(live_revision)

            test_revision = settings.get("revision_info_test", [])
            if test_revision:
                test_revision = await self.full_revision(test_revision)

            print("{time} | CHECKER: Skipping revision fetch".format(time=await self.bot.get_formatted_time()))

        print("{time} | CHECKER: Live revision is {live_revision}".format(time=await self.bot.get_formatted_time(), live_revision=live_revision))
        print("{time} | CHECKER: Test revision is {test_revision}".format(time=await self.bot.get_formatted_time(), test_revision=test_revision))

    async def load_bruteforcer(self):

        # If we don't have a bruteforcer config file, generate one with default options
        if not os.path.isfile(bot_globals.bruteforcer_path):
            with open(bot_globals.bruteforcer_path, "w") as data:
                json.dump(bot_globals.bruteforcer_template, data, indent=4)

        # Load our bruteforcer config
        with open(bot_globals.bruteforcer_path) as data:
            self.bruteforcer_config = json.load(data)

        # Load the active bruteforce profiles
        for mode in bot_globals.bruteforce_mode_to_index.values():
            profile_info, index = await self.get_bruteforce_profile_info(mode)
            self.current_profiles.insert(mode, [profile_info, index])

    async def update_bruteforcer_config(self, config_name, variable_to_replace):

        # We typically shouldn't be updating a config variable that doesn't already exist
        if config_name not in self.bruteforcer_config:
            print("Updated config variable '{}' that does not exist!".format(config_name))

        # Update the config variable
        self.bruteforcer_config[config_name] = variable_to_replace

        # Save our config
        await self.save_bruteforcer_config()

    async def save_bruteforcer_config(self):

        # Write to the bruteforcer config file
        with open(bot_globals.bruteforcer_path, "w") as data:
            json.dump(self.bruteforcer_config, data, indent=4)

    async def get_bruteforce_profile_names(self, mode):

        # Grab the name of the mode we're using
        mode_name = bot_globals.bruteforce_index_to_mode.get(mode)
        if not mode_name:
            return None
            
        # Grab our bruteforcer config
        mode_config = self.bruteforcer_config.get(mode_name)
        if not mode_config:
            return None

        profile_names = []

        # Iterate over all profiles and gather their names
        for profile in mode_config:
            profile_name = profile.get("profile_name")
            profile_names.append(profile_name)

        return profile_names

    async def get_bruteforce_profile_info(self, mode, search_by_name = False):

        # Grab the name of the mode we're using
        mode_name = bot_globals.bruteforce_index_to_mode.get(mode)
        if not mode_name:
            return None, None
            
        # Grab our bruteforcer config
        mode_config = self.bruteforcer_config.get(mode_name)
        if not mode_config:
            return None, None

        # Iterate over all profiles to find the one we want
        for profile in mode_config:

            profile_name = profile.get("profile_name")
            profile_active = profile.get("profile_active")

            # Return the profile based on how we're searching for it
            approved = False
            if search_by_name == profile_name:
                approved = True
            elif profile_active:
                approved = True

            if approved:
                index = mode_config.index(profile)

                # Gather all the info from the profile and return it
                setting_names = await self.get_bruteforce_profile_settings(mode)
                profile_info = []

                for setting in setting_names:
                    info = profile.get(setting)
                    profile_info.append(info)

                return profile_info, index

        return None, None

    async def get_bruteforce_profile_settings(self, mode):

        # Grab the name of the mode we're using
        mode_name = bot_globals.bruteforce_index_to_mode.get(mode)
        if not mode_name:
            return None

        # Grab the template config of the mode
        mode_config = bot_globals.bruteforcer_template.get(mode_name)
        if not mode_config:
            return

        # Use the very first one
        template_config = mode_config[0]

        # Return all the setting names
        setting_names = list(template_config.keys())
        return setting_names

    async def get_bruteforce_profile_setting(self, mode, key):
        
        profile_info = self.current_profiles[mode][bot_globals.BRUTEFORCE_PROFILE_INFO]
        setting = profile_info[key]

        return setting

    async def update_bruteforce_profile_info(self, mode, key, value):
        
        # Grab the current info and update it with our value
        profile_info = self.current_profiles[mode][bot_globals.BRUTEFORCE_PROFILE_INFO]
        if profile_info:
            profile_info[key] = value

        # Save the profile
        self.current_profiles[mode][bot_globals.BRUTEFORCE_PROFILE_INFO] = profile_info

        # Prepare our profile back into a dictonary to save it to our config
        profile_dict = {}
        settings_names = await self.get_bruteforce_profile_settings(mode)
        for index in range(len(profile_info)):
            info = profile_info[index]
            setting_name = settings_names[index]
            profile_dict[setting_name] = info

        # Grab the name of the mode we're using
        mode_name = bot_globals.bruteforce_index_to_mode.get(mode)
        if not mode_name:
            return None

        # Grab our bruteforcer config
        mode_config = self.bruteforcer_config.get(mode_name)
        if not mode_config:
            return

        # Insert the updated profile at the correct index
        profile_index = self.current_profiles[mode][bot_globals.BRUTEFORCE_PROFILE_INDEX]
        mode_config[profile_index] = profile_dict

        await self.update_bruteforcer_config(mode_name, mode_config)

    async def switch_bruteforce_profile(self, mode, selection):

        # Disable the current profile
        await bot.bruteforcer.update_bruteforce_profile_info(mode, bot_globals.BRUTEFORCE_PROFILE_ACTIVE, False)

        # Load the new profile
        profile_names = await self.get_bruteforce_profile_names(mode)
        profile_info, index = await self.get_bruteforce_profile_info(mode, profile_names[selection])
        self.current_profiles[mode] = [profile_info, index]

        # Enable the new profile
        await bot.bruteforcer.update_bruteforce_profile_info(mode, bot_globals.BRUTEFORCE_PROFILE_ACTIVE, True)

    async def add_embed_comments(self, embed: Embed):

        # We don't have any comments to add
        if not self.embed_comments:
            return

        # Keep track of the most recent embed- we may need to update it later
        self.recent_embed = embed

        # Add the embed
        embed.add_field(name = bot_globals.bruteforce_embed_comments, value = self.embed_comments, inline = False)

    async def set_embed_comments(self, comments):

        self.embed_comments = comments

    async def handle_control_panel(self, interaction: Interaction, mode: int, respond: bool = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_control_panel(interaction)
            if respond:
                await interaction.respond(embed = embed, view = view)
                return
            
            await interaction.response.edit_message(embed = embed, view = view)
            return

    async def get_bruteforce_image_control_panel(self, interaction: Interaction):
        
        embed = Embed(color = Color.blurple())
        embed.add_field(name = bot_globals.bruteforce_image_control_panel_name, value = bot_globals.bruteforce_image_control_panel_instructions)
        await self.add_embed_comments(embed)
        view = BruteforceImageControlPanel(author = interaction.user, timeout = None)

        return embed, view

    async def handle_run_panel(self, interaction: Interaction, mode: int, respond: bool = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_run_panel(interaction)
            if respond:
                await interaction.respond(embed = embed, view = view)
                return

            await interaction.response.edit_message(embed = embed, view = view)
            return

    async def get_bruteforce_image_run_panel(self, interaction: Interaction):

        embed = Embed(color = Color.green())
        embed.add_field(name = bot_globals.bruteforce_image_run_name, value = bot_globals.bruteforce_image_run_instructions)
        await self.add_embed_comments(embed)
        view = BruteforceImageRun(author = interaction.user, timeout = None)

        return embed, view

    async def handle_schedule_panel(self, interaction: Interaction, mode: int, respond: bool = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_schedule_panel(interaction)
            if respond:
                await interaction.respond(embed = embed, view = view)
                return

            await interaction.response.edit_message(embed = embed, view = view)
            return

    async def get_bruteforce_image_schedule_panel(self, interaction: Interaction):

        embed = Embed(color = Color.blurple())
        embed.add_field(name = "Schedule", value = "TBD")
        await self.add_embed_comments(embed)
        view = BruteforceImageSchedule(author = interaction.user, timeout = None)

        return embed, view

    async def handle_in_progress_panel(self, interaction: Interaction, mode: int, respond: bool = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_in_progress_panel(interaction)
            if respond:
                await interaction.respond(embed = embed, view = view)
                return

            await interaction.response.edit_message(embed = embed, view = view)
            return

    async def get_bruteforce_image_in_progress_panel(self, interaction: Interaction):

        embed = await self.get_bruteforce_progress_embed()
        await self.add_embed_comments(embed)
        view = BruteforceImageInProgress(author = interaction.user, timeout = None, interaction = interaction)

        return embed, view

    async def handle_profiles_panel(self, interaction: Interaction, mode: int, respond: bool = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_profiles_panel(interaction)
            if respond:
                await interaction.respond(embed = embed, view = view)
                return
            
            await interaction.response.edit_message(embed = embed, view = view)
            return

    async def get_bruteforce_image_profiles_panel(self, interaction: Interaction):

        embed = Embed(color=Color.blurple())
        embed.add_field(name = "Profiles", value = "TBD")
        await self.add_embed_comments(embed)
        view = BruteforceImageProfiles(author = interaction.user, timeout = None)

        return embed, view

    async def handle_edit_profile_panel(self, interaction: Interaction, mode: int, respond: bool = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_edit_profile_panel(interaction)
            if respond:
                await interaction.respond(embed = embed, view = view)
                return

            await interaction.response.edit_message(embed = embed, view = view)
            return

    async def get_bruteforce_image_edit_profile_panel(self, interaction: Interaction):

        embed = Embed(color=Color.blurple())
        embed.add_field(name = "Edit Profile", value = "TBD")
        await self.add_embed_comments(embed)
        view = BruteforceImageEditProfile(author = interaction.user, timeout = None)

        return embed, view

    async def start_image_bruteforce(self, interaction: Interaction = None):

        print("Starting up image bruteforce!")

        if self.ongoing_operation:
            print("Attempted to start an image bruteforce but one is already ongoing!")
            return

        # The bruteforce operation is now in progress
        self.ongoing_operation = True
        self.embed_comments = "Bruteforce in progress."

        # Grab info about the images we're about to bruteforce
        image_names = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)
        image_names_successes = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES_SUCCESSES)
        image_extensions = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_EXTENSIONS)
        image_prefixes = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_PREFIXES)
        image_suffixes = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_SUFFIXES)

        # We have no image names queued up to bruteforce
        if not image_names:
            await self.cancel_image_bruteforce(interaction = interaction, reason = "Attempted to start an image bruteforce without any image names!")
            return

        # For some reason, we don't have any image extensions to bruteforce
        if not image_extensions:
            await self.cancel_image_bruteforce(interaction = interaction, reason = "Attempted to start an image bruteforce without any file extensions!")
            return

        # Even though we don't technically need any prefixes or suffixes, our system requires at the very least an empty string for each
        # So if we don't even have that, we cann't move forward with the bruteforce
        if not image_prefixes or not image_suffixes:
            await self.cancel_image_bruteforce(interaction = interaction, reason = "Attempted to start an image bruteforce without any prefixes or suffixes!")
            return

        # Grab the URL we're going to bruteforce, don't proceed if it doesn't exist
        request_url = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_REQUEST_URL)
        if not request_url:
            await self.cancel_image_bruteforce(interaction = interaction, reason = "Attempted to start an image bruteforce without a URL to bruteforce!")
            return

        # Grab the request cooldown, i.e. how long we wait in between each individual bruteforce
        request_cooldown = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_REQUEST_COOLDOWN)
        if not request_cooldown:
            await self.cancel_image_bruteforce(interaction = interaction, reason = "Attempted to start an image bruteforce with a request cooldown less than or equal to 0!")
            return

        self.total_queries = len(image_names) * len(image_prefixes) * len(image_suffixes) * len(image_extensions)
        self.total_terms = len(image_names)

        if interaction:
            await self.handle_in_progress_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

        # Grab information about how to handle successful bruteforces on Discord and Twitter
        discord_notify = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_DISCORD_NOTIFY)
        discord_channel = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_DISCORD_CHANNEL)
        discord_message = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_DISCORD_MESSAGE)
        twitter_notify = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_TWITTER_NOTIFY)
        twitter_message = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_TWITTER_MESSAGE)


        request_threading = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_REQUEST_THREADING)
        request_threading_count = await self.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_REQUEST_THREADING_COUNT)
        if request_threading:
            # Divide our images between X processes
            image_lists = [[] for i in range(request_threading_count)]
            list_length = len(image_lists)

            i = 0
            image_names_copy = image_names[:]
            while image_names_copy:
                image_lists[i].append(image_names_copy.pop(0))
                i = (i + 1) % list_length

            # Execute all our processes
            processes = []
            for i, l in enumerate(image_lists):
                p = threading.Thread(target = asyncio.run, args=(self.bruteforce_image_list(interaction, l, image_names, image_names_successes, image_prefixes, image_suffixes, image_extensions, request_url, request_cooldown, discord_notify, discord_channel, discord_message, twitter_notify, twitter_message),))
                processes.append(p)
                p.start()

            def get_thread_status():
                status = []
                for p in processes:
                    status.append(p.is_alive())
                return status
            
            thread_status = get_thread_status()
            while any(thread_status):
                thread_status = get_thread_status()
                await asyncio.sleep(5)

        else:

            for image_name in image_names:
                await self.bruteforce_image_name(interaction, image_name, image_names, image_names_successes, image_prefixes, image_suffixes, image_extensions, request_url, request_cooldown, discord_notify, discord_channel, discord_message, twitter_notify, twitter_message)

        # Give our info collector some time to catch up
        asyncio.sleep(3)

        # The bruteforce operation is now over
        self.embed_comments = "Bruteforce over."
        self.ongoing_operation = False
        self.pause_operation = False
        self.cancel_operation = False
        self.total_queries = 0
        self.current_query = 0
        self.total_terms = 0
        self.current_term = 0
        self.recent_timestamps = []

        print("Image bruteforce ended!")

    async def bruteforce_image_list(self, interaction: Interaction, image_list: list, image_names: list, image_names_successes: list, image_prefixes: list, image_suffixes: list, image_extensions: list, request_url: str, request_cooldown: float, discord_notify: bool, discord_channel: int, discord_message: str, twitter_notify: bool, twitter_message: str):

        for image_name in image_list:
            #print("on image {}, index {}\n\n".format(image_name, image_list.index(image_name)))
            await self.bruteforce_image_name(interaction, image_name, image_names, image_names_successes, image_prefixes, image_suffixes, image_extensions, request_url, request_cooldown, discord_notify, discord_channel, discord_message, twitter_notify, twitter_message)

    async def bruteforce_image_name(self, interaction: Interaction, image_name: str, image_names: list, image_names_successes: list, image_prefixes: list, image_suffixes: list, image_extensions: list, request_url: str, request_cooldown: float, discord_notify: bool, discord_channel: int, discord_message: str, twitter_notify: bool, twitter_message: str):

        # Term tracking for reporting info back to our user
        self.current_term += 1

        # Track how long it will take to bruteforce this term
        time_started = datetime.datetime.now()

        # We've been requested to cancel the ongoing operation, so break out from the loop and stop bruteforcing
        if self.cancel_operation:
            await self.cancel_image_bruteforce(interaction = interaction, reason = "User requested to cancel the image bruteforce.")
            #break

        # Iterate over all of our prefixes to attempt every possible variation
        for prefix in image_prefixes:

            # Break out of the loop if we need to cancel the operation
            if self.cancel_operation:
                await self.cancel_image_bruteforce(interaction = interaction, reason = "User requested to cancel the image bruteforce.")
                break

            # Also iterate over all of our suffixes
            for suffix in image_suffixes:

                # Break out of the loop if we need to cancel the operation
                if self.cancel_operation:
                    await self.cancel_image_bruteforce(interaction = interaction, reason = "User requested to cancel the image bruteforce.")
                    break

                # Finally iterate over all the possible file extensions
                for extension in image_extensions:

                    # Break out of the loop if we need to cancel the operation
                    if self.cancel_operation:
                        await self.cancel_image_bruteforce(interaction = interaction, reason = "User requested to cancel the image bruteforce.")
                        break

                    # The operation is paused, hold here until further notice
                    while self.pause_operation:
                        time.sleep(1.0)

                    # Query tracking for reporting back info to the user
                    self.current_query += 1

                    # Bruteforce this image
                    possible_image = prefix + image_name + suffix + extension
                    formatted_url = request_url.format(possible_image)
                    response = await self.bruteforce_image(formatted_url, request_cooldown)

                    # We got a response, which means the image exists! Handle it according to our config
                    if response and ((discord_notify and discord_channel) or twitter_notify):

                        print("Bruteforce found image! {image_name}".format(image_name = possible_image))

                        # Remove the image name from the list
                        image_name_index = image_names.index(image_name)
                        updated_image_names = image_names[:]
                        del updated_image_names[image_name_index]
                        await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES, updated_image_names)

                        # Add it to the the successful name list
                        image_names_successes.append(image_name)
                        await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES_SUCCESSES, image_names_successes)

                        # Save the image to file
                        image = response.body
                        file_path = "cache/{image_name}".format(image_name = possible_image)
                        saved_file = open(file_path, "wb")
                        saved_file.write(image)
                        saved_file.close()

                        # Attempt to post to Discord
                        if discord_notify and discord_channel:
                            formatted_discord_message = "**{discord_message}\n{image_name}**\n<{image_url}>".format(discord_message = discord_message, image_name = possible_image, image_url = formatted_url)
                            file_to_send = File(file_path)
                            await self.bot.queue_to_discord(discord_channel, formatted_discord_message, file_to_send)

                        # Attempt to post to Twitter
                        if twitter_notify:
                            formatted_twitter_message = "{twitter_message}\n{image_name}\n\n{image_url}".format(twitter_message = twitter_message, image_name = possible_image, image_url = formatted_url)
                            await self.bot.send_to_twitter(formatted_twitter_message, file_path)

                    # We're done the bruteforce, cool down a bit to avoid being rate limited
                    #await asyncio.sleep(request_cooldown)

        # Record how long it took to bruteforce this one term
        time_taken =  datetime.datetime.now() - time_started
        await self.record_time_taken(time_taken)

    async def bruteforce_image(self, formatted_url, request_cooldown):

        # Attempt to see if the image exists
        try:
            http_client = AsyncHTTPClient()
            response = await http_client.fetch(HTTPRequest(formatted_url, follow_redirects = False), raise_error = False)
            response_code = response.code
        
        # If it times out, that's fine, just make note of the error
        except Exception as error:
            await self.bruteforce_error(error, formatted_url)
            return None

        # The image exists! Let's return the response to be handled elsewhere
        if response_code == 200:
            return response

        return None

    async def record_time_taken(self, time_taken: datetime.timedelta):
        
        self.recent_timestamps.insert(0, time_taken)
        if len(self.recent_timestamps) > self.time_estimation_threshold:
            self.recent_timestamps.pop()

    async def bruteforce_error(self, error, formatted_url):

        self.error_count += 1
        print("BRUTEFORCE ERROR: {}\nERROR COUNT: {}".format(error, self.error_count))

        if self.error_count > 25:
            self.cancel_operation = True
            print("BRUTEFORCE CANCELLED BECAUSE OF TOO MANY ERRORS! @everyone")

    async def cancel_image_bruteforce(self, interaction, reason: str):

        print("Bruteforce cancelled with reason: {reason}".format(reason))

        self.embed_comments = reason
        self.ongoing_operation = False
        self.total_queries = 0
        self.current_query = 0
        self.total_terms = 0
        self.current_term = 0
        self.recent_timestamps = []

    async def get_bruteforce_progress_embed(self):

        # We have a bruteforce in-progress
        if self.total_queries:

            # Determine percentage completion
            percentage_completed = round(((self.current_query) / self.total_queries) * 100, 2)

            # Estimate how long is left until the bruteforce is completed
            if len(self.recent_timestamps) >= self.time_estimation_threshold:
                average_timedelta = sum([delta.seconds for delta in self.recent_timestamps]) / len(self.recent_timestamps)
                terms_remaining = self.total_terms - self.current_term
                timedelta_to_completion = (average_timedelta * terms_remaining)
                total_seconds = timedelta_to_completion
                hours_to_completion = total_seconds // 3600
                total_seconds = total_seconds - (hours_to_completion * 3600)
                minutes_to_completion = total_seconds // 60
                seconds_to_completion = total_seconds - (minutes_to_completion * 60)
                time_to_completion = "{:02}:{:02}:{:02}".format(int(hours_to_completion), int(minutes_to_completion), int(seconds_to_completion))
            else:
                time_to_completion = bot_globals.bruteforce_image_run_time_to_completion_default

            bruteforce_info = bot_globals.bruteforce_image_run_progress_embed.format(current_query = self.current_query, total_queries = self.total_queries, percentage = percentage_completed, estimated_time = time_to_completion)

            # Embed indicating our progress on the bruteforce
            if not self.ongoing_operation:
                embed = Embed(color = Color.green())
                embed.add_field(name = bot_globals.bruteforce_image_run_completed_name, value = bruteforce_info)
            elif self.pause_operation:
                embed = Embed(color = Color.red())
                embed.add_field(name = bot_globals.bruteforce_image_run_paused_name, value = bruteforce_info)
            else:
                embed = Embed(color = Color.green())
                embed.add_field(name = bot_globals.bruteforce_image_run_in_progress_name, value = bruteforce_info)

            return embed
        
        return None

    async def start_revision_brutefore(self, patch_url, revision_start, revision_range, version_list):
        q = queue.Queue()

        await bruteforce_revision(patch_url, revision_start, revision_range, version_list, q)

        new_revisions = list(q.queue)
        return new_revisions

    async def start_test_realm_check(self):

        if self.bot.spoilers.important_update:
            return

        # TODO: This is temporary, hacky, and nasty
        base_revision = "736675"
        base_version = "WizardDev"
        base_patcher = "testversionec"
        base_patcher_secondary = "testversionec"
        base_service = bot_globals.TEST_REALM

        # We need to see if there are any signs of Test Realm!
        # First things first, let's contact to patcher to see if it's online
        patcher_status = await self.check_patcher(base_service, ["V_r{}".format(base_revision), base_version])

        # Patcher is offline, don't go any further
        if patcher_status == 504:
            print("Patcher is offline.")
            return

        # Patcher returned an odd error code, let's make note of it
        if patcher_status not in (200, 403, 404):
            print("Patcher returned odd status code {}".format(patcher_status))

        # The patcher could be online, let's notify Discord about it before proceeding
        print("Patcher may be online! Returned error code {}".format(patcher_status))
        spoiler_channel_ids = settings.get("spoiler_channels")
        announcement_channel = self.bot.get_channel(spoiler_channel_ids[bot_globals.CHANNEL_ANNOUNCEMENT])
        await announcement_channel.send("Patcher may be online! Returned error code {}".format(patcher_status))

        # Now that we know the patcher has activity, let's attempt to get the new revision
        try:

            print("Attempting to obtain patcher revision normally.")

            url_file, base_url = await self.get_patch_urls(base_patcher_secondary)
            revision = await self.get_revision_from_url(url_file)

            print("Successfully bruteforced patcher revision {} normally.".format(revision))

            # Double check and make sure our revision is higher than the base one
            revision_number = int(revision.split(".")[0].replace("V_r", ""))
            if int(base_revision) >= revision_number:
                print("The new revision is lower than or equal to our base revision!")
                raise Exception

        # Hmm, no luck. But we won't stop there, let's attempt to bruteforce the revision for ourselves.
        except Exception as e:

            print(e)

            print("Unable to get patcher revision normally, attempting bruteforce.")
            patch_url = "http://" + base_patcher + ".us.wizard101.com/WizPatcher/V_r{revision}.{version}/Windows/LatestFileList.bin"
            revisions = await self.start_revision_brutefore(patch_url, int(base_revision), 5000, [base_version])

            if not revisions:
                print("Could not bruteforce a revision, ending test realm check.")
                return

            print("Successfully bruteforced revisions {}!".format(revisions))

            def compare_bruteforced_revisions(revision_list):
                highest_rev = None

                for rev in revision_list:
                    rev_number = int(rev[0].replace("V_r", ""))
                    if not highest_rev:
                        highest_rev = rev
                        continue
                    highest_rev_number = int(highest_rev[0].replace("V_r", ""))
                    if rev_number > highest_rev_number:
                        highest_rev = rev

                return highest_rev

            if len(revisions) > 1:
                print("Multiple revisions bruteforced, finding largest!")
                revision_pair = compare_bruteforced_revisions(revisions)
            else:
                revision_pair = revisions.pop(0)
            revision_number = revision_pair[0].replace("V_", "")
            version = revision_pair[1]
            revision = "{}.{}".format(revision_number, version)

            # Double check and make sure our revision is higher than the base one
            if int(base_revision) >= int(revision_number.replace("r", "")):
                print("The new revision is lower than or equal to our base revision!")
                return

        # By now we must have a revision, so let's pass it over to our spoilers system to handle
        print("Revision obtained! Handling revision {} to be spoiled.".format(revision))

        await self.bot.spoilers.handle_revision(revision)

    async def get_patch_urls(self, server_name):

        url_to_connect = "{server_name}.us.wizard101.com".format(server_name=server_name)
        reader, writer = await asyncio.open_connection(url_to_connect, 12500)

        writer.write(b"\x0D\xF0\x24\x00\x00\x00\x00\x00\x08\x01\x20" + bytes(29))
        await reader.read(4096)  # session offer or whatever

        data = await reader.read(4096)
        writer.close()

        def _read_url(start: int):
            str_len_data = data[start: start + 2]
            str_len = struct.unpack("<H", str_len_data)[0]

            str_data = data[start + 2: start + 2 + str_len]

            return str_data.decode()

        # -2 for the str len
        file_list_url_start = data.find(b"http") - 2
        base_url_start = data.rfind(b"http") - 2

        return _read_url(file_list_url_start), _read_url(base_url_start)

    # Stolen from WizDiff, grabs revision from any patcher url
    async def get_revision_from_url(self, url: str):
        res = re.compile(r"WizPatcher/([^/]+)").search(url)

        if res is None:
            raise ValueError(f"Reversion string not found in {url}")

        return res.group(1)

    # Used to check whether the Test Realm patcher is online
    async def check_patcher(self, service, revision):

        # Status code of the patcher
        status_code = 0

        # We're making this a try in the case we cannot cannot (which is actually most of the time)
        try:

            # Make a request to the patcher to determine the status code
            patcher_url = await self.grab_patcher_url(service=service, revision = revision)
            patcher_request = requests.head(patcher_url)
            status_code = patcher_request.status_code

            return status_code

        # If we cannot connect, that's a status code too
        except requests.ConnectionError:

            return status_code

    # Constructs a pathcher url
    async def grab_patcher_url(self, server=bot_globals.VERSIONEC, service=bot_globals.TEST_REALM, game=bot_globals.WIZARD101, revision=None, wad=bot_globals.fallback_wad):

        # Grab our server name
        service_name = bot_globals.service_names.get(service)
        server_name = bot_globals.server_options.get(server)
        full_server_name = service_name + server_name

        # Game longhand and shorthand
        game_longhand = bot_globals.game_longhands.get(game)
        game_shorthand = bot_globals.game_shorthands_patcher.get(game)

        # Grab revision from settings if we didn't provide it
        if not revision:
            setting_name = "revision_info_{service}".format(service=service_name if service_name else "live")
            revision = settings.get(setting_name, [])

        # TODO: Automatically request/bruteforce revision via URL if we STILL don't have it

        # Separate revision number and version
        revision_number = revision[bot_globals.REVISION_NUMBER]
        revision_version = revision[bot_globals.REVISION_VERSION]

        # Format everything together into our patcher url
        patcher_url = bot_globals.patcher_url.format(server=full_server_name, game_longhand=game_longhand, game_shorthand=game_shorthand, revision_number=revision_number, revision_version=revision_version, wad_name=wad)
        return patcher_url

    """
    async def grab_revision(self, service):

        # It won't always work depending on whether the server is up and accepting connections
        try:
            server_name = bot_globals.service_names.get(service) + bot_globals.server_options.get(bot_globals.PATCH)
            url_file = await self.get_patch_url(server_name)
            revision = await self.get_revision_from_url(url_file)
            return revision

        # Handle any errors
        except:

            # We aren't giving up if it's Test Realm! Bruteforce activate
            if service == bot_globals.TEST_REALM:

                # Start with the most recent revision we have
                revision_start = await self.most_recent_revision()
                version_list = [await self.most_recent_version(), bot_globals.fallback_version_dev]
                revision = await self.revision_bruteforcer.start(revision_start=revision_start, revision_range=bot_globals.default_revision_range, version_list=version_list)
                return revision

            # Just return an empty string, we were unsuccessful
            else:
                return ""

    async def most_recent_revision(self):

        # Live revision info
        live_revision = settings.get("revision_info_live")
        if live_revision:
            live_revision_number = await self.revision_to_int(live_revision[bot_globals.REVISION_NUMBER])
        else:
            live_revision_number = bot_globals.fallback_revision

        # Test revision info
        test_revision = settings.get("revision_info_test")
        if test_revision:
            test_revision_number = await self.revision_to_int(test_revision[bot_globals.REVISION_NUMBER])
        else:
            test_revision_number = bot_globals.fallback_revision

        # Return most recent revision
        recent_revision = max(live_revision_number, test_revision_number)

        return recent_revision

    async def most_recent_version(self, next_version=True):

        live_revision = settings.get("revision_info_live")
        if live_revision:
            live_version = live_revision[bot_globals.REVISION_VERSION]
        else:
            live_version = bot_globals.fallback_version
        live_version = int("".join(x for x in live_version if x.isdigit()))

        test_revision = settings.get("revision_info_test")
        if test_revision:
            test_version = test_revision[bot_globals.REVISION_VERSION]
        else:
            test_version = bot_globals.fallback_version
        test_version = int("".join(x for x in test_version if x.isdigit()))

        # Return most recent version
        recent_version = max(live_version, test_version)
        
        if next_version:
            recent_version += 10

        return await self.int_to_version(str(recent_version))

    async def revision_to_int(self, revision):
        revision = revision.replace("V_r", "")
        return int(revision)

    async def full_revision(self, revision):
        return ".".join(revision)

    async def int_to_version(self, version):
        return bot_globals.version_empty.format(version[0], version[1:])

    # To grab important urls to check for Test Realm activity
    async def get_important_urls(self):

        # You know, at first I was just going to reference "self.startup_time", but I realized that in the odd
        # case this bot manages to stay up for more than a few days at a time, it could start producing
        # undesirable results. In which case, we'll grab a new datetime whenever this function is ran.
        current_time = datetime.datetime.now()

        # Grab the month and year strings
        month_string = current_time.strftime("%B").lower()
        year_string = current_time.strftime("%Y")

        # Plug them into our update notes url
        update_notes_url = bot_globals.update_notes_url.format(month=month_string, year=year_string)

        # Return our urls to check
        important_urls = [bot_globals.test_patch_client_url, update_notes_url]
        return important_urls

    # Ran whenver we want to check to see if one of our important urls have updated
    async def check_url_status(self):

        # Whether one of the urls has changed
        changed = False

        # Iterate over our urls to determine if any have changed
        important_urls = await self.get_important_urls()
        for url in important_urls:

            # Just in case something goes wrong here
            try:

                # Load up our prior request and hash
                cache = self.url_cache[url]
                request = cache[bot_globals.URL_CACHE_REQUEST]
                old_hash = cache[bot_globals.URL_CACHE_HASH]

                # Make a new request and hash the response
                new_url_response = urlopen(request).read()
                new_hash = hashlib.sha224(new_url_response).hexdigest()

                # The url has changed
                if old_hash != new_hash:
                    changed = True

                # Insert new hash back into the dict
                cache[bot_globals.URL_CACHE_HASH] = new_hash
                self.url_cache[url] = cache

            # Uh oh, that's not good
            except Exception as e:
                print("Error has occurred: {}".format(e))

        return changed

    """

""""
OLD CODE ABOVE
NEW CODE BELOW
"""

class BruteforceImageControlPanel(utils.PrivateView):
    """
    Interface for interacting with the image bruteforcer.

    Run: Displays a view giving you options on how to run the current bruteforce profile.
    Profiles: Displays a view giving you options to manage the current bruteforce profiles.
    Close: Deletes the message with our view, essentially closing the bruteforcer.

    """

    def __init__(self, author, *items: Item, timeout: Optional[float] = 180, disable_on_timeout: bool = False):
        super().__init__(author, *items, timeout=timeout, disable_on_timeout=disable_on_timeout)

        if bot.bruteforcer.ongoing_operation:
            self.in_progress_button = Button(label = bot_globals.bruteforce_image_run_in_progress_button,
                                             style = ButtonStyle.green)
            self.in_progress_button.callback = self.view_bruteforce
            self.add_item(self.in_progress_button)

        self.run_button = Button(label = bot_globals.bruteforce_image_run_button,
                                 style = ButtonStyle.green,
                                 disabled = False if not bot.bruteforcer.ongoing_operation else True)
        self.run_button.callback = self.run_bruteforce
        self.add_item(self.run_button)

        self.profiles_button = Button(label = bot_globals.bruteforce_image_profiles_button,
                                      style = ButtonStyle.blurple)
        self.profiles_button.callback = self.show_profiles
        self.add_item(self.profiles_button)

        self.close_button = Button(label = bot_globals.bruteforce_close_button,
                                   style = ButtonStyle.grey)
        self.close_button.callback = self.close_bruteforcer
        self.add_item(self.close_button)

    async def view_bruteforce(self, interaction: Interaction):

        await bot.bruteforcer.handle_in_progress_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    async def run_bruteforce(self, interaction: Interaction):

        await bot.bruteforcer.handle_run_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    async def show_profiles(self, interaction: Interaction):

        await bot.bruteforcer.handle_profiles_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    async def close_bruteforcer(self, interaction: Interaction):

        await interaction.message.delete()


class BruteforceImageRun(utils.PrivateView):
    """
    Interface for running the image bruteforcer using the current profile.

    Start: Starts a bruteforce using the current profile, and displays a view of the bruteforce's progress.
    Loop: Starts a bruteforce on loop using the current profile, and displays a view of the bruteforce's progress.
    Schedule: Displays a view giving you options to schedule when the next bruteforce should occur.
    Back: Returns to the Image Bruteforcer Control Panel.

    """

    def __init__(self, author, *items: Item, timeout: Optional[float] = 180, disable_on_timeout: bool = False):
        super().__init__(author, *items, timeout=timeout, disable_on_timeout=disable_on_timeout)

        if bot.bruteforcer.ongoing_operation:
            self.in_progress_button = Button(label = bot_globals.bruteforce_image_run_in_progress_button,
                                             style = ButtonStyle.green)
            self.in_progress_button.callback = self.view_bruteforce
            self.add_item(self.in_progress_button)

        self.start_button = Button(label = bot_globals.bruteforce_image_run_start_button,
                                   style = ButtonStyle.green,
                                   disabled = False if not bot.bruteforcer.ongoing_operation else True)
        self.start_button.callback = self.start_bruteforce
        self.add_item(self.start_button)

        self.loop_button = Button(label = bot_globals.bruteforce_image_run_loop_button,
                                  style = ButtonStyle.green,
                                  disabled = False if not bot.bruteforcer.ongoing_operation else True)
        self.loop_button.callback = self.loop_bruteforce
        self.add_item(self.loop_button)

        self.schedule_button = Button(label = bot_globals.bruteforce_image_run_schedule_button,
                                      style = ButtonStyle.blurple,
                                      disabled = False if not bot.bruteforcer.ongoing_operation else True)
        self.schedule_button.callback = self.schedule_bruteforce
        self.add_item(self.schedule_button)

        self.back_button = Button(label = bot_globals.bruteforce_back_button,
                                  style = ButtonStyle.grey)
        self.back_button.callback = self.enter_control_panel
        self.add_item(self.back_button)

    async def view_bruteforce(self, interaction: Interaction):

        await bot.bruteforcer.handle_in_progress_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    async def start_bruteforce(self, interaction: Interaction):

        await bot.bruteforcer.start_image_bruteforce(interaction = interaction)

    async def loop_bruteforce(self, interaction: Interaction):

        await interaction.response.send_message("Temporarily disabled.")

    async def schedule_bruteforce(self, interaction: Interaction):

        await bot.bruteforcer.handle_schedule_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    async def enter_control_panel(self, interaction: Interaction):

        await bot.bruteforcer.handle_control_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)


class BruteforceImageSchedule(utils.PrivateView):
    """

    """

    def __init__(self, author, *items: Item, timeout: Optional[float] = 180, disable_on_timeout: bool = False):
        super().__init__(author, *items, timeout=timeout, disable_on_timeout=disable_on_timeout)

        self.timer_button = Button(label = "Timer",
                                   style = ButtonStyle.green)
        self.timer_button.callback = self.schedule_timer
        self.add_item(self.timer_button)

        self.date_button = Button(label = "Date",
                                  style = ButtonStyle.green,
                                  disabled = True)
        self.date_button.callback = self.schedule_date
        self.add_item(self.date_button)

        self.back_button = Button(label = bot_globals.bruteforce_back_button,
                                  style = ButtonStyle.grey)
        self.back_button.callback = self.enter_run_panel
        self.add_item(self.back_button)

    async def schedule_timer(self, interaction: Interaction):

        modal = BruteforceImageScheduleTimer(title = "Enter a time in seconds.")
        await interaction.response.send_modal(modal)

    async def schedule_date(self, interaction: Interaction):

        return

    async def enter_run_panel(self, interaction: Interaction):

        await bot.bruteforcer.handle_run_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)


class BruteforceImageScheduleTimer(Modal):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.seconds_input = InputText(label = "Seconds", placeholder = "300")

        self.add_item(self.seconds_input)

    async def callback(self, interaction: Interaction):

        seconds = self.seconds_input.value

        await bot.add_scheduled_task("Scheduled Bruteforce", "start_image_bruteforce", delay = int(seconds))
        await interaction.response.send_message("Scheduled timed bruteforce. Starting in 5 seconds, to loop every {seconds} seconds.".format(seconds = seconds))

        return

        # Current image names
        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)

        # Image index to pop
        image_index = self.children[0].value

        # Only pop the index if an integer was specified
        if image_index.isdigit():

            # The index can only be between 1 and the length of the image name list
            if 1 <= int(image_index) <= len(current_image_names):

                popped_image_name = current_image_names.pop(int(image_index) - 1)
                await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES, current_image_names)

                await interaction.response.send_message("Popped **{popped_image_name}** from the list.".format(popped_image_name = popped_image_name), delete_after=5)
                
                return

        await interaction.response.send_message("Invalid index specified.", delete_after=5)


class BruteforceImageInProgress(utils.PrivateView):
    """
    Interface for viewing the current bruteforce in progress

    Cancel: Starts a bruteforce using the current profile, and displays a view of the bruteforce's progress.
    Pause: Starts a bruteforce on loop using the current profile, and displays a view of the bruteforce's progress.
    Back: Returns to the Image Bruteforcer Control Panel.

    """

    def __init__(self, author, *items: Item, timeout: Optional[float] = 180, disable_on_timeout: bool = False, interaction: Interaction = None):
        super().__init__(author, *items, timeout = timeout, disable_on_timeout = disable_on_timeout)

        self.interaction = interaction

        self.cancel_button = Button(label = "Cancel",
                                    style = ButtonStyle.red)
        self.cancel_button.callback = self.cancel_bruteforce
        self.add_item(self.cancel_button)

        self.pause_button = Button(label = "Pause",
                                   style = ButtonStyle.red,
                                   disabled = True)
        self.pause_button.callback = self.pause_bruteforce
        self.add_item(self.pause_button)

        self.back_button = Button(label = bot_globals.bruteforce_back_button,
                                  style = ButtonStyle.grey)
        self.back_button.callback = self.enter_run_panel
        self.add_item(self.back_button)

        self.update_progress_embed.start()

    @tasks.loop(seconds = 3)
    async def update_progress_embed(self):

        # If we're no longer attached to the interaction, stop the loop
        if not bot.bruteforcer.ongoing_operation:
            self.update_progress_embed.stop()
            return

        # Generate an embed
        embed = await bot.bruteforcer.get_bruteforce_progress_embed()
        await bot.bruteforcer.add_embed_comments(embed)

        # Update our message with the new embed
        await self.interaction.message.edit(embed = embed, view = self)

    async def cancel_bruteforce(self, interaction: Interaction):

        bot.bruteforcer.loop_operation = False
        bot.bruteforcer.cancel_operation = True

        self.update_progress_embed.stop()

        embed, view = await bot.bruteforcer.get_bruteforce_image_control_panel(interaction)
        await interaction.response.edit_message(content = None, embed = embed, view = view)

    async def pause_bruteforce(self, interaction: Interaction):

        if bot.bruteforcer.pause_operation:
            bot.bruteforcer.pause_operation = False
        #    self.pause_button.label = "Pause"
        #    self.pause_button.style = ButtonStyle.red
            
        else:
            bot.bruteforcer.pause_operation = True
        #    self.pause_button.label = "Resume"
        #    self.pause_button.style = ButtonStyle.green
        #self.pause_button.callback = self.pause_bruteforce

        #await interaction.response.defer()
        #await interaction.message.edit(view = self)

        await bot.bruteforcer.handle_in_progress_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    async def enter_run_panel(self, interaction: Interaction):

        self.update_progress_embed.stop()
        await bot.bruteforcer.handle_run_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)


class BruteforceImageProfiles(utils.PrivateView):

    @button(label = "Switch", style = ButtonStyle.blurple)
    async def switch_profile(self, button: Button, interaction: Interaction):

        # Send a view with options for browsing the list of images
        profile_names = await bot.bruteforcer.get_bruteforce_profile_names(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)
        switch_profile_view = utils.SelectData(author = interaction.user,
                                               timeout = None,
                                               data = profile_names, 
                                               title = bot_globals.bruteforce_image_browse_terms_name,
                                               back_callback = self.back_callback,
                                               select_callback = self.select_callback)
        switch_profile_view.current_selection = bot.bruteforcer.current_profiles[bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE][bot_globals.BRUTEFORCE_PROFILE_INDEX]
        await switch_profile_view.update(interaction, selection = True)

    async def back_callback(self, interaction):

        await bot.bruteforcer.handle_profiles_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    async def select_callback(self, interaction, selection):

        await bot.bruteforcer.switch_bruteforce_profile(mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, selection = selection)
        await bot.bruteforcer.handle_profiles_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    @button(label = "New", style = ButtonStyle.green)
    async def add_profile(self, button: Button, interaction: Interaction):
        return

    @button(label = "Delete", style = ButtonStyle.red)
    async def remove_profile(self, button: Button, interaction: Interaction):
        return

    @button(label = "Edit", style = ButtonStyle.blurple)
    async def edit_profile(self, button: Button, interaction: Interaction):

        await bot.bruteforcer.handle_edit_profile_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    @button(label = "Back", style = ButtonStyle.grey)
    async def enter_control_panel(self, button: Button, interaction: Interaction):

        await bot.bruteforcer.handle_control_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)


class BruteforceImageEditProfile(utils.PrivateView):

    # Button for adding names to the bruteforce list
    @button(label = bot_globals.bruteforce_image_profile_add_term_button, style = ButtonStyle.green)
    async def add_name(self, button: Button, interaction: Interaction):

        # TODO: Not only do we need to standardize how this is loaded, but we should have a View for various ways to add
        # TODO: Like right now you can only add one new name at a time, but I want a way to do it via file upload

        # Send a modal requesting a name to bruteforce
        modal = BruteforceImageEditProfileAdd(title = "Enter a name to bruteforce.")
        await interaction.response.send_modal(modal)

    # Button for removing image names to bruteforce
    @button(label = bot_globals.bruteforce_image_profile_remove_term_button, style = ButtonStyle.red)
    async def remove_name(self, button: Button, interaction: Interaction):

        # TODO: Standardize how this is loaded

        # Embed containing instructions on how to use the following view
        embed = Embed(color=Color.red())
        embed.add_field(name = bot_globals.bruteforce_image_profile_remove_term_name, value = bot_globals.bruteforce_image_profile_remove_term_instructions)

        # Send a view with options for removing a name from the brutefoce list
        view = BruteforceImageEditProfileRemove(author = interaction.user, timeout = None)
        await interaction.response.edit_message(embed = embed, view = view)

    # Button for browsing the current list of image names
    @button(label = bot_globals.bruteforce_image_browse_terms_button, style = ButtonStyle.blurple)
    async def browse_names(self, button: Button, interaction: Interaction):

        # Send a view with options for browsing the list of images
        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)
        browse_names_view = utils.BrowseData(author = interaction.user,
                                             timeout = None,
                                             data = current_image_names, 
                                             title = bot_globals.bruteforce_image_browse_terms_name,
                                             back_callback = self.back_callback)
        await browse_names_view.update(interaction)

    @button(label = "Import", style = ButtonStyle.blurple)
    async def import_names(self, button: Button, interaction: Interaction):

        author = interaction.user
        channel_id = interaction.channel_id

        def check(m):
            return m.author == author and m.channel.id == channel_id

        await interaction.response.send_message("Please upload your file.")

        try:
            import_message = await bot.wait_for("message", check = check, timeout = 15.0)
        except Exception as e:
            await interaction.followup.send("Unable to import file. Please try again.")
            return

        new_names = []
        for import_attachment in import_message.attachments:
            if import_attachment.filename.endswith(".txt"):
                await import_attachment.save(fp = "cache/Import.txt")
                name_file = open("cache/Import.txt", "r")
                name_list = name_file.readlines()
                for name in name_list:
                    new_names.append(name.strip())

        await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES, new_names)
        await interaction.followup.send("Import successful.")
        
    @button(label = "Export", style = ButtonStyle.blurple)
    async def export_names(self, button: Button, interaction: Interaction):

        # Send a view with options for browsing the list of images
        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)
        profile_name = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_PROFILE_NAME)

        file_path = "cache/{profile_name}_Export.txt".format(profile_name = profile_name)
        with open(file_path, "w") as f:
            for image_name in current_image_names:
                f.write("{image_name}\n".format(image_name = image_name))

        export_file = File(file_path)
        await interaction.response.send_message(file = export_file)

    async def back_callback(self, interaction):

        await bot.bruteforcer.handle_edit_profile_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    @button(label = "Back", style = ButtonStyle.grey)
    async def enter_control_panel(self, button: Button, interaction: Interaction):

        await bot.bruteforcer.handle_profiles_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)


class BruteforceImageEditProfileAdd(Modal):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(InputText(label="Image Name", placeholder = "NewPvPArena"))

    async def callback(self, interaction: Interaction):

        # Grab current image names and name to add
        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)
        image_name = self.children[0].value

        # We don't want to add any names that are too long
        if len(image_name) > 50:
            await interaction.response.send_message("Image name is too long!", delete_after=5)
            return

        # We don't want to add a name already in the list
        if image_name in current_image_names:
            await interaction.response.send_message("**{image_name}** already exists in bruteforce list.".format(image_name = image_name), delete_after=5)
            return

        # Update the image names with our new list
        current_image_names.append(image_name)
        await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES, current_image_names)

        # Let the user know their name was added to the list
        await interaction.response.send_message("Added image name **{image_name}** to bruteforce list.".format(image_name = image_name), delete_after=5)


class BruteforceImageEditProfileRemove(utils.PrivateView):

    # Button for clearing all names from the image bruteforce list
    @button(label = "Clear", style = ButtonStyle.red)
    async def clear_all(self, button: Button, interaction: Interaction):

        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)

        # Empty the list of image names
        await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES, [])

        # Relay message that the list has been cleared
        if current_image_names:
            await interaction.response.send_message("Cleared all image names.", delete_after=5)

        else:
            await interaction.response.send_message("No image names available to clear.", delete_after=5)

    # Button for removing the name at the front of the image bruteforce list
    @button(label = "Remove First", style = ButtonStyle.red)
    async def remove_front(self, button: Button, interaction: Interaction):

        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)

        if current_image_names:
            popped_image_name = current_image_names.pop(0)
            await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES, current_image_names)

            await interaction.response.send_message("Removed **{popped_image_name}** from front of list.".format(popped_image_name = popped_image_name), delete_after=5)

        else:

            await interaction.response.send_message("No image names available to remove.", delete_after=5)

    # Button for removing the name at the back of the image bruteforce list
    @button(label = "Remove Last", style = ButtonStyle.red)
    async def remove_back(self, button: Button, interaction: Interaction):

        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)

        if current_image_names:
            popped_image_name = current_image_names.pop()
            await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES, current_image_names)

            await interaction.response.send_message("Removed **{popped_image_name}** from back of list.".format(popped_image_name = popped_image_name), delete_after=5)

        else:

            await interaction.response.send_message("No image names available to remove.", delete_after=5)

    # Button for removing the name at the specified index
    @button(label = "Remove Specific", style = ButtonStyle.red)
    async def remove_index(self, button: Button, interaction: Interaction):

        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)

        if current_image_names:

            # TODO: Standardize how this is loaded?
            
            modal = BruteforceImageEditProfileRemoveIndex(title = "Type an image index to remove.")
            await interaction.response.send_modal(modal)

        else:

            await interaction.response.send_message("No image names available to remove.", delete_after=5)

    @button(label = "Back", style = ButtonStyle.grey)
    async def enter_control_panel(self, button: Button, interaction: Interaction):

        embed, view = await bot.bruteforcer.get_bruteforce_image_control_panel(interaction)
        await interaction.response.edit_message(content = None, embed = embed, view = view)


class BruteforceImageEditProfileRemoveIndex(Modal):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(InputText(label="Index", placeholder = "1"))

    async def callback(self, interaction: Interaction):

        # Current image names
        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)

        # Image index to pop
        image_index = self.children[0].value

        # Only pop the index if an integer was specified
        if image_index.isdigit():

            # The index can only be between 1 and the length of the image name list
            if 1 <= int(image_index) <= len(current_image_names):

                popped_image_name = current_image_names.pop(int(image_index) - 1)
                await bot.bruteforcer.update_bruteforce_profile_info(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES, current_image_names)

                await interaction.response.send_message("Popped **{popped_image_name}** from the list.".format(popped_image_name = popped_image_name), delete_after=5)
                
                return

        await interaction.response.send_message("Invalid index specified.", delete_after=5)

