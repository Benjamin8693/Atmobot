# 3rd-Party Packages
from discord import Color, Embed, slash_command, Permissions
from discord.ext import commands

# Local packages
import bot_globals

# Built-in packages
import os
import shutil
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

    def cooldown_behavior(message):

        # Users with manage messages perms get to bypass all cooldowns
        if message.author.guild_permissions.manage_messages:
            return None

        # This is a channel with a reduced cooldown
        elif message.channel in bot.reduced_cooldown_channels:
            return commands.Cooldown(1, 3)

        # We have a role that reduces cooldowns
        elif any(role in message.author.roles for role in bot.reduced_cooldown_roles):
            return commands.Cooldown(1, 5)

        # All other users have the regular cooldown
        return commands.Cooldown(1, 15)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def reloadcommands(self, ctx):

        command_module_name = "cogs.public_commands"

        self.bot.reload_extension(command_module_name)

        await ctx.send("Commands reloaded.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def testping(self, ctx):

        await ctx.send("<@&886396512018501733>")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def bruteforce(self, ctx):

        most_recent_version = await self.bot.bruteforcer.most_recent_revision()
        version_list = [bot_globals.fallback_version_dev, most_recent_version]
        revision = await self.bot.bruteforcer.revision_bruteforcer.start(revision_start=most_recent_version, revision_range=bot_globals.default_revision_range, version_list=version_list)
        
        await ctx.send("Revision is {}.".format(revision))

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def tweet(self, ctx, content: str = "", link: str = ""):

        print("{time} | TWEET: {user} submitted tweet draft with content {content} and link {link}".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author), content=content, link=link))

        authorized_poster_ids = settings.get("authorized_posters", [])
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

    # Update Command
    # Automatically pulls the latest commit and restarts Atmobot
    @slash_command(name = "update", description = "Updates Atmobot", guild_ids = [bot.guild_id], default_member_permissions = Permissions(manage_messages = True))
    @commands.dynamic_cooldown(cooldown_behavior, commands.BucketType.user)
    async def update(self, ctx):

        await ctx.respond("Updating Atmobot.")

        final_ouput = ""
        commands_to_run = ("git pull", "sudo pm2 restart Atmobot")
        for command in commands_to_run:
            output = subprocess.getoutput(command)
            final_ouput += output
            final_ouput += "\n"

        await ctx.respond(final_ouput)

    # Restart Command
    # Restarts Atmobot
    @slash_command(name = "restart", description = "Restarts Atmobot", guild_ids = [bot.guild_id], default_member_permissions = Permissions(manage_messages = True))
    @commands.dynamic_cooldown(cooldown_behavior, commands.BucketType.user)
    async def restart(self, ctx):

        await ctx.respond("Restarting Atmobot.")

        final_ouput = ""
        output = subprocess.getoutput("sudo pm2 restart Atmobot")
        final_ouput += output
        final_ouput += "\n"

        await ctx.respond(final_ouput)

    # Stop Command
    # Stops Atmobot
    @slash_command(name = "stop", description = "Stops Atmobot", guild_ids = [bot.guild_id], default_member_permissions = Permissions(manage_messages = True))
    @commands.dynamic_cooldown(cooldown_behavior, commands.BucketType.user)
    async def stop(self, ctx):

        await ctx.respond("Stopping Atmobot.")

        final_ouput = ""
        output = subprocess.getoutput("sudo pm2 stop Atmobot")
        final_ouput += output
        final_ouput += "\n"

        await ctx.respond(final_ouput)

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
    async def restoredb(self, ctx):

        await ctx.send("Restoring database backup.")

        source_directory="resources/database/backup.db"
        destination_directory="wizdiff.db"
        shutil.copy(source_directory, destination_directory)

        await ctx.send("Restored database backup.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def backupdb(self, ctx):

        await ctx.send("Backing up current database.")

        source_directory="wizdiff.db"
        destination_directory="resources/database/backup.db"
        shutil.copy(source_directory, destination_directory)

        await ctx.send("Backed database up.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def testdb(self, ctx):

        await ctx.send("Copying over reliable test database.")

        source_directory="resources/database/wizdiff-V_r707528.Wizard_1_460.db"
        destination_directory="wizdiff.db"
        shutil.copy(source_directory, destination_directory)

        await ctx.send("Now using test database.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def initdb(self, ctx):

        await ctx.send("Initializing database.")
        await self.bot.spoilers.init_db()
        await ctx.send("Database initialized.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def autospoil(self, ctx):

        print("{time} | SPOILERS: {user} requested to toggle autospoil mode".format(time=await self.bot.get_formatted_time(), user=await self.get_full_username(ctx.author)))

        state = await self.bot.spoilers.get_state()
        state = not state
        state_name = "enabled" if state else "disabled"

        print("{time} | SPOILERS: Autospoil mode has been {state}".format(time=await self.bot.get_formatted_time(), state=state_name))
        await ctx.send("{state} autospoil mode.".format(state=state_name.capitalize()))

        await self.bot.spoilers.update_loop(state)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def spoil(self, ctx, revision: str = ""):

        version_to_spoil = "latest revision"
        if revision:
            version_to_spoil = "revision {revision}".format(revision=revision)

        print("{time} | SPOILERS: Attempting to spoil {version_to_spoil}".format(time=await self.bot.get_formatted_time(), version_to_spoil=version_to_spoil))
        await ctx.send("Attempting to spoil {version_to_spoil}.".format(version_to_spoil=version_to_spoil))

        await self.bot.spoilers.handle_revision(revision=revision)

        print("{time} | SPOILERS: Finished spoiling {version_to_spoil}".format(time=await self.bot.get_formatted_time(), version_to_spoil=version_to_spoil))
        await ctx.send("Finished spoiling {version_to_spoil}.".format(version_to_spoil=version_to_spoil))

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def testcheck(self, ctx):

        await ctx.send("Checking for Test Realm")

        await self.bot.bruteforcer.start_test_realm_check()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def revisiontest(self, ctx, revision_start: str, revision_range: str):

        await ctx.send("Bruteforcing starting at revision {} through revision {}".format(revision_start, (int(revision_start) + int(revision_range))))

        patch_url = "http://versionec.us.wizard101.com/WizPatcher/V_r{revision}.{version}/Windows/LatestFileList.bin"
        new_revisions = await self.bot.bruteforcer.start_revision_brutefore(patch_url, int(revision_start), int(revision_range), ["Wizard_1_490"])

        if new_revisions:
            await ctx.send("Revisions: {}".format(new_revisions))
        else:
            await ctx.send("No new revisions")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def restoreben(self, ctx):

        member = await ctx.guild.fetch_member(104405233987235840)
        role = ctx.guild.get_role(786274093036732517)
        await member.add_roles(role)

        await ctx.send("Benjamin has Minimod once more.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def setdelay(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def testtweet(self, ctx, message: str):

        self.bot.spoilers.twitter_api_v2.create_tweet(text=message)
        await ctx.send(f"Tweeted message '{message}'.")

# Used for connecting the Command Center to the rest of the bot
def setup(bot):
    bot.add_cog(PrivateCommands(bot=bot))
