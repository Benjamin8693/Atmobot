# 3rd-Party Packages
from discord import Intents, Embed, Color, file
import discord
from discord.ext import commands
from discord.ext.commands.core import command
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

# Local packages
import bot_globals

# Built-in packages
import datetime
import os
import random
import time
import typing

class CommandCenter(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.patcher_historicals = []
        self.website_historicals = []

    async def get_full_username(self, user):
        user_name = user.name
        user_discriminator = user.discriminator

        full_username = "{user_name}#{user_discriminator}".format(user_name=user_name, user_discriminator=user_discriminator)
        return full_username

    async def get_formatted_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    @commands.command()
    async def uptime(self, ctx):

        # Logging
        print("{time} | UPTIME: {user} requested bot uptime.".format(time=await self.get_formatted_time(), user=await self.get_full_username(ctx.message.author)))

        # Find how much time has elasped since we started the bot
        current_time = datetime.datetime.now()
        elasped_time = current_time - self.bot.startup_time

        # Format the elasped time properly
        days_formatted = elasped_time.days
        hours_formatted = elasped_time.seconds // 3600
        minutes_formatted = elasped_time.seconds // 60 % 60
        seconds_formatted = elasped_time.seconds % 60

        # Send the uptime
        await ctx.send("Atmobot uptime: {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds".format(days=days_formatted, hours=hours_formatted, minutes=minutes_formatted, seconds=seconds_formatted))

        # Log the result
        print("{time} | UPTIME: Bot has been up for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds.".format(time=await self.get_formatted_time(), days=days_formatted, hours=hours_formatted, minutes=minutes_formatted, seconds=seconds_formatted))

    @commands.command()
    async def meme(self, ctx):

        # Logging
        print("{time} | MEME: {user} requested a meme.".format(time=await self.get_formatted_time(), user=await self.get_full_username(ctx.message.author)))

        # Path to get our memes from
        current_path = os.path.join(os.getcwd(), bot_globals.resources_path)

        # Pick a random file
        all_files = [x for x in list(os.scandir(current_path)) if x.is_file()]
        random_file = random.choice(all_files).name

        # Generate a file path and send the file
        file_path = os.path.join(current_path, random_file)
        file_to_send = discord.File(file_path)
        await ctx.send(file=file_to_send)

        # Log the result
        print("{time} | MEME: Random meme '{file_path}' uploaded.".format(time=await self.get_formatted_time(), file_path=random_file))

    @commands.command()
    async def deepfake(self, ctx, directory: typing.Optional[str]):

        # Logging
        print("{time} | DEEPFAKE: {user} requested a deepfake with directory {directory}.".format(time=await self.get_formatted_time(), user=await self.get_full_username(ctx.message.author), directory=directory))

        # Path to get our deepfakes from
        current_path = os.path.join(os.getcwd(), bot_globals.resources_path, bot_globals.deepfakes_path)

        def get_all_directories(return_as_strings=False):
            directories_to_return = []

            all_directories = [(x) for x in list(os.scandir(current_path)) if x.is_dir()]

            if return_as_strings:
                for directory in all_directories:
                    directories_to_return.append(directory.name)
            else:
                directories_to_return = all_directories

            return directories_to_return

        # The user wants to know about our deepfake categories
        if directory and directory.lower() == "list":

            # Grab all the directories
            all_directories = get_all_directories(return_as_strings=True)
            categories_string = ", ".join(all_directories)

            # Relay our categories back to them
            await ctx.send("Deepfake categories: {}".format(categories_string))

            # Log the result
            print("{time} | DEEPFAKE: Deepfake categories requested, returning category list '{category_list}'.".format(time=await self.get_formatted_time(), category_list=categories_string))

            return

        # If the user specifies a directory that doesn't exist, let them know
        elif directory and not os.path.exists(os.path.join(bot_globals.resources_path, bot_globals.deepfakes_path, directory)):

            # Send the message
            await ctx.send("Deepfake category '{}' does not exist!".format(directory))

            # Log the result
            print("{time} | DEEPFAKE: Deepfake category '{category}' requested, but does not exist.".format(time=await self.get_formatted_time(), category=directory))

            return

        # But if they specify a directory and it DOES exist, pick a random file from it
        elif directory and os.path.exists(os.path.join(bot_globals.resources_path, bot_globals.deepfakes_path, directory)):

            # Pick a random file
            all_files = [x for x in list(os.scandir(os.path.join(current_path, directory)))]
            random_file = random.choice(all_files).name

        # Otherwise just pick a random file AND directory
        else:

            # Pick a random directory
            all_directories = get_all_directories()
            directory = random.choice(all_directories).name

            # Pick a random file
            all_files = [x for x in list(os.scandir(os.path.join(current_path, directory)))]
            random_file = random.choice(all_files).name

        # Generate a file path and send the file
        file_path = os.path.join(current_path, directory, random_file)
        file_to_send = discord.File(file_path)
        await ctx.send(file=file_to_send)

        # Log the result
        print("{time} | DEEPFAKE: Deepfake '{file_path}' uploaded.".format(time=await self.get_formatted_time(), file_path=random_file))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def website(self, ctx):
        website_change = self.bot.checker.check_url_status()

        if not website_change:
            await ctx.send("No website change.")
        else:
            await ctx.send("Website change!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def patcher(self, ctx):
        response_code = self.bot.checker.check_patcher()

        await ctx.send("Patcher error code is {}".format(response_code))

    # Generates a set of buttons users can click on to check Test Realm status manually
    @commands.command()
    @commands.has_permissions(administrator=True)
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
            response_code = self.bot.checker.check_patcher()
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

            website_change = self.bot.checker.check_url_status()
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
    bot.add_cog(CommandCenter(bot=bot))
