# Bot settings
bot_settings =  {
    "bot_token": ["Bot API Token", "Token used to connect to the Discord API.", 1, str, "", True],
    "twitter_api_keys": ["Twitter API Keys", "Keys used to connect to the Twitter API.", 1, str, ["", "", "", "", ""], True, ["Key A", "Key B", "Key C", "Key D", "Key E"]],
    "guild_id": ["Server ID", "ID of the Discord server we're in.", 1, int, 0, False],
    "reduced_cooldown_channels": ["Cooldown Exempt Channels", "IDs of channels with reduced command cooldowns.", 1, int, [], False],
    "reduced_cooldown_roles": ["Cooldown Exempt Roles", "IDs of roles with reduced command cooldowns.", 1, int, [], False],
    "deprecated_commands": ["Allow Deprecated Commands", "Whether or not to enable deprecated (unsupported) commands.", 1, bool, False, False],
    "log_channel": ["Logging Channel", "ID of the channel to post bot logs in.", 1, int, 0, False],
    "authorized_posters": ["Authorized Twitter Posters", "IDs of users with permission to make a post on the connected Twitter account.", 1, int, [], False],
    "spoiler_channels": ["Spoiler Channels", "IDs of channels to post spoilers in.", 1, int, [0, 0, 0, 0, 0], False, ["Announcements Channel", "Channel A", "Channel B", "Channel C", "Channel D"]],
    "spoiler_ping_role": ["Spoiler Announcement Role", "ID of the role to ping for important spoiler announcements.", 1, int, 0, False],
    "spoiler_introduction": ["Spoiler Introduction Message", "Message to display when the bot has detected a new file update with files of interest.", 1, str, "Hello! I am Atmobot.\n\nAny automatically posted tweets will begin with [BOT].", False],
    "spoiler_closure": ["Spoiler Closure Message", "Message to display after the bot has finished posting about new file updates.", 1, str, "Thats all for now!\n\nSee you next time!", False] 
}

BOT_SETTINGS_NAME = 0
BOT_SETTINGS_DESCRIPTION = 1
BOT_SETTINGS_VERSION = 2
BOT_SETTINGS_TYPE = 3
BOT_SETTINGS_DEFAULT = 4
BOT_SETTINGS_CENSOR = 5
BOT_SETTINGS_INDEX_DESCRIPTORS = 6

# Name of the settings file
settings_path = "settings.json"

# Described our bot
bot_description = '''Atmobot adds a range of fun and informative commands to the Atmoplex Discord Server. It can also automatically spoil updates for Wizard101 and Pirate101!'''

# Debug message for when the bot starts up
startup_message = "{header}\nLogged in as {username} with user ID {id}\nStarted up at {timestamp}\n{footer}"

# Paths to our resource folders
resources_path = "resources"
deepfakes_path = "deepfakes"
memes_path = "memes"
memes_archived_path = "archive"
memes_hidden_path = "hidden"
hero101_path = "hero"
video_path = "video"
locale_path = "locale"

# Font paths
font_atmoplex = "font_atmoplex.ttf"
font_mgi = "font_mgi.ttf"

# Command logging
fallback_log_message = "WARNING: Log information not provided!"
formatted_log_message_local = "{current_time} | {caller_name_formatted} | {full_username} ({user_id}) | {channel_name} ({channel_id})\n{message}"
formatted_log_message_discord = "**{current_time} | {caller_name_formatted} | {user_mention} | {channel_mention}**\n*{message}*"

# Command error messages
command_error_cooldown_header_title = "This command is on cooldown."
command_error_cooldown_header_desc = "Try again in **{time_to_retry} seconds.**"
command_error_cooldown_footer_title = "Want shorter cooldowns?"
command_error_cooldown_footer_desc = "Become a Server Booster or use Atmobot in {cooldown_free_channel} for shorter cooldowns!"
command_error_exception_title = "Uh oh! Atmobot has run into an error."
command_error_exception_desc = "Please try again. If the problem persists, please contact an administrator."

