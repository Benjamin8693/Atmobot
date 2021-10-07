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
    "spoiler_channel_ids": [0, 0, 0],
    "spoiler_announcement": "Hello! I am Atmobot.\n\nAny automatically posted tweets will begin with [BOT].",
    "spoiler_goodbye": "Thats all for now!\n\nSee you next time!"
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
HERO101 = 2

game_longhands = {GAME_UNKNOWN: "",
                  WIZARD101: "Wizard101",
                  PIRATE101: "Pirate101",
                  HERO101: "Hero101"}
longhand_to_game = {"Wizard101": WIZARD101,
                    "Pirate101": PIRATE101,
                    "Hero101": HERO101}

game_shorthands = {GAME_UNKNOWN: "",
                   WIZARD101: "Wiz",
                   PIRATE101: "Pirate",
                   HERO101: "Hero"}

# Revision handling
REVISION_UNKNOWN = -1
REVISION_NUMBER = 0
REVISION_VERSION = 1

fallback_revision = 702000
fallback_version = "Wizard_1_460"
fallback_version_dev = "WizardDev"

version_empty = "Wizard_{}_{}"

default_revision_range = 25

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
video_path = "video"
locale_path = "locale"

# Commands
default_command_cooldown = 15
extended_command_cooldown = 1

command_remco_name = "remco"
command_remco_description = "Posts Remco."
command_remco_art = "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠉⠉⠙⠻⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠟⢁⣠⣤⣶⣶⣷⣶⣶⣦⣄⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⡟⠃⠀⢠⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⡏⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠈⢻⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⠃⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣆⡌⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡏⠀⠀⣸⣿⣿⣿⡿⠿⠿⣿⣿⣿⣿⣿⣿⠿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡇⠀⢀⡙⠛⠑⡸⠛⠛⠂⠀⠘⢻⣟⠊⠀⠘⢛⡛⣧⠙⠃⣽⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⡇⠈⠿⣿⣿⣯⣺⣿⣿⣿⡟⣰⣿⣿⣏⢻⣿⣿⣿⣟⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣧⣾⣿⣿⣿⣿⣶⣭⣴⣿⣿⣿⣿⣿⣷⣶⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣅⣀⣈⣿⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⡟⢿⣿⣿⣿⣿⣤⣀⣀⣀⣉⣉⣉⣉⣉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣷⡀⢿⡝⢿⣿⣿⣿⣷⣭⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⠘⢻⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⣿⣿⣿⣿⣿⣿⣿⣿⡇⣦⡀⢀⠀⠴⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠏⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿"

command_quote_name = "quote"
command_quote_description = "Posts a random quote."
command_quote_arg_author_name = "author"
command_quote_arg_author_description = "Choose an author to retrieve a quote from."
command_quote_authors = {"chris": (310684137403056128, (2021, 5, 12)),
                         "alphastaire": (169587016684666880, None),
                         "benjamin": (104405233987235840, None)}

COMMAND_QUOTE_AUTHOR_ID = 0
COMMAND_QUOTE_DATE_RANGE = 1

command_quote_channel_id = 389266925185662986
command_quote_message_limit = 10000

command_days_name = "days"
command_days_description = "Displays the amount of days left until Test Realm Watch begins."
command_days_formatted = "There are {days} days until Test Realm Watch (October 25th)."

command_testrealm_name = "testrealm"
command_testrealm_description = "Details when Test Realm is likely to arrive, and why."
command_testrealm_embed_title = "When is Test Realm coming?"
command_testrealm_embed_intro_title = "We don't know"
command_testrealm_embed_intro_description = "But we can certainly make an educated guess. By taking a look at prior Test Realm release dates, we can estimate when this one may release. We typically reference every Test Realm since 2015, when the 3-updates-a-year cycle began."
command_testrealm_embed_historicals_title = "Prior release dates"
command_testrealm_embed_historicals_description = "2015 - Polaris: Monday, 10/26 @ 9:15 AM\n2016 - Mirage: Wednesday, 11/9 @ 5:00 PM\n2017 - Empyrea Part 1: Wednesday, 10/18 @ 4:37 PM\n2018 - Empyrea Part 2: Thursday, 10/18 @ 9:50 AM\n2019 - Catacombs: Wednesday, 10/23 @ 1:22 PM\n2020 - Karamelle: Wednesday, 10/28 @ 10:59 AM"
command_testrealm_embed_summary_title = "Summary"
command_testrealm_embed_summary_description = "Earliest Date: October 18th\nLatest Date: November 9th\nEarliest Time: 9:15 AM PST\nLatest Time: 5:00 PM PST\n\nMost popular day: Wednesday\nLeast popular day: Tuesday\nPossible days: Monday through Thursday\n\nEarliest FULL world update: October 26th\nLast year's date: October 28th"
command_testrealm_embed_estimation_title = "Estimation"
command_testrealm_embed_estimation_description = "We will go into Test Realm watch on Monday, October 18th. This day, and every weekday thereafter (excluding Friday), is likely for Test Realm to release.\n\nAtmobot (me) will also be checking for any Test Realm activity on a regular basis. As soon as there any activity, everyone who has the \"Test Realm Notifications\" role will be notified!"

