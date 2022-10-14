# 3rd-Party Packages
from discord import Color, Embed
from discord.ext import commands
from discord_components import Button, ButtonStyle, InteractionType

# Local packages
import bot_globals

# Built-in packages
import datetime
import time

class DeprecatedCommands(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.patcher_historicals = []
        self.website_historicals = []

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def website(self, ctx):
        website_change = await self.bot.bruteforcer.check_url_status()

        if not website_change:
            await ctx.send("No website change.")
        else:
            await ctx.send("Website change!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def patcher(self, ctx):
        response_code = await self.bot.bruteforcer.check_patcher()

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
            response_code = await self.bot.bruteforcer.check_patcher()
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

            website_change = await self.bot.bruteforcer.check_url_status()
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

# Used for connecting the this Cog to the rest of the bot
def setup(bot):
    bot.add_cog(DeprecatedCommands(bot=bot))