# Hero101 command
command_hero101_name = "hero101"
command_hero101_description = "Posts something random related to Hero101."

# Remco command
command_remco_name = "remco"
command_remco_description = "Posts ascii art depicting the CEO of MGI, Remco Westermann."
command_remco_art = "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠉⠉⠙⠻⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠟⢁⣠⣤⣶⣶⣷⣶⣶⣦⣄⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⡟⠃⠀⢠⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⡏⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠈⢻⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⠃⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣆⡌⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡏⠀⠀⣸⣿⣿⣿⡿⠿⠿⣿⣿⣿⣿⣿⣿⠿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡇⠀⢀⡙⠛⠑⡸⠛⠛⠂⠀⠘⢻⣟⠊⠀⠘⢛⡛⣧⠙⠃⣽⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡇⠈⠿⣿⣿⣯⣺⣿⣿⣿⡟⣰⣿⣿⣏⢻⣿⣿⣿⣟⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣧⣾⣿⣿⣿⣿⣶⣭⣴⣿⣿⣿⣿⣿⣷⣶⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣅⣀⣈⣿⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⡟⢿⣿⣿⣿⣿⣤⣀⣀⣀⣉⣉⣉⣉⣉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣷⡀⢿⡝⢿⣿⣿⣿⣷⣭⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⠘⢻⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⣦⡀⢀⠀⠴⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠏⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿"

# Quote command
command_quote_name = "quote"
command_quote_description = "Posts a random quote from the specified user."
command_quote_arg_user_name = "user"
command_quote_arg_user_description = "The user to retrieve a quote from."

COMMAND_QUOTE_USER_NAME = 0
COMMAND_QUOTE_USER_ID = 1
COMMAND_QUOTE_DATE_RANGE = 2

command_quote_message_history = 10000
command_quote_message_threshold = 10

# Days command
command_days_name = "days"
command_days_description = "Displays the amount of days left until Test Realm Watch begins."
command_days_formatted = "There {verb} **{days} day{s}** until Test Realm Watch ({date}).\nTest Realm Watch is the first day of the season in which Test Realm has a chance to release."
command_days_watch = "**Test Realm Watch has begun!**\nTest Realm is likely to release any time **Monday through Thursday**, from **9:00 AM PST until 5:00 PM PST**."

# Test Realm command
command_testrealm_name = "testrealm"
command_testrealm_description = "Details when Test Realm is likely to arrive, and why."
command_testrealm_embed_title = "When is Test Realm coming?"
command_testrealm_embed_intro_title = "We don't know"
command_testrealm_embed_intro_description = "But we can certainly make an educated guess. By taking a look at prior Test Realm release dates, we can estimate when this one may release. Let's look at Summer Update releases from the last 5 years."
command_testrealm_embed_historicals_title = "Prior release dates"
command_testrealm_embed_historicals_description = "2017: Wednesday, 6/21 @ 8:13 AM\n2018: Wednesday, 6/27 @ 8:04 AM\n2019: Wednesday, 7/10 @ 4:00 PM\n2020: Wednesday, 7/1 @ 7:00 AM\n2021: Tuesday, 7/6 @ 8:00 AM"
command_testrealm_embed_summary_title = "Summary"
command_testrealm_embed_summary_description = "Earliest Date: June 21st\nLatest Date: August 3rd\nEarliest Time: 7:00 AM PST\nLatest Time: 4:00 PM PST\n\nMost popular day: Wednesday\nLeast popular day: Monday/Thursday\nPossible days: Monday through Thursday\n\nLast year's date: Tuesday, July 6th"
command_testrealm_embed_estimation_title = "Estimation"
command_testrealm_embed_estimation_description = "We think Test Realm will release on Tuesday, July 5th. On this day, we will go into Test Realm Watch and check for any activity with Kingsisle's Test Realm related servers. If anything is detected, everyone who has the \"Test Realm Notifications\" role will be notified!"

