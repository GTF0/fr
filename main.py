import discord 
from discord.ext import commands
import os 
import sys 
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from discord import Embed
# all intents are going to be given for this bot
intents = discord.Intents.all()

client = commands.Bot(command_prefix='.', intents=intents, help_command=None) # prefix = "" defined the client.


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the world burn"), status=discord.Status.idle)
    print(f'{client.user} is ready')



# Set the cooldown period to 5 minutes
cooldown = timedelta(minutes=5)

# Keep track of the time of the last join event
last_join = None

@client.event
async def on_member_join(member):
    global last_join

    # Check if the cooldown period has passed since the last join
    if last_join is not None and datetime.utcnow() - last_join < cooldown:
        return

    try:
        # Get the welcome channel ID from the environment variable
        welcome_channel_id = int(os.environ.get('welcome_channel'))

        # Find the welcome channel
        welcome_channel = client.get_channel(welcome_channel_id)

        # Log the join in the console
        print(f'{member.name} has joined the server.')

        # Send a welcome message in the welcome channel
        await welcome_channel.send(f'welcome {member.mention}')

        # Update the time of the last join event
        last_join = datetime.utcnow()
    except Exception as e:
        # Log any errors that occur
        print(f'An error occurred: {e}')


@client.event # autorole event 
async def on_member_join(member):
    autorole_id = int(os.getenv('AUTOROLE_ID'))
    role = member.guild.get_role(autorole_id)
    try:
        await member.add_roles(role)
    except discord.Forbidden:
        pass

# Define the number of mentions threshold
MENTION_THRESHOLD = 6

# Define the timeout duration
TIMEOUT_DURATION = 300  # in seconds

# Event for detecting mass mentions
@client.event
async def on_message(message):
    # Check if the message author is a bot or if the message is a DM
    if message.author.bot or not message.guild:
        return

    # Check the number of mentions in the message
    mention_count = sum(1 for user in message.mentions if not user.bot)
    bot_mention_count = sum(1 for user in message.mentions if user.bot)
    total_mentions = mention_count + bot_mention_count

    # Check if the total number of mentions exceeds the threshold
    if total_mentions >= MENTION_THRESHOLD:
        # Delete the message
        await message.delete()

        # Remove the user's send message permission
        await message.author.add_roles(discord.utils.get(message.guild.roles, name="Muted"))

        # Set a timeout for the user
        await asyncio.sleep(TIMEOUT_DURATION)

        # Remove the user's muted role
        await message.author.remove_roles(discord.utils.get(message.guild.roles, name="Muted"))

        # Send a response message
        response_message = f"{message.author.mention} has been muted for {TIMEOUT_DURATION/60} minutes for mass mentioning."
        await message.channel.send(response_message)


# commands start here 

@client.command()
async def mutesetup(ctx):
    # Check if mute role already exists
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role:
        await ctx.send("Mute role already exists!")
        return

    # Start mute setup
    setup_message = await ctx.send("Initiating the mute setup... :orange_circle:")

    # Get list of text channels and voice channels
    text_channels = []
    voice_channels = []
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            text_channels.append(channel)
        elif isinstance(channel, discord.VoiceChannel):
            voice_channels.append(channel)

    # Update setup message with channel count
    await setup_message.edit(content=f"Initiating the mute setup... :green_circle: Detected {len(text_channels)} text channels and {len(voice_channels)} voice channels.")

    # Create mute role
    await setup_message.edit(content="Initiating the mute setup... :orange_circle: Creating mute role...")
    mute_role = await ctx.guild.create_role(name="Muted")

    # Set mute role permissions
    for channel in text_channels:
        await channel.set_permissions(mute_role, send_messages=False)
    for channel in voice_channels:
        await channel.set_permissions(mute_role, speak=False, connect=False)

    # Update setup message with mute role creation
    await setup_message.edit(content="Initiating the mute setup... :green_circle: Created mute role!")

    # Finish setup
    await setup_message.edit(content="Initiating the mute setup process... :orange_circle: Edited number/channel amount for mute role! :green_circle: Completed mute role setup!")

@client.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    # Get the BOT_OWNER_ID from the environment variable
    bot_owner_id = int(os.getenv('BOT_OWNER_ID'))

    # Check if the command is executed by the bot owner
    if ctx.author.id == bot_owner_id:
        # Kick the member with the provided reason
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked.")

