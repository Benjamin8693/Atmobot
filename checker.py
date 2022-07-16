# 3rd Party Packages
from discord import ButtonStyle, Color, Embed, Interaction, Optional, File
from discord.ui import InputText, Modal, Item, View, Button, button

# Local packages
import os
import bot_globals
import bruteforcer

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

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import asyncio


class Checker:

    def __init__(self, bot):
        
        self.bot = bot
        #self.revision_bruteforcer = bruteforcer.Bruteforcer(self.bot)

        #self.url_cache = {}
       
    async def startup(self):

        self.load_checker()

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

    def load_checker(self):

        # If we don't have a checker config file, generate one
        if not os.path.isfile(bot_globals.checker_path):
            with open(bot_globals.checker_path, "w") as data:
                json.dump(bot_globals.checker_template, data, indent=4)

        # Load our checker config
        with open(bot_globals.checker_path) as data:
            self.checker_config = json.load(data)

    async def update_checker_config(self, config_name, variable_to_replace):

        # We typically shouldn't be updating a config variable that doesn't already exist
        if config_name not in self.checker_config:
            print("Updated config variable '{}' that does not exist!".format(config_name))

        # Update the config variable
        self.checker_config[config_name] = variable_to_replace

        # Save our config
        self.save_checker_config()

    def save_checker_config(self):

        # Write to the checker config file
        with open(bot_globals.checker_path, "w") as data:
            json.dump(self.checker_config, data, indent=4)

    async def find_images(self, interaction, term):

        # Http client
        conn = AsyncHTTPClient()

        # Load suffixes and extensions to check
        suffixes = self.checker_config.get("image_suffixes")
        extensions = self.checker_config.get("image_extensions")

        def get_percentage(percentage):

            formatted_percentage = round(percentage * 100, 2)

            return "Bruteforcing term **{term}**: {percentage}%".format(term = term, percentage = formatted_percentage)

        percentage_message = await interaction.channel.send(get_percentage(0))

        # Iterate over all of our suffixes to attempt every possible variation
        for suffix in suffixes:

            # Update the percantage
            suffix_count = suffixes.index(suffix) + 1
            percentage = suffix_count / len(suffixes)
            await percentage_message.edit(content=get_percentage(percentage))

            # Also iterate over every possible file extension we're looking for
            for extension in extensions:

                # Name of the possible file
                short_url = term + suffix + extension

                # Generate a url and check to see whether the image exists
                url = "https://edgecast.wizard101.com/image/free/Wizard/C/Wizard-Society/Patch-Notes/{short_url}?v=1".format(short_url = short_url)
                resp = await conn.fetch(HTTPRequest(url, follow_redirects=False), raise_error=False)

                # Grab response code from the request
                response = resp.code

                # The image exists
                if response == 200:

                    print(f'{short_url} exists.')
                    image = resp.body
                    file_path = "cache/{image_name}".format(image_name = short_url)
                    f = open(file_path, "wb")
                    f.write(image)
                    f.close()

                    file_to_send = File(file_path)
                    await interaction.channel.send("**{image_name}**\n<{image_url}>".format(image_name = short_url, image_url = url), file = file_to_send)

                # Cooldown to prevent rate limiting
                await asyncio.sleep(0.25)

        await interaction.channel.send("Finished bruteforcing term **{term}**".format(term = term))


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


class ImageRunView(View):

    @button(label = "Start", style = ButtonStyle.green)
    async def start_bruteforce(self, button: Button, interaction: Interaction):

        current_image_names = bot.checker.checker_config.get("image_names", [])
    
        if not current_image_names:
            await interaction.response.send_message("No image names to bruteforce.")
            return

        await interaction.response.send_message("Bruteforce started.")

        for image_name in current_image_names:
            await bot.checker.find_images(interaction, image_name)

        await interaction.channel.send("Bruteforce completed.")

        #await interaction.response.send_message("Start not yet implemented.")

    @button(label = "Schedule", style = ButtonStyle.blurple)
    async def schedule_bruteforce(self, button: Button, interaction: Interaction):

        await interaction.response.send_message("Schedule not yet implemented.", delete_after=5)

    
class ImagePopIndexModal(Modal):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(InputText(label="Index", placeholder = "1"))

    async def callback(self, interaction: Interaction):

        # Current image names
        current_image_names = bot.checker.checker_config.get("image_names", [])

        # Image index to pop
        image_index = self.children[0].value

        # Only pop the index if an integer was specified
        if image_index.isdigit():

            # The index can only be between 1 and the length of the image name list
            if 1 <= int(image_index) <= len(current_image_names):

                popped_image_name = current_image_names.pop(int(image_index) - 1)
                await bot.checker.update_checker_config("image_names", current_image_names)

                await interaction.response.send_message("Popped **{popped_image_name}** from the list.".format(popped_image_name = popped_image_name), delete_after=5)
                
                return

        await interaction.response.send_message("Invalid index specified.", delete_after=5)