# Thumbnail command
command_thumbnail_name = "thumbnail"
command_thumbnail_description = "Creates a thumbnail in the same style as a Wizard101 Music upload from The Atmoplex."
command_thumbnail_arg_header_name = "header"
command_thumbnail_arg_header_description = "The thumbnail header. Typically the name of a song."
command_thumbnail_arg_footer_name = "footer"
command_thumbnail_arg_footer_description = "The thumbnail footer. Typically the name of a world."
command_thumbnail_arg_image_name = "image"
command_thumbnail_arg_image_description = "Which image is used to create the thumbnail."
command_thumbnail_file_name = "command_{}"
command_thumbnail_extras = {"Wizard101": ("wiz", 1, font_atmoplex, 130, 272, (239, 238, 41), 416, (255, 255, 255), 0),
                            "Wizard101 (New)": ("wiz_new", 1, font_atmoplex, 130, 272, (239, 238, 41), 416, (255, 255, 255), 0),
                            "Pirate101": ("pirate", 1, font_atmoplex, 130, 272, (239, 238, 41), 416, (255, 255, 255), 0),
                            "Hero101": ("hero", 1, font_atmoplex, 130, 272, (239, 238, 41), 416, (255, 255, 255), 0),
                            "Media Games Invest": ("mgi", 0, font_mgi, 70, -70, (255, 255, 255), 15, (255, 255, 255), 40)}

COMMAND_THUMBNAIL_NAME = 0
COMMAND_THUMBNAIL_UPPERCASE = 1
COMMAND_THUMBNAIL_FONT = 2
COMMAND_THUMBNAIL_FONT_SIZE = 3
COMMAND_THUMBNAIL_HEADER_OFFSET = 4
COMMAND_THUMBNAIL_HEADER_COLOR = 5
COMMAND_THUMBNAIL_FOOTER_OFFSET = 6
COMMAND_THUMBNAIL_FOOTER_COLOR = 7
COMMAND_THUMBNAIL_X_OFFSET = 8

# Stats command
command_stats_name = "stats"
command_stats_description = "Displays interesting statistics about Atmobot."
command_stats_release_version_unknown = "Unknown"
command_stats_newline = "\n"
command_stats_release_note = "- {note}" + command_stats_newline
command_stats_version = "**Version:** {version}"
command_stats_notes = "**Release Notes:**\n{notes}"
command_stats_uptime = "**Uptime:** {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds."

COMMAND_STATS_RELEASE_VERSION = 0
COMMAND_STATS_RELEASE_NOTES = 1

# Meme command
command_meme_name = "meme"
command_meme_description = "Posts a random meme relevant to The Atmoplex Discord Server."

COMMAND_MEME_HIDDEN_NAME = 0
COMMAND_MEME_HIDDEN_RARITY = 1

# Deepfake command
command_deepfake_name = "deepfake"
command_deepfake_description = "Posts a deepfake of a person or character related to Kingsisle."
command_deepfake_arg_directory_name = "directory"
command_deepfake_arg_directory_description = "Choose a specific category to retrieve a deepfake from."

# URLs for the checker to test
test_patch_client_url = "https://www.wizard101.com/testpatchClient"
update_notes_url = "https://www.wizard101.com/game/community/update-notes/{month}{year}"

URL_CACHE_REQUEST = 0
URL_CACHE_HASH = 1

# Base patcher url
patcher_url = "http://{server}.us.{game_longhand}.com/{game_shorthand}Patcher/V_r{revision_number}.{revision_version}/LatestBuild/Data/GameData/{wad_name}.wad"

# Service information
SERVICE_UNKNOWN = -1
LIVE_REALM = 0
TEST_REALM = 1

service_names = {SERVICE_UNKNOWN: "",
                 LIVE_REALM: "",
                 TEST_REALM: "test"}

service_suffix = "Realm"

# Server information
SERVER_UNKNOWN = -1
PATCH = 0
VERSION = 1
VERSIONEC = 2

server_options = {SERVER_UNKNOWN: "",
                  PATCH: "patch",
                  VERSION: "version",
                  VERSIONEC: "versionec"}

