
# Default settings
default_settings = {
    "game_id": 0,
    "bot_token": "",
    "subscribed_guild_ids": [0],
    "cooldown_exempt_channel_ids": [0],
    "cooldown_exempt_role_ids": [0],
    "deprecated_commands": False,
    "last_startup": "",
    "revision_info_live": [],
    "revision_info_test": [],
    "fetch_revision_on_startup": False,
    "twitter_api_keys": ["", "", "", "", ""],
    "authorized_poster_ids": [],
    "spoiler_channel_ids": [0, 0, 0, 0, 0],
    "spoiler_announcement_role_id": 0,
    "spoiler_greetings": "Hello! I am Atmobot.\n\nAny automatically posted tweets will begin with [BOT].",
    "spoiler_goodbye": "Thats all for now!\n\nSee you next time!",
    "release_info": ["1.0.0", ["Added a new feature", "Made a tweak", "Fixed a bug"]],
    "hidden_memes": [],
    "quote_channel_id": 0,
    "quote_users": []
}

# Name of the settings file
settings_path = "settings.json"

# Described our bot
bot_description = '''Atmobot adds unique functionality to The Atmoplex Discord Server!'''

# Debug message for when the bot starts up
startup_message = "{header}\nLogged in as {username} with user ID {id}\nStarted up at {timestamp}\nRunning in {game_longhand} mode\n{footer}"

# Important urls to check
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

game_longhands = {GAME_UNKNOWN: "",
                  WIZARD101: "Wizard101",
                  PIRATE101: "Pirate101"}
longhand_to_game = {"Wizard101": WIZARD101,
                    "Pirate101": PIRATE101}

game_shorthands = {GAME_UNKNOWN: "",
                   WIZARD101: "Wiz",
                   PIRATE101: "Pirate"}

# Revision handling
REVISION_UNKNOWN = -1
REVISION_NUMBER = 0
REVISION_VERSION = 1

fallback_revision = 716142
fallback_version = "Wizard_1_470"
fallback_version_dev = "WizardDev"

version_empty = "Wizard_{}_{}"

default_revision_range = 500

# Fallback .WAD file used for testing
fallback_wad = "Root"

# Strings that relate the patcher's error code to likeliness of being online
patcher_tips = {200: "The Patcher is online",
                403: "The Patcher may be online",
                404: "The Patcher may be online"}

# Paths to our resource folders
resources_path = "resources"
deepfakes_path = "deepfakes"
memes_path = "memes"
memes_archived_path = "archive"
memes_hidden_path = "hidden"
hero101_path = "hero"
video_path = "video"
locale_path = "locale"

# Fonts
font_atmoplex = "font_atmoplex.ttf"
font_mgi = "font_mgi.ttf"
font_sans = "font_sans.ttf"

# Commands
default_command_cooldown = 5
extended_command_cooldown = 1

command_hero101_name = "hero101"
command_hero101_description = "Posts something random related to Hero101."

command_remco_name = "remco"
command_remco_description = "Posts Remco."
command_remco_art = "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠉⠉⠙⠻⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠟⢁⣠⣤⣶⣶⣷⣶⣶⣦⣄⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⡟⠃⠀⢠⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⡏⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠈⢻⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⠃⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣆⡌⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡏⠀⠀⣸⣿⣿⣿⡿⠿⠿⣿⣿⣿⣿⣿⣿⠿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡇⠀⢀⡙⠛⠑⡸⠛⠛⠂⠀⠘⢻⣟⠊⠀⠘⢛⡛⣧⠙⠃⣽⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡇⠈⠿⣿⣿⣯⣺⣿⣿⣿⡟⣰⣿⣿⣏⢻⣿⣿⣿⣟⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣧⣾⣿⣿⣿⣿⣶⣭⣴⣿⣿⣿⣿⣿⣷⣶⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣅⣀⣈⣿⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⡟⢿⣿⣿⣿⣿⣤⣀⣀⣀⣉⣉⣉⣉⣉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣷⡀⢿⡝⢿⣿⣿⣿⣷⣭⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⠘⢻⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⣦⡀⢀⠀⠴⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠏⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿"

command_quote_name = "quote"
command_quote_description = "Posts a random quote."
command_quote_arg_user_name = "user"
command_quote_arg_user_description = "Choose a user to retrieve a quote from."

COMMAND_QUOTE_USER_NAME = 0
COMMAND_QUOTE_USER_ID = 1
COMMAND_QUOTE_DATE_RANGE = 2

command_quote_message_history = 10000
command_quote_message_threshold = 10

command_days_name = "days"
command_days_description = "Displays the amount of days left until Test Realm Watch begins."
command_days_formatted = "There {verb} **{days} day{s}** until Test Realm Watch ({date}).\nTest Realm Watch is the first day of the season in which Test Realm has a chance to release."
command_days_watch = "**Test Realm Watch has begun!**\nTest Realm is likely to release any time **Monday through Thursday**, from **9:00 AM PST until 5:00 PM PST**."

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

command_thumbnail_name = "thumbnail"
command_thumbnail_description = "Creates a thumbnail in the same style as a Wizard101 Music upload from The Atmoplex."
command_thumbnail_arg_header_name = "header"
command_thumbnail_arg_header_description = "The thumbnail header. Typically the name of a song."
command_thumbnail_arg_footer_name = "footer"
command_thumbnail_arg_footer_description = "The thumbnail footer. Typically the name of a world."
command_thumbnail_arg_type_name = "type"
command_thumbnail_arg_type_description = "Which type of thumbnail is created."
command_thumbnail_file_name = "command_{}"
command_thumbnail_extras = {"Wizard101": ("wiz", 1, font_atmoplex, 130, 272, (239, 238, 41), 416, (255, 255, 255), 0),
                            "Pirate101": ("pirate", 1, font_atmoplex, 130, 272, (239, 238, 41), 416, (255, 255, 255), 0),
                            "Hero101": ("hero", 1, font_atmoplex, 130, 272, (239, 238, 41), 416, (255, 255, 255), 0),
                            "Media Games Invest": ("mgi", 0, font_mgi, 70, -70, (255, 255, 255), 15, (255, 255, 255), 40),
                            "Server Dude": ("server", 0, font_sans, 30, 272, (0, 0, 0), 416, (0, 0, 0), 40)}

COMMAND_THUMBNAIL_NAME = 0
COMMAND_THUMBNAIL_UPPERCASE = 1
COMMAND_THUMBNAIL_FONT = 2
COMMAND_THUMBNAIL_FONT_SIZE = 3
COMMAND_THUMBNAIL_HEADER_OFFSET = 4
COMMAND_THUMBNAIL_HEADER_COLOR = 5
COMMAND_THUMBNAIL_FOOTER_OFFSET = 6
COMMAND_THUMBNAIL_FOOTER_COLOR = 7
COMMAND_THUMBNAIL_X_OFFSET = 8

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

command_meme_name = "meme"
command_meme_description = "Posts a random meme relevant to The Atmoplex Discord Server."

COMMAND_MEME_HIDDEN_NAME = 0
COMMAND_MEME_HIDDEN_RARITY = 1

command_deepfake_name = "deepfake"
command_deepfake_description = "Posts a deepfake of a person or character related to Kingsisle."
command_deepfake_arg_directory_name = "directory"
command_deepfake_arg_directory_description = "Choose a specific category to retrieve a deepfake from."

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
