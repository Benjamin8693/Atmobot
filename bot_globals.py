# Default settings
default_settings = {
    "game_id": 0,
    "bot_token": "ODYxNDQ4NjI2NTU4MjA1OTUy.YOJ8jQ.kql-_eSMOcC7QnUYvRXtg4NFvl0",
    "subscribed_guilds": [231218732440092675],
    "last_startup": "",
    "revision_info_live": [],
    "revision_info_test": [],
    "fetch_revision_on_startup": False,
    "twitter_api_keys": ["KMHnLXsOx4Ov8Y4GxF0mBTFph", "kksTCeqwGAtipvbyqYXH1dEQLzhMAO1ivmu3z7bAT0W5S2W1MN", "1431849304600178689-rqAp9UinhhKWGO7nB6xaKDQyfOuJXS", "lRAT0SHWiRBtamdsqzyhGQGOvsbSqlfCYSTHZ4X618e6s", "AAAAAAAAAAAAAAAAAAAAAH27TAEAAAAAocKtOIzTQrUkW3JvJjXVOnnBujM%3DbOkZvWFKu1SpsxC09lbVE8gFlr3EjQCQaZTlTdL1c9BIzFRfVo"]
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

game_shorthands = {GAME_UNKNOWN: "",
                   WIZARD101: "Wiz",
                   PIRATE101: "Pirate"}

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

# Slash command information
command_uptime_name = "uptime"
command_uptime_description = "Displays how long Atmobot has been online for."

command_meme_name = "meme"
command_meme_description = "Posts a random meme relevant to The Atmoplex Discord Server."

command_deepfake_name = "deepfake"
command_deepfake_description = "Posts a deepfake of a person or character related to Kingsisle."
command_deepfake_arg_directory_name = "directory"
command_deepfake_arg_directory_description = "Choose a specific category to retrieve a deepfake from."

# Posted when a new test revision has been detected, and the bot is about to commence with auto-spoilers
spoilers_incoming_twitter = "Hello! I am Atmobot.\nThe Lemuria Test Realm files have just updated, so I'm here to spoil a few things automatically! Plex is currently datamining manually at the moment, so enjoy these automatic spoilers while you wait.\nAny automatically posted tweets will begin with [BOT]."
spoilers_incoming_discord = "Hello! I am Atmobot.\nThe Lemuria Test Realm files have just updated, so I'm here to spoil a few things automatically! Plex is currently datamining manually at the moment, so enjoy these automatic spoilers while you wait.\nCheck out these 3 new channels:"