# Game information
GAME_UNKNOWN = -1
WIZARD101 = 0
PIRATE101 = 1

# Longhang names for the games
game_longhands = {GAME_UNKNOWN: "",
                  WIZARD101: "Wizard101",
                  PIRATE101: "Pirate101"}
longhand_to_game = {"Wizard101": WIZARD101,
                    "Pirate101": PIRATE101}

# Shorthand names for the games used for patcher links
game_shorthands_patcher = {GAME_UNKNOWN: "",
                   WIZARD101: "Wiz",
                   PIRATE101: "Pirate"}

# Shorthand names for the games used for version labeling
game_shorthands_version = {GAME_UNKNOWN: "",
                           WIZARD101: "Wizard",
                           PIRATE101: "Pirate"}

# Revision handling
REVISION_UNKNOWN = -1
REVISION_NUMBER = 0
REVISION_VERSION = 1

fallback_game = WIZARD101
fallback_revision = 716142
fallback_version_live = "1_470"
fallback_version_live_formatted = "{game}_{version}"
fallback_version_dev = "{game}Dev"

version_empty = "{game}_{revision}_{version}"

default_revision_range = 500

# Fallback .WAD file used for testing
fallback_wad = "Root"

# Correlation between patcher error code and likeliness of being online
patcher_online = "is online"
patcher_offline = "is offline"
patcher_undecided = "may be online"
patcher_tips = {200: patcher_online,
                403: patcher_undecided,
                404: patcher_undecided,
                504: patcher_offline}

CHECKER_ROUTINE_GAME = 0

CHECKER_ROUTINE_GAME_WIZARD = 0
CHECKER_ROUTINE_GAME_PIRATE = 1
CHECKER_ROUTINE_GAME_BOTH = 2

CHECKER_ROUTINE_METHOD = 1

CHECKER_ROUTINE_METHOD_PATCHER = 0
CHECKER_ROUTINE_METHOD_WEBSITE = 1
CHECKER_ROUTINE_METHOD_BOTH = 2

CHECKER_ROUTINE_DURATION = 1
CHECKER_ROUTINE_FREQUENCY = 2
CHECKER_ROUTINE_ANNOUNCEMENT_LEVEL = 3

CHECKER_ROUTINE_ANNOUNCEMENT_LEVEL_NONE = 0
CHECKER_ROUTINE_ANNOUNCEMENT_LEVEL_MODS = 1
CHECKER_ROUTINE_ANNOUNCEMENT_LEVEL_ROLE = 2
CHECKER_ROUTINE_ANNOUNCEMENT_LEVEL_EVERYONE = 3
CHECKER_ROUTINE_ANNOUNCEMENT_LEVEL_TWEET = 4

CHECKER_ROUTINE_ANNOUNCEMENT_MESSAGE = 4
CHECKER_ROUTINE_REPEAT_AFTER_SUCCESS = 5

# Posted when a new test revision has been detected, and the bot is about to commence with auto-spoilers
spoilers_incoming_twitter = "Hello! I am Atmobot.\nThe Test Realm files have just updated, so I'm here to spoil a few things automatically! Plex is datamining manually at the moment, so enjoy these automatic spoilers while you wait.\nAny automatically posted tweets will begin with [BOT]."
spoilers_incoming_discord_title = "Atmobot"
spoilers_incoming_discord_information_title = "Hello! I am Atmobot"
spoilers_incoming_discord_information = "I am a bot created by the Atmoplex team for the purpose of spoiling Test Realm. Test Realm has just updated, so it's time for me to spoil a few things automatically!"
spoilers_incoming_discord_coming_soon_title = "So what now?"
spoilers_incoming_discord_coming_soon = "Within the next minute, I will begin posting in the spoilers category of this server. There will be about one file posted every 10 seconds, give or take.\n\nIn the meantime, the Atmoplex team is datamining the update manually. Whatever is missed by Atmobot will be later posted to Twitter. Enjoy these automatic spoilers!"
spoilers_incoming_discord_channels_title = "New Channels"
spoilers_incoming_discord_channels = "{images_channel} - Icons of new spells, equipment, furniture, spells, NPCs, and more.\n\n{music_channel} - All of the new soundtracks, excluding ambient music and cues.\n\n{locale_channel} - A collection of new zone names, mob names, and more."