@client.command()
async def mute(ctx, member: discord.Member, duration: int, *, reason=None):
    # Get the BOT_OWNER_ID from the environment variable
    bot_owner_id = int(os.getenv('BOT_OWNER_ID'))

    # Check if the command is executed by the bot owner
    if ctx.author.id == bot_owner_id:
        # Get the muted role or create it if it doesn't exist
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")

            # Set the permissions for the muted role
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        # Add the muted role to the member
        await member.add_roles(muted_role, reason=reason)

        # Set a timeout for the mute
        await asyncio.sleep(duration)

        # Remove the muted role from the member
        await member.remove_roles(muted_role, reason="Mute timeout")

        await ctx.send(f"{member.mention} has been muted for {duration} seconds.")

@client.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    bot_owner_id = int(os.getenv('BOT_OWNER_ID'))
    if ctx.author.id == bot_owner_id:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned.")
    else:
        await ctx.send("You are not authorized to use this command.") 








@client.command()
async def kswitch(ctx): # kills the bot exiting the proccess 
    bot_owner_id = int(os.getenv('BOT_OWNER_ID'))
    if ctx.author.id == bot_owner_id:
        await ctx.reply("Terminating the bot...")

        # closes the client
        await client.close()
    else:
        await ctx.reply("lol good try man.")


# Define the links as variables
group_chat_link = 'https://t.me/HellGore'
tutorial_link = 'https://t.me/howtoviewthegroup'

@client.command()
async def tele(ctx):
    # Create a new Embed object
    embed = Embed(title='sension Telegram groups', color=000000)

    # Add fields to the embed
    embed.add_field(name='Group chat', value=f'[Click Here]({group_chat_link})')
    embed.add_field(name='\u200b', value='\u200b') # Add empty field for spacing
    embed.add_field(name='Instructions', value=f'Make sure to join our Telegram chat. It is the backup to our server and your ticket back to the server in case it gets deleted by Discord. If you aren\'t able to join right now, bookmark it until the server is deleted, and join then.\n\nIf you cannot view the group chat on mobile check out [this tutorial]({tutorial_link}).')

    # Set the thumbnail for the embed
    embed.set_thumbnail(url='https://telegram.org/img/t_logo.png')

    # Send the embed as a reply to the command
    await ctx.reply(embed=embed)


########################## ANTI NUKE SYSTEM ##############################

# Define the list of dangerous permission flags
DANGEROUS_PERMISSIONS = ['administrator', 'ban_members', 'kick_members', 'manage_channels', 'manage_roles', 'manage_guild', 'manage_emojis_and_stickers', 'manage_webhooks']

# Define the timeout duration
TIMEOUT_DURATION = timedelta(days=1)

# Define the user tracking dictionary
user_tracking = {}


# Event for tracking member bans
@client.event
async def on_member_ban(guild, user):
    # Check if the user is a bot
    if user.bot:
        return

    # Get the current timestamp
    current_time = datetime.utcnow()

    # Get the user's previous ban history
    previous_bans = user_tracking.get(user.id, [])

    # Remove any ban records that are older than 10 minutes
    for i in range(len(previous_bans) - 1, -1, -1):
        ban_time = previous_bans[i]
        if current_time - ban_time > timedelta(minutes=10):
            previous_bans.pop(i)

    # Add the current ban to the user's history
    previous_bans.append(current_time)
    user_tracking[user.id] = previous_bans

    # Check if the user has banned too many members in a short amount of time
    if len(previous_bans) >= 3:
        # Remove the user's dangerous permissions
        for role in user.roles:
            for permission in role.permissions:
                if permission[0] in DANGEROUS_PERMISSIONS and permission[1]:
                    try:
                        await role.edit(permissions=discord.Permissions.none())
                    except discord.Forbidden:
                        pass
                        # You can add a response message here saying that the bot couldn't remove the user's dangerous permissions due to insufficient permissions
                    break

        # DM the user
        await user.send("you are fucked. just wait until I get online to rape your fucking ass.")

        # Log the response message
        response_message = f"Prevented {user.mention} from nuking the server. Response time: {round(client.latency * 1000)}ms"
        await guild.system_channel.send(response_message)

