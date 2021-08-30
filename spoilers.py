# 3rd-Party Packages
from time import sleep
import discord
from PIL import Image
import twitter
from wizdiff.delta import FileDelta
from wizdiff.update_notifier import UpdateNotifier
from wizwalker.file_readers.wad import Wad

# Local packages
import bot_globals

# Built-in packages
import datetime
import os
import threading
import urllib.request
import zlib

# Spoilers
class Spoilers(UpdateNotifier):

    def __init__(self, bot):

        UpdateNotifier.__init__(self)
        
        self.bot = bot
        self.twitter_api = None

    async def startup(self):
        
        # Log into our Twitter account so we can post stuff later
        self.twitter_api = twitter.Api(consumer_key="KMHnLXsOx4Ov8Y4GxF0mBTFph",
                                       consumer_secret="kksTCeqwGAtipvbyqYXH1dEQLzhMAO1ivmu3z7bAT0W5S2W1MN",
                                       access_token_key="1431849304600178689-rqAp9UinhhKWGO7nB6xaKDQyfOuJXS",
                                       access_token_secret="lRAT0SHWiRBtamdsqzyhGQGOvsbSqlfCYSTHZ4X618e6s")

    def notify_wad_file_update(self, delta: FileDelta):
        if delta.name.endswith("_Shared-WorldData.wad"):
            for inner_file_info in delta.changed_inner_files:
                if inner_file_info.name.endswith("Button_World_Karamelle.dds"):
                    if inner_file_info.is_compressed:
                        data_size = inner_file_info.compressed_size
                    else:
                        data_size = inner_file_info.size

                    file_data = self.webdriver.get_url_data(delta.url, data_range=(inner_file_info.file_offset, inner_file_info.file_offset + data_size))

                    if inner_file_info.is_compressed:
                        file_data = zlib.decompress(file_data)

                    with open("Button_World_Karamelle.dds", "wb+") as fp:
                        fp.write(file_data)

    async def join_images_demo(self):

        discord_channel = self.bot.get_channel(814900537966329936)
        await discord_channel.send("Start @ {time}".format(time=datetime.datetime.now().strftime("%H:%M:%S")))

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
        await discord_channel.send("Finish @ {time}".format(time=datetime.datetime.now().strftime("%H:%M:%S")))

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