# Helps retrieve Twitter API keys from the settings
TWITTER_KEY_CONSUMER = 0
TWITTER_KEY_CONSUMER_SECRET = 1
TWITTER_KEY_ACCESS_TOKEN = 2
TWITTER_KEY_ACCESS_TOKEN_SECRET = 3
TWITTER_KEY_BEAR = 4

CHANNEL_INVALID = -1
CHANNEL_LOG = 0
CHANNEL_ANNOUNCEMENT = 1
CHANNEL_IMAGES = 2
CHANNEL_MUSIC = 3
CHANNEL_LOCALE = 4

spoilers_template = {
    "Root": [{"name": "Spell Preview Icons",
              "file_path": "GUI/DeckConfig/",
              "file_exclusions": ["Spell_Complete_BW"],
              "file_inclusions": [],
              "channel_to_post": 1,
              "post_description": "Take a look at the new Spell Preview Icons!",
              "post_to_twitter": True,
              "divide_threshold": 5}]
}

spoilers_path = "spoilers.json"

SPOILER_NAME = 0
SPOILER_FILE_PATH = 1
SPOILER_FILE_EXCLUSIONS = 2
SPOILER_FILE_INCLUSIONS = 3
SPOILER_CHANNEL_TO_POST = 4
SPOILER_POST_DESCRIPTION = 5
SPOILER_POST_TO_TWITTER = 6
SPOILER_DIVIDE_THRESHOLD = 7

time_between_posts = 5
spoiler_divide_amount = 16
spoilers_per_tweet = 4

twitter_description_format = "[BOT] {description}"
twitter_description_extension = " [{current}/{total}]"

thumbnail_template_name = "thumbnail_template_{thumb_type}.png"
thumbnail_output_path = "video_thumbnail_{file_name}.png"
thumbnail_dimensions = (1920, 1080)

video_output_path = "music_video.mp4"

prefix_to_world = {
    "WC": "Wizard City",
    "KT": "Krokotopia",
    "MB": "Marleybone",
    "MS": "Mooshu",
    "DS": "Dragonspyre",
    "GH": "Grizzleheim",
    "WT": "Wintertusk",
    "WY": "Wysteria",
    "ZF": "Zafaria",
    "AV": "Avalon",
    "AZ": "Azteca",
    "AQ": "Aquila",
    "KR": "Khrysalis",
    "SB": "Shangri-Ba",
    "DM": "Darkmoor",
    "PL": "Polaris",
    "AR": "Arcanum",
    "MR": "Mirage",
    "EM": "Empyrea",
    "KM": "Karamelle",
    "LM": "Lemuria",
    "YG": "Yago"
}

twitter_video_limit = 140
twitter_video_process_time = 15

video_dimension = 720
video_fade_duration = 5

video_overtime_description = "\n\n(Track shortened to adhere to Twitter's video limit. Full version uploaded later.)"

CHAIN_STATUS_INVALID = -1
CHAIN_STATUS_NOT_READY = 0
CHAIN_STATUS_WAITING = 1
CHAIN_STATUS_COMPLETE = 2

LINK_DATA_STATUS = 0
LINK_DATA_CONFIG = 1
LINK_DATA_LAST_TWEET_ID = 2

LINK_CONFIG_PATH = 0
LINK_CONFIG_NAME = 1
LINK_CONFIG_DESCRIPTION = 2

next_video_signal = "video_next_up"

locale_template_path = "locale_template.png"
locale_path_old = "old"

locale_divide_amount = 12

locale_header_offset_x = 532
locale_header_offset_y = 454

locale_line_offset_x = 250
locale_line_offset_x_secondary = 1075
locale_line_offset_y = 175
locale_line_offset_y_lower = 125