# Event for tracking member kicks
@client.event
async def on_member_remove(member):
    # Check if the member is a bot
    if member.bot:
        return

    # Get the current timestamp
    current_time = datetime.utcnow()

    # Get the member's previous kick history
    previous_kicks = user_tracking.get(member.id, [])

    # Remove any kick records that are older than 10 minutes
    for i in range(len(previous_kicks) - 1, -1, -1):
        kick_time = previous_kicks[i]
        if current_time - kick_time > timedelta(minutes=10):
            previous_kicks.pop(i)

    # Add the current kick to the member's history
    previous_kicks.append(current_time)
    user_tracking[member.id] = previous_kicks

    # Check if the member has kicked too many members in a short amount of time
    if len(previous_kicks) >= 3:
        # Remove the member's dangerous permissions
        for role in member.roles:
            for permission in role.permissions:
                if permission[0] in DANGEROUS_PERMISSIONS and permission[1]:
                    try:
                        await role.edit(permissions=discord.Permissions.none())
                    except discord.Forbidden:
                        pass
                        # You can add a response message here saying that the bot couldn't remove the member's dangerous permissions due to insufficient permissions
                    break

        # DM the server owner
        server_owner = await member.guild.fetch_owner()
        await server_owner.send(f"Warning: {member.mention} has been removing too many members. Their dangerous permissions have been removed.")

        # Log the response message
        response_message = f"Prevented {member.mention} from kicking more members. Response time: {round(client.latency * 1000)}ms"
        await member.guild.system_channel.send(response_message)

@client.event
async def on_channel_create(channel):
    # Check if the channel is a DM channel or a category
    if isinstance(channel, discord.DMChannel) or isinstance(channel, discord.CategoryChannel):
        return

    # Get the current timestamp
    current_time = datetime.utcnow()

    # Get the user's previous channel creation history
    previous_creations = user_tracking.get(channel.guild.owner.id, {}).get('channel_creations', [])

    # Remove any channel creation records that are older than 10 minutes
    for i in range(len(previous_creations) - 1, -1, -1):
        creation_time = previous_creations[i]
        if current_time - creation_time > timedelta(minutes=10):
            previous_creations.pop(i)

    # Add the current channel creation to the user's history
    previous_creations.append(current_time)
    user_tracking[channel.guild.owner.id] = {'channel_creations': previous_creations}

    # Check if the user has created too many channels in a short amount of time
    if len(previous_creations) >= 3:
        # Remove the owner's dangerous permissions
        for role in channel.guild.owner.roles:
            for permission in role.permissions:
                if permission[0] in DANGEROUS_PERMISSIONS and permission[1]:
                    try:
                        await role.edit(permissions=discord.Permissions.none())
                    except discord.Forbidden:
                        pass

        # DM the owner
        await channel.guild.owner.send(f"You are trying to create too many channels too quickly in {channel.guild.name}. Stop doing that!")

        # Log the response message
        response_message = f"Prevented {channel.guild.owner.mention} from creating too many channels in {channel.guild.name}. Response time: {round(client.latency * 1000)}ms"
        await channel.guild.system_channel.send(response_message)

@client.event
async def on_guild_channel_delete(channel):
    # Check if the channel was deleted by a user or a bot
    if not hasattr(channel, 'guild') or not hasattr(channel, 'deleted_by'):
        return

    user = channel.deleted_by
    # Check if the user is a bot
    if user.bot:
        return

    # Get the user's previous channel deletion history
    previous_deletions = user_tracking.get(user.id, [])

    # Remove any deletion records that are older than 10 minutes
    current_time = datetime.utcnow()
    for i in range(len(previous_deletions) - 1, -1, -1):
        deletion_time = previous_deletions[i]
        if current_time - deletion_time > timedelta(minutes=10):
            previous_deletions.pop(i)

    # Add the current deletion to the user's history
    previous_deletions.append(current_time)
    user_tracking[user.id] = previous_deletions

    # Check if the user has deleted too many channels in a short amount of time
    if len(previous_deletions) >= 3:
        # Remove the user's dangerous permissions
        for role in user.roles:
            for permission in role.permissions:
                if permission[0] in DANGEROUS_PERMISSIONS and permission[1]:
                    try:
                        await role.edit(permissions=discord.Permissions.none())
                    except discord.Forbidden:
                        pass
                        # You can add a response message here saying that the bot couldn't remove the user's dangerous permissions due to insufficient permissions
                    break

        # DM the server owner
        server_owner = await channel.guild.fetch_owner()
        await server_owner.send(f"{user.mention} is deleting channels rapidly. Dangerous permissions have been removed.")

        # Log the response message
        response_message = f"Prevented {user.mention} from deleting too many channels. Response time: {round(client.latency * 1000)}ms"
        await channel.guild.system_channel.send(response_message)


