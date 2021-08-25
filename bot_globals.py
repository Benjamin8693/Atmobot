# Default settings
default_settings = '''{
    "last_startup": "",
    "bot_token": "ODYxNDQ4NjI2NTU4MjA1OTUy.YOJ8jQ.kql-_eSMOcC7QnUYvRXtg4NFvl0",
    "game": 0,
    "service": 1,
    "latest_revision": "r703991.Wizard_1_460",
    "revision_bruteforce": true,
    "wads_to_download": ["Root", "_Shared-WorldData"],
    "download_updated_wads": true
}'''

bot_description = '''Atmobot adds unique functionality to The Atmoplex Discord Server!'''

# Important urls to check
test_patch_client_url = "https://www.wizard101.com/testpatchClient"
update_notes_url = "https://www.wizard101.com/game/community/update-notes/{month}{year}"

URL_CACHE_REQUEST = 0
URL_CACHE_HASH = 1

# Base patcher url
patcher_url = "http://{server}.us.{game_longhand}.com/{game_shorthand}Patcher/{revision}/LatestBuild/Data/GameData/{wad_name}.wad"

# Service information
SERVICE_UNKNOWN = -1
LIVE_REALM = 0
TEST_REALM = 1

service_names = {SERVICE_UNKNOWN: "",
                 LIVE_REALM: "",
                 TEST_REALM: "test"}

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

# Fallback .WAD file used for testing
fallback_wad = "Root"

# Strings that relate the patcher's error code to likeliness of being online
patcher_tips = {200: "The Patcher is online",
                403: "The Patcher may be online",
                404: "The Patcher may be online"}

resources_path = "resources"
deepfakes_path = "deepfakes"