command_thumbnail_name = "thumbnail"
command_thumbnail_description = "Creates a thumbnail in the same style as a Wizard101 Music upload from The Atmoplex."
command_thumbnail_arg_header_name = "header"
command_thumbnail_arg_header_description = "The thumbnail header. Typically the name of a song."
command_thumbnail_arg_footer_name = "footer"
command_thumbnail_arg_footer_description = "The thumbnail footer. Typically the name of a world."
command_thumbnail_arg_game_name = "game"
command_thumbnail_arg_game_description = "Which game the thumbnail is for."

command_uptime_name = "uptime"
command_uptime_description = "Displays how long Atmobot has been online for."

command_meme_name = "meme"
command_meme_description = "Posts a random meme relevant to The Atmoplex Discord Server."

command_deepfake_name = "deepfake"
command_deepfake_description = "Posts a deepfake of a person or character related to Kingsisle."
command_deepfake_arg_directory_name = "directory"
command_deepfake_arg_directory_description = "Choose a specific category to retrieve a deepfake from."

# Posted when a new test revision has been detected, and the bot is about to commence with auto-spoilers
spoilers_incoming_twitter = "Hello! I am Atmobot.\nThe Lemuria Test Realm files have just updated, so I'm here to spoil a few things automatically! Plex is datamining manually at the moment, so enjoy these automatic spoilers while you wait.\nAny automatically posted tweets will begin with [BOT]."
spoilers_incoming_discord_title = "Atmobot"
spoilers_incoming_discord_information_title = "Hello! I am Atmobot"
spoilers_incoming_discord_information = "I am a bot created by the Atmoplex team for the purpose of spoiling Test Realm when it releases. The Test Realm patcher just updated, so it's time for me to spoil a few things automatically!\n\nThis does **NOT** mean for certain that Test Realm is releasing today- but it's very likely!"
spoilers_incoming_discord_coming_soon_title = "So what now?"
spoilers_incoming_discord_coming_soon = "Within the next minute, I will begin posting in three new channels that have opened up. There will be about one file posted every 10 seconds, give or take.\n\nIn the meantime, the Atmoplex team is datamining the update manually. Whatever is missed by Atmobot will be later posted to Twitter. Enjoy these automatic spoilers, and get excited for Test Realm!"
spoilers_incoming_discord_channels_title = "New Channels"
spoilers_incoming_discord_channels = "{images_channel} - Icons of new spells, equipment, furniture, spells, NPCs, and more.\n\n{music_channel} - All of the new soundtracks, excluding ambient music and cues.\n\n{locale_channel} - A collection of new zone names, mob names, and more."

# Helps retrieve Twitter API keys from the settings
TWITTER_KEY_CONSUMER = 0
TWITTER_KEY_CONSUMER_SECRET = 1
TWITTER_KEY_ACCESS_TOKEN = 2
TWITTER_KEY_ACCESS_TOKEN_SECRET = 3
TWITTER_KEY_BEAR = 4

CHANNEL_INVALID = -1
CHANNEL_LOCALE = 0
CHANNEL_IMAGES = 1
CHANNEL_MUSIC = 2

spoilers_template = {
    "Root": [{"name": "Spell Preview Icons",
              "file_path": "GUI/DeckConfig/",
              "file_exclusions": ["Spell_Complete_BW"],
              "channel_to_post": 1,
              "post_description": "Take a look at the new Spell Preview Icons!",
              "post_to_twitter": True}]
}

spoilers_path = "spoilers.json"

SPOILER_NAME = 0
SPOILER_FILE_PATH = 1
SPOILER_FILE_EXCLUSIONS = 2
SPOILER_CHANNEL_TO_POST = 3
SPOILER_POST_DESCRIPTION = 4
SPOILER_POST_TO_TWITTER = 5

time_between_posts = 5
spoiler_divide_threshold = 5
spoiler_divide_amount = 16

twitter_description_format = "[BOT] {description}"
twitter_description_extension = " [{current}/{total}]"

thumbnail_template_path = {GAME_UNKNOWN: "thumbnail_template_wizard.png",
                           WIZARD101: "thumbnail_template_wizard.png",
                           PIRATE101: "thumbnail_template_pirate.png",
                           HERO101: "thumbnail_template_hero.png"}
thumbnail_font_path = "thumbnail_font.ttf"
thumbnail_output_path = "video_thumbnail_{file_name}.png"

thumbnail_command_name = "command_{}"

thumbnail_font_size = 130
thumbnail_header_offset = 272
thumbnail_header_color = (239, 238, 41)
thumbnail_footer_offset = 416
thumbnail_footer_color = (255, 255, 255)

thumbnail_offsets = (thumbnail_header_offset, thumbnail_footer_offset)
thumbnail_colors = (thumbnail_header_color, thumbnail_footer_color)

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

video_overtime_description = " (Track shortened to adhere to Twitter's video limit. Full version uploaded later.)"

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