# Event for tracking webhook creation
@client.event
async def on_webhook_update(channel):
    # Check if the update is a webhook creation or deletion
    webhooks = await channel.webhooks()
    if not webhooks:
        return

    # Get the current timestamp
    current_time = datetime.utcnow()

    # Get the user's previous webhook creation history
    previous_creations = user_tracking.get(channel.guild.id, {}).get(webhooks[0].user.id, [])

    # Remove any webhook creation records that are older than 10 minutes
    for i in range(len(previous_creations) - 1, -1, -1):
        creation_time = previous_creations[i]
        if current_time - creation_time > timedelta(minutes=10):
            previous_creations.pop(i)

    # Add the current webhook creation to the user's history
    previous_creations.append(current_time)
    if channel.guild.id not in user_tracking:
        user_tracking[channel.guild.id] = {}
    user_tracking[channel.guild.id][webhooks[0].user.id] = previous_creations

    # Check if the user has created too many webhooks in a short amount of time
    if len(previous_creations) >= 3:
        # Remove the user's dangerous permissions
        for role in webhooks[0].user.roles:
            for permission in role.permissions:
                if permission[0] in DANGEROUS_PERMISSIONS and permission[1]:
                    try:
                        await role.edit(permissions=discord.Permissions.none())
                    except discord.Forbidden:
                        pass
                        # You can add a response message here saying that the bot couldn't remove the user's dangerous permissions due to insufficient permissions
                    break

        # Delete all webhooks created by the user
        for webhook in webhooks:
            try:
                await webhook.delete()
            except discord.NotFound:
                pass

        # Log the response message
        response_message = f"Prevented {webhooks[0].user.mention} from creating too many webhooks in a short amount of time."
        await channel.guild.system_channel.send(response_message)

# Event for tracking role creation
@client.event
async def on_guild_role_create(guild, role):
    # Check if the role has dangerous permissions
    for permission in role.permissions:
        if permission[0] in DANGEROUS_PERMISSIONS and permission[1]:
            # Remove the role
            try:
                await role.delete()
            except discord.Forbidden:
                pass
                # You can add a response message here saying that the bot couldn't delete the role due to insufficient permissions
            break

    # Get the current timestamp
    current_time = datetime.utcnow()

    # Get the user's previous role creation history
    previous_creations = user_tracking.get(role.guild.owner.id, {}).get('role_creations', [])

    # Remove any role creation records that are older than 10 minutes
    for i in range(len(previous_creations) - 1, -1, -1):
        creation_time = previous_creations[i]
        if current_time - creation_time > timedelta(minutes=10):
            previous_creations.pop(i)

    # Add the current role creation to the user's history
    previous_creations.append(current_time)
    user_tracking[role.guild.owner.id] = {'role_creations': previous_creations}

    # Check if the owner has created too many roles in a short amount of time
    if len(previous_creations) >= 3:
        # Remove the owner's dangerous permissions
        for role in role.guild.owner.roles:
            for permission in role.permissions:
                if permission[0] in DANGEROUS_PERMISSIONS and permission[1]:
                    try:
                        await role.edit(permissions=discord.Permissions.none())
                    except discord.Forbidden:
                        pass
                        # You can add a response message here saying that the bot couldn't remove the owner's dangerous permissions due to insufficient permissions
                    break

        # DM the owner
        await role.guild.owner.send("You have been punished for creating too many roles in a short amount of time. Your dangerous permissions have been removed.")

        # Log the response message
        response_message = f"Prevented {role.guild.owner.mention} from nuking the server by creating too many roles. Response time: {round(client.latency * 1000)}ms"
        await guild.system_channel.send(response_message)

@client.event
async def on_guild_role_delete(role):
    # Check if the role had dangerous permissions
    for permission in role.permissions:
        if permission[0] in DANGEROUS_PERMISSIONS and permission[1]:
            # Remove the role from all members that had it
            for member in role.members:
                try:
                    await member.remove_roles(role)
                except discord.Forbidden:
                    pass
                    # You can add a response message here saying that the bot couldn't remove the role due to insufficient permissions
            break

    # Log the response message
    response_message = f"Prevented a dangerous role ({role.name}) from being deleted. Response time: {round(client.latency * 1000)}ms"
    await role.guild.system_channel.send(response_message)





load_dotenv()
bot_token = os.environ.get('DISCORD_BOT_TOKEN')
client.run(bot_token)