# 3rd-Party Packages
from discord import Color, Embed
from discord.ext import commands
from discord_components import Button, ButtonStyle, InteractionType

# Local packages
import bot_globals

# Built-in packages
import subprocess
import sys
import traceback
import typing

class PrivateCommands(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        await self.handle_error(ctx, error)

    async def cog_command_error(self, ctx, error):
        await self.handle_error(ctx, error)

    async def handle_error(self, ctx, error):

        # Errors to ignore
        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return

        # Cooldown error
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_embed = Embed(title=f"You are on cooldown.", description=f"Try again in {error.retry_after:.2f}s.", color=Color.red())
            await ctx.send(embed=cooldown_embed)

        # Print traceback
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def get_full_username(self, user):
        user_name = user.name
        user_discriminator = user.discriminator

        full_username = "{user_name}#{user_discriminator}".format(user_name=user_name, user_discriminator=user_discriminator)
        return full_username

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def reactbutton(self, ctx):
        
        # Embed header
        initial_embed = Embed(title="Test Realm Notifications", color=Color.blurple())

        # Disclaimer so people don't flip their shit and take the bot as gospel
        initial_embed.add_field(name="About",
                                value=f"Anyone with the \"Test Realm Status\" role will be pinged in the event of any Test Realm news. Click the button below to add or remove the role from yourself.",
                                inline=False)

        # Explains what the patcher status actually is
        initial_embed.add_field(name="Warning",
                                value=f"Most pings will be automaticaly sent by Atmobot. There is a possibility something could go wrong, resulting in inaccurate notifications. If this happens, please bear with us!",
                                inline=False)

        # Buttons to check the patcher status (technically there are two, but one is always invisible)
        get_role_button = Button(style=ButtonStyle.blue, label="Toggle Role")

        # Send the embed
        message = await ctx.send(embed=initial_embed, components=[get_role_button])

        # We only care about button presses in the channel our message was sent in
        def check(response):
            return response.channel == ctx.channel

        # Wait for the button press
        res = await self.bot.wait_for("button_click", check=check)

        # Handle the patcher button
        if res.component.label.startswith("Patcher"):

            return

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def run(self, ctx, *args):

        command =  " ".join(args[:])

        if not command:
            await ctx.send("No command specified.")
            return
        
        output = subprocess.getoutput(command)
        if not output:
            output = "Command run with no output."
        await ctx.send(output)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spoilers(self, ctx):
        await self.bot.spoilers.test_file_update()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: str = "1"):

        # Logging
        print("{time} | CLEAR: {user} requested to clear {amount} messages from {channel_name}".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author), amount=amount, channel_name=ctx.message.channel.name))

        # Make sure an actual digit was provided
        if not amount.isdigit():
            return
        amount = int(amount)

        # Delete the messages
        await ctx.channel.purge(limit=amount)

        # Send notification in the channel that the messages were deleted
        await ctx.send("{amount} messages cleared.".format(amount=amount), delete_after=5)

        # Log the result
        print("{time} | CLEAR: Cleared {amount} messages from {channel_name}".format(time=await self.bot.get_formatted_time(), amount=amount, channel_name=ctx.message.channel.name))

# Used for connecting the Command Center to the rest of the bot
def setup(bot):
    bot.add_cog(PrivateCommands(bot=bot))
