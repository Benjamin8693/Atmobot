# Default settings
default_settings = {
    "game_id": 0,
    "bot_token": "ODYxNDQ4NjI2NTU4MjA1OTUy.YOJ8jQ.kql-_eSMOcC7QnUYvRXtg4NFvl0",
    "subscribed_guilds": [231218732440092675],
    "last_startup": "",
    "revision_info_live": [],
    "revision_info_test": [],
    "fetch_revision_on_startup": False
}

settings_path = "settings.json"

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

default_revision_range = 5000

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
COMMAND_UPTIME_NAME = "uptime"
COMMAND_UPTIME_DESCRIPTION = "Displays how long Atmobot has been online for."

COMMAND_MEME_NAME = "meme"
COMMAND_MEME_DESCRIPTION = "Posts a random meme relevant to The Atmoplex Discord Server."

COMMAND_DEEPFAKE_NAME = "deepfake"
COMMAND_DEEPFAKE_DESCRIPTION = "Posts a deepfake of a person or character related to Kingsisle."
COMMAND_DEEPFAKE_ARG_DIRECTORY_NAME = "directory"
COMMAND_DEEPFAKE_ARG_DIRECTORY_DESCRIPTION = "Choose a specific category to retrieve a deepfake from."
