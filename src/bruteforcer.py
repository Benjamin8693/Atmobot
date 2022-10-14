# 3rd Party Packages
from discord import ButtonStyle, Color, Embed, Interaction, Optional, File
from discord.ui import InputText, Modal, Item, View, Button, button

# Local packages
import bot_globals
import utils

# Build-in packages
import asyncio
import datetime
import hashlib
from multiprocessing import Process
import re
import requests
from socket import create_connection
import struct
from urllib.request import urlopen, Request
import os
import json
import math
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class Bruteforcer:

    def __init__(self, bot):
        
        self.bot = bot

        self.bruteforcer_config = None
        self.current_profiles = []

        self.loop_operation = False
        self.cancel_operation = False
        self.pause_operation = False

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
        for info in profile_info:
            index = profile_info.index(info)
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

    async def handle_control_panel(self, interaction, mode, respond = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_control_panel()
            if respond:
                await interaction.respond(embed = embed, view = view)
            else:
                await interaction.response.edit_message(embed = embed, view = view)
            return

        elif mode == bot_globals.COMMAND_BRUTEFORCE_MODE_WEBSITE:

            await interaction.respond("Website bruteforcer not yet implemented.")
            return

        elif mode == bot_globals.COMMAND_BRUTEFORCE_MODE_REVISION:

            await interaction.respond("Revision bruteforcer not yet implemented.")
            return

        await interaction.respond("Error!")

    async def get_bruteforce_image_control_panel(self):
        
        embed = Embed(color = Color.blurple())
        embed.add_field(name = bot_globals.bruteforce_image_control_panel_name, value = bot_globals.bruteforce_image_control_panel_instructions)
        view = BruteforceImageControlPanel(timeout = None)

        return embed, view

    async def handle_run_panel(self, interaction, mode, respond = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_run_panel()
            if respond:
                await interaction.respond(embed = embed, view = view)
            else:
                await interaction.response.edit_message(embed = embed, view = view)
            return

        elif mode == bot_globals.COMMAND_BRUTEFORCE_MODE_WEBSITE:

            await interaction.respond("Website bruteforcer not yet implemented.")
            return

        elif mode == bot_globals.COMMAND_BRUTEFORCE_MODE_REVISION:

            await interaction.respond("Revision bruteforcer not yet implemented.")
            return

    async def get_bruteforce_image_run_panel(self):

        embed = Embed(color=Color.green())
        embed.add_field(name = bot_globals.bruteforce_image_run_name, value = bot_globals.bruteforce_image_run_instructions)
        view = BruteforceImageRun(timeout = None)

        return embed, view

    async def handle_profiles_panel(self, interaction, mode, respond = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_profiles_panel()
            if respond:
                await interaction.respond(embed = embed, view = view)
            else:
                await interaction.response.edit_message(embed = embed, view = view)
            return

        elif mode == bot_globals.COMMAND_BRUTEFORCE_MODE_WEBSITE:

            await interaction.respond("Website bruteforcer not yet implemented.")
            return

        elif mode == bot_globals.COMMAND_BRUTEFORCE_MODE_REVISION:

            await interaction.respond("Revision bruteforcer not yet implemented.")
            return

    async def get_bruteforce_image_profiles_panel(self):

        embed = Embed(color=Color.blurple())
        embed.add_field(name = "Profiles", value = "TBD")
        view = BruteforceImageProfiles(timeout = None)

        return embed, view

    async def handle_edit_profile_panel(self, interaction, mode, respond = False):

        if mode == bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE:

            embed, view = await self.get_bruteforce_image_edit_profile_panel()
            if respond:
                await interaction.respond(embed = embed, view = view)
            else:
                await interaction.response.edit_message(embed = embed, view = view)
            return

        elif mode == bot_globals.COMMAND_BRUTEFORCE_MODE_WEBSITE:

            await interaction.respond("Website bruteforcer not yet implemented.")
            return

        elif mode == bot_globals.COMMAND_BRUTEFORCE_MODE_REVISION:

            await interaction.respond("Revision bruteforcer not yet implemented.")
            return

    async def get_bruteforce_image_edit_profile_panel(self):

        embed = Embed(color=Color.blurple())
        embed.add_field(name = "Edit Profile", value = "TBD")
        view = BruteforceImageEditProfile(timeout = None)

        return embed, view

    async def start_image_bruteforce(self, interaction, image_names, image_extensions, image_prefixes, image_suffixes):

        # Get amount of images we're going to bruteforce
        image_count = len(image_names)
        
        # Iterate over each image name and bruteforce it
        for image_name in image_names:

            # We've been requested to cancel the ongoing operation, so break out from the loop and stop bruteforcing
            if self.cancel_operation:

                # Reset the cancel operation bool
                self.cancel_operation = False

                # Break from the loop
                break

            # Get index of the current image, later used to determine progress
            image_index = image_names.index(image_name)

            # Update our interaction with a progress report
            await self.update_bruteforce_progress(interaction, image_name, image_index, image_count)

            # Bruteforce this image
            await self.bruteforce_image(interaction, image_name, image_extensions, image_prefixes, image_suffixes)

    async def bruteforce_image(self, interaction, image_name, image_extensions, image_prefixes, image_suffixes):

        # Iterate over all of our prefixes to attempt every possible variation
        for prefix in image_prefixes:

            # Break out of the loop if we need to cancel the operation
            if self.cancel_operation:
                break

            # Also iterate over all of our suffixes
            for suffix in image_suffixes:

                # Break out of the loop if we need to cancel the operation
                if self.cancel_operation:
                    break

                # Finally iterate over all the possible file extensions
                for extension in image_extensions:

                    # Break out of the loop if we need to cancel the operation
                    if self.cancel_operation:
                        break

                    # The operation is paused, hold here until further notice
                    while self.pause_operation:
                        asyncio.sleep(1.0)

                    # Construct a url to see whether our possible image exists
                    possible_image = prefix + image_name + suffix + extension
                    url = "https://edgecast.wizard101.com/image/free/Wizard/C/Wizard-Society/Patch-Notes/{possible_image}?v=1".format(possible_image = possible_image)

                    # Check to see if the image exists
                    try:
                        response = await self.http_client.fetch(HTTPRequest(url, follow_redirects = False), raise_error = False)
                    except Exception as e:
                        print("Timed out with url:\n{}".format(url))
                        print(e)
                    response_code = response.code

                    # The image exists
                    if response_code == 200:

                        print(f'{possible_image} exists.')
                        image = resp.body
                        file_path = "cache/{image_name}".format(image_name = possible_image)
                        f = open(file_path, "wb")
                        f.write(image)
                        f.close()

                        file_to_send = File(file_path)

                        await interaction.channel.send("@everyone")
                        await interaction.channel.send("**{image_name}**\n<{image_url}>".format(image_name = possible_image, image_url = url), file = file_to_send)

                    # Cooldown to prevent rate limiting
                    await asyncio.sleep(0.05)

        #await interaction.channel.send("Finished bruteforcing term **{term}**".format(term = term))

    async def update_bruteforce_progress(self, interaction, image_name = None, image_index = None, image_count = None, view = None):

        # We have a bruteforce in-progress
        if not self.cancel_operation and not self.pause_operation and interaction:

            bruteforce_title = "Bruteforce In-Progress"

            # Determine percentage completion based on current image index and image count
            percentage = round(((image_index + 1) / image_count) * 100, 2)
            estimated_time = "TBD"
            bruteforce_info = "__**{image_name}**__ ({image_index} of {image_count})\n__**{percentage}%**__ completed\n__**{estimated_time}**__ until completion".format(image_name = image_name, image_index = image_index, image_count = image_count, percentage = percentage, estimated_time = estimated_time)

            # Embed indicating our progress on the bruteforce
            embed = Embed(color=Color.green())
            embed.add_field(name = bruteforce_title, value = bruteforce_info)

        # Our bruteforce is currently paused
        elif self.pause_operation and interaction:

            bruteforce_title = "Bruteforce Paused"

            # TODO: Temp
            bruteforce_info = "TODO"
            
            # Embed indicating our bruteforce is paused
            embed = Embed(color=Color.red())
            embed.add_field(name = bruteforce_title, value = bruteforce_info)

        # Edit the interaction with our embed
        if view:
            await interaction.message.edit(embed = embed, view = view)
        else:
            await interaction.message.edit(embed = embed)


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

    # Stolen from WizDiff, grabs LatestFileList
    async def get_patch_url(self, server_name):

        url_to_connect = "{server_name}.us.wizard101.com".format(server_name=server_name)

        with create_connection((url_to_connect, 12500)) as socket:
            socket.send(b"\x0D\xF0\x24\x00\x00\x00\x00\x00\x08\x01\x20" + bytes(29))
            socket.recv(4096)
            data = socket.recv(4096)

        def _read_url(start: int):
            str_len_data = data[start:start + 2]
            str_len = struct.unpack("<H", str_len_data)[0]

            str_data = data[start + 2: start + 2 + str_len]

            return str_data.decode()

        file_list_url_start = data.find(b"http") - 2

        return _read_url(file_list_url_start)

    # Stolen from WizDiff, grabs revision from any patcher url
    async def get_revision_from_url(self, url: str):
        res = re.compile(r"WizPatcher/([^/]+)").search(url)

        if res is None:
            raise ValueError(f"Reversion string not found in {url}")

        return res.group(1)

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

    # Used to check whether the Test Realm patcher is online
    async def check_patcher(self):

        # Status code of the patcher
        status_code = 0

        # We're making this a try in the case we cannot cannot (which is actually most of the time)
        try:

            # Make a request to the patcher to determine the status code
            patcher_url = await self.grab_patcher_url()
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
        game_shorthand = bot_globals.game_shorthands.get(game)

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

""""
OLD CODE ABOVE
NEW CODE BELOW
"""

class BruteforceImageControlPanel(View):
    """
    Interface for interacting with the image bruteforcer.

    Run: Displays a view giving you options on how to run the current bruteforce profile. Includes buttons for starting, looping, scheduling, and more.
    Profiles: Displays a view giving you options to manage the current bruteforce profiles. Includes buttons for creating, deleting, editing, and more.
    Settings: Displays a view giving you options to edit the bruteforce settings.

    """

    @button(label = bot_globals.bruteforce_image_run_button, style = ButtonStyle.green)
    async def run(self, button: Button, interaction: Interaction):

        await bot.bruteforcer.handle_run_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    @button(label = "Profiles", style = ButtonStyle.blurple)
    async def profiles(self, button: Button, interaction: Interaction):

        await bot.bruteforcer.handle_profiles_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)

    @button(label = bot_globals.bruteforce_image_settings_button, style = ButtonStyle.grey)
    async def settings(self, button: Button, interaction: Interaction):

        await interaction.response.send_message("Settings not yet implemented.", delete_after=5)


class BruteforceImageRun(View):

    @button(label = "Start", style = ButtonStyle.green)
    async def start_bruteforce(self, button: Button, interaction: Interaction):

        # Grab info about the images we're about to bruteforce
        image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)
        image_extensions = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_EXTENSIONS)
        image_prefixes = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_PREFIXES)
        image_suffixes = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_SUFFIXES)

        # We have no image names queued up to bruteforce
        if not image_names:
            await interaction.response.send_message("No image names to bruteforce!")
            return

        # For some reason, we don't have any image extensions to bruteforce
        if not image_extensions:
            await interaction.response.send_message("No file extensions specified to bruteforce!")
            return

        # Even though we don't technically need any prefixes or suffixes, our system requires at the very least an empty string for each
        # So if we don't even have that, we cann't move forward with the bruteforce
        if not image_prefixes or not image_suffixes:
            await interaction.response.send_message("No image prefixes or suffixes found! Did you remove the empty strings?")
            return

        # Embed indicates a bruteforce is about to begin
        embed = Embed(color=Color.blurple())
        embed.add_field(name = "Starting Bruteforce", value = "Please wait.")

        # Cancel button used to stop the bruteforce at any time
        view = BruteforceImageCancel(timeout = None)

        # Respond that we're about to begin the bruteforce
        await interaction.response.edit_message(embed = embed, view = view)

        # Send our list of images off to be bruteforced
        await bot.bruteforcer.start_image_bruteforce(interaction, image_names, image_extensions, image_prefixes, image_suffixes)

    @button(label = "Loop", style = ButtonStyle.green)
    async def loop_bruteforce(self, button: Button, interaction: Interaction):

        bot.bruteforcer.loop_operation = True

        await interaction.response.defer()

        while bot.bruteforcer.loop_operation:

            current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_PROFILE_NAME)
            current_image_extensions = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_EXTENSIONS)
            current_image_suffixes = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_SUFFIXES)
        
            if not current_image_names:
                await interaction.response.send_message("No image names to bruteforce.")
                return

            time_estimate = len(current_image_names) * len(current_image_extensions) * len(current_image_suffixes) * 0.1
            instructions = "__**{names_amount}**__ names to bruteforce\n__**{time_estimate}**__ estimated time to completion".format(names_amount = len(current_image_names), time_estimate = time_estimate)

            embed = Embed(color=Color.blurple())
            embed.add_field(name = "Bruteforce started", value = instructions)

            view = BruteforceImageCancel(timeout = None)

            await interaction.message.edit(embed = embed, view = view)

            for image_name in current_image_names:

                if bot.bruteforcer.cancel_operation:
                    bot.bruteforcer.cancel_operation = True
                    break

                image_index = current_image_names.index(image_name)
                await bot.bruteforcer.find_images(interaction, embed, view, image_name, image_index, len(current_image_names))

            await asyncio.sleep(10)

    @button(label = "Schedule", style = ButtonStyle.blurple)
    async def schedule_bruteforce(self, button: Button, interaction: Interaction):

        await interaction.response.send_message("Schedule not yet implemented.", delete_after=5)

    @button(label = "Back", style = ButtonStyle.grey)
    async def enter_control_panel(self, button: Button, interaction: Interaction):

        await bot.bruteforcer.handle_control_panel(interaction = interaction, mode = bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)


