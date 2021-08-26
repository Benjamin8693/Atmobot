# 3rd-Party Packages
import discord
from PIL import Image
from wizwalker.file_readers.wad import Wad

# Built-in packages
import asyncio
import os
import urllib.request

# Spoilers
class Spoilers:

    def __init__(self, bot):
        
        self.bot = bot

    async def unpack(self):

        revision = self.bot.bot_settings.get("latest_revision")
        discord_channel = self.bot.get_channel(814898239647776798)

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
