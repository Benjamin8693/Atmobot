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

        self.tweet_queue = {}

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
    async def tweet(self, ctx, content: str = "", link: str = ""):

        print("{time} | TWEET: {user} submitted tweet draft with content {content} and link {link}".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author), content=content, link=link))

        authorized_poster_ids = settings.get("authorized_poster_ids", [])
        if ctx.author.id not in authorized_poster_ids:
            print("{time} | TWEET: {user} attempted to draft tweet but is not authorized".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))
            await ctx.send("Unauthorized poster.")
            return
        
        # Embed header
        initial_embed = Embed(title="Proposed Tweet", color=Color.orange())

        # Contents of the proposed tweet
        initial_embed.add_field(name="Content", value=content, inline=False)

        # List all of the image links that would go out with this tweet
        if link:
            initial_embed.add_field(name="Attached Image Link", value=link, inline=False)

        initial_embed.add_field(name="Author", value=await self.get_full_username(ctx.author), inline=False)

        vote_string = ""
        for poster in authorized_poster_ids:

            poster_name = await self.get_full_username(ctx.message.guild.get_member(poster))
            vote_string += "{poster_name} - Awaiting Response".format(poster_name=poster_name)

            index = authorized_poster_ids.index(poster)
            if index + 1 != len(authorized_poster_ids):
                vote_string += "\n"

        initial_embed.add_field(name="Votes", value=vote_string, inline=False)

        # Button to approve the tweet
        approve_button = Button(style=ButtonStyle.green, label="Approve Tweet")

        # Button to deny the tweet
        deny_button = Button(style=ButtonStyle.red, label="Deny Tweet")

        # Send the embed
        await ctx.send(embed=initial_embed, components=[approve_button, deny_button])

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def reactbutton(self, ctx):
        
        # Embed header
        initial_embed = Embed(title="Test Realm Notifications", color=Color.blurple())

        # Describe what this role is for
        initial_embed.add_field(name="About",
                                value=f"Anyone with the \"Test Realm Status\" role will be pinged in the event of any Test Realm news. Click the button below to add or remove the role from yourself.",
                                inline=False)

        # Warn people that it may not always be accurate
        initial_embed.add_field(name="Warning",
                                value=f"Most pings will be automatically sent by Atmobot. There is a possibility something could go wrong, resulting in inaccurate notifications. If this happens, please bear with us!",
                                inline=False)

        # Button that toggles the role on a user
        get_role_button = Button(style=ButtonStyle.blue, label="Toggle Role")

        # Send the embed
        await ctx.send(embed=initial_embed, components=[get_role_button])

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def update(self, ctx):

        await ctx.send("Updating Atmobot.")

        final_ouput = ""
        commands_to_run = ("git pull", "sudo pm2 restart Atmobot")
        for command in commands_to_run:
            output = subprocess.getoutput(command)
            final_ouput += output
            final_ouput += "\n"

        await ctx.send(final_ouput)

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
    @commands.has_permissions(manage_messages=True)
    async def spoilers(self, ctx):
        await self.bot.spoilers.test_file_update()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def updateloop(self, ctx):
        await self.bot.spoilers.update_loop()

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