class BruteforceImageCancel(View):

    @button(label = "Cancel", style = ButtonStyle.red)
    async def cancel_bruteforce(self, button: Button, interaction: Interaction):

        bot.bruteforcer.loop_operation = False
        bot.bruteforcer.cancel_operation = True

        embed, view = await bot.bruteforcer.get_bruteforce_image_control_panel()
        await interaction.response.edit_message(content = None, embed = embed, view = view)

    @button(label = "Pause", style = ButtonStyle.red)
    async def pause_bruteforce(self, button: Button, interaction: Interaction):

        if bot.bruteforcer.pause_operation:
            
            bot.bruteforcer.pause_operation = False

            button.label = "Pause"
            button.style = ButtonStyle.red

            await interaction.response.edit_message(view = self)

        else:

            bot.bruteforcer.pause_operation = True

            button.label = "Resume"
            button.style = ButtonStyle.green

            #await interaction.response.defer()
            #await interaction.message.edit(view = self)
            await bot.bruteforcer.update_bruteforce_progress(interaction, view = self)


class BruteforceImageProfiles(View):

    @button(label = "Switch", style = ButtonStyle.blurple)
    async def switch_profile(self, button: Button, interaction: Interaction):

        # Send a view with options for browsing the list of images
        profile_names = await bot.bruteforcer.get_bruteforce_profile_names(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE)
        switch_profile_view = utils.SelectData(timeout = None,
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


class BruteforceImageEditProfile(View):

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
        view = BruteforceImageEditProfileRemove(timeout = None)
        await interaction.response.edit_message(embed = embed, view = view)

    # Button for browsing the current list of image names
    @button(label = bot_globals.bruteforce_image_browse_terms_button, style = ButtonStyle.blurple)
    async def browse_names(self, button: Button, interaction: Interaction):

        # Send a view with options for browsing the list of images
        current_image_names = await bot.bruteforcer.get_bruteforce_profile_setting(bot_globals.COMMAND_BRUTEFORCE_MODE_IMAGE, bot_globals.BRUTEFORCE_IMAGE_IMAGE_NAMES)
        browse_names_view = utils.BrowseData(timeout = None,
                                             data = current_image_names, 
                                             title = bot_globals.bruteforce_image_browse_terms_name,
                                             back_callback = self.back_callback)
        await browse_names_view.update(interaction)

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


class BruteforceImageEditProfileRemove(View):

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

        embed, view = await bot.bruteforcer.get_bruteforce_image_control_panel()
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