class ImageRemovalView(View):

    # Button for clearing all names from the image bruteforce list
    @button(label = "Clear", style = ButtonStyle.red)
    async def clear_all(self, button: Button, interaction: Interaction):

        current_image_names = bot.checker.checker_config.get("image_names", [])

        # Empty the list of image names
        await bot.checker.update_checker_config("image_names", [])

        # Relay message that the list has been cleared
        if current_image_names:
            await interaction.response.send_message("Cleared all image names.", delete_after=5)

        else:
            await interaction.response.send_message("No image names available to clear.", delete_after=5)

    # Button for removing the name at the front of the image bruteforce list
    @button(label = "Pop First", style = ButtonStyle.red)
    async def pop_front(self, button: Button, interaction: Interaction):

        current_image_names = bot.checker.checker_config.get("image_names", [])

        if current_image_names:
            popped_image_name = current_image_names.pop(0)
            await bot.checker.update_checker_config("image_names", current_image_names)

            await interaction.response.send_message("Popped **{popped_image_name}** from front of list.".format(popped_image_name = popped_image_name), delete_after=5)

        else:

            await interaction.response.send_message("No image names available to pop.", delete_after=5)

    # Button for removing the name at the back of the image bruteforce list
    @button(label = "Pop Last", style = ButtonStyle.red)
    async def pop_back(self, button: Button, interaction: Interaction):

        current_image_names = bot.checker.checker_config.get("image_names", [])

        if current_image_names:
            popped_image_name = current_image_names.pop()
            await bot.checker.update_checker_config("image_names", current_image_names)

            await interaction.response.send_message("Popped **{popped_image_name}** from back of list.".format(popped_image_name = popped_image_name), delete_after=5)

        else:

            await interaction.response.send_message("No image names available to pop.", delete_after=5)

    # Button for removing the name at the specified index
    @button(label = "Pop Specific", style = ButtonStyle.red)
    async def pop_index(self, button: Button, interaction: Interaction):

        current_image_names = bot.checker.checker_config.get("image_names", [])

        if current_image_names:
            
            modal = ImagePopIndexModal(title = "Type an image index to pop.")
            await interaction.response.send_modal(modal)

        else:

            await interaction.response.send_message("No image names available to pop.", delete_after=5)


class ImageInputModal(Modal):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(InputText(label="Image Name", placeholder = "NewPVPArena"))

    async def callback(self, interaction: Interaction):

        # Current image names
        current_image_names = bot.checker.checker_config.get("image_names", [])

        # Image name to add
        image_name = self.children[0].value

        # We don't want to add an image name already in the list
        if image_name in current_image_names:

            await interaction.response.send_message("**{image_name}** already exists in bruteforce list.".format(image_name = image_name), delete_after=5)
            return

        if len(image_name) > 50:

            await interaction.response.send_message("Image name is too long to add!", delete_after=5)
            return

        current_image_names.append(image_name)
        await bot.checker.update_checker_config("image_names", current_image_names)

        await interaction.response.send_message("Added image name **{image_name}** to bruteforce list.".format(image_name = image_name), delete_after=5)


class ImageBruteforcer(View):

    # Button for adding possible image names to the bruteforce list
    @button(label = bot_globals.command_bruteforce_image_button_add, style = ButtonStyle.green)
    async def bruteforce_(self, button: Button, interaction: Interaction):

        # Send a modal requesting the name of an image to bruteforce
        modal = ImageInputModal(title = "Type an image name to bruteforce.")
        await interaction.response.send_modal(modal)

    # Button for removing image names to bruteforce
    @button(label = "Remove", style = ButtonStyle.red)
    async def remove_image(self, button: Button, interaction: Interaction):

        instructions = "__**Clear**__ all names from the bruteforce list\n__**Pop the First**__ name from the bruteforce list\n__**Pop the Last**__ name from the bruteforce list\n__**Pop a Specific**__ name from the bruteforce list"

        view_embed = Embed(color=Color.blurple())
        view_embed.add_field(name = "Remove", value = instructions, inline=False)

        image_removal_view = ImageRemovalView()
        await interaction.response.send_message(embed=view_embed, view = image_removal_view)

    # Button for scheduling image bruteforce routines
    @button(label = "Run", style = ButtonStyle.blurple)
    async def run_check(self, button: Button, interaction: Interaction):

        image_run_view = ImageRunView()
        await interaction.response.send_message("**Run Bruteforce**", view = image_run_view)

    # Button for viewing the current list of image names
    @button(label = "View", style = ButtonStyle.grey)
    async def view_images(self, button: Button, interaction: Interaction):

        image_list = ""
        current_image_names = bot.checker.checker_config.get("image_names", [])
        for image_name in current_image_names:
            index = current_image_names.index(image_name)
            image_list += "__**#{image_index}**__ {image_name}\n".format(image_index = index + 1, image_name = image_name)

        # Create an embed
        view_embed = Embed(color=Color.blurple())
        view_embed.add_field(name = "Bruteforce List", value = image_list, inline=False)

        # Respond with the embed
        await interaction.response.send_message(embed=view_embed)

    # Button for changing the image bruteforce settings
    @button(label = "Settings", style = ButtonStyle.grey)
    async def settings_callback(self, button: Button, interaction: Interaction):

        await interaction.response.send_message("Settings not yet implemented.", delete_after=5)
