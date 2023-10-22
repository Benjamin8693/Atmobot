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

# Scheduler template config
scheduler_template = {
    "date": [{"name": "Good Morning Atmoplexia",
              "active": False,
              "initial_time": 0,
              "method": "send_to_discord",
              "args": [963182643816579107, "Good morning Atmoplexia!"]}],
    "tick": [{"name": "Good Morning Atmoplexia",
              "active": True,
              "initial_time": 0,
              "delay": 10,
              "method": "send_to_discord",
              "args": [963182643816579107, "Good morning Atmoplexia!"]}],
    "manual": [{"name": "Good Morning Atmoplexia",
                "method": "send_to_discord",
                "args": [963182643816579107, "Good morning Atmoplexia!"]}]
}

# File name for the scheduler config
scheduler_path = "scheduler.json"

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

# Server command
command_server_name = "server"
command_server_description = "I wonder what this one does?"

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
command_days_formatted = "There {verb} **{amount} {factor}{s}** until Test Realm Watch ({date}).\nTest Realm Watch is the first day of the season in which Test Realm has a chance to release."
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

# Bruteforce command
command_bruteforce_name = "bruteforce"
command_bruteforce_description = "Opens the control panel for one of our bruteforcers."
command_bruteforce_arg_mode_name = "mode"
command_bruteforce_arg_mode_description = "Choose the bruteforcing mode to access."

COMMAND_BRUTEFORCE_MODE_IMAGE = 0
COMMAND_BRUTEFORCE_MODE_WEBSITE = 1
COMMAND_BRUTEFORCE_MODE_REVISION = 2

bruteforce_mode_to_index = {"image": COMMAND_BRUTEFORCE_MODE_IMAGE,
                            "website": COMMAND_BRUTEFORCE_MODE_WEBSITE,
                            "revision": COMMAND_BRUTEFORCE_MODE_REVISION}

bruteforce_index_to_mode = {COMMAND_BRUTEFORCE_MODE_IMAGE: "image",
                            COMMAND_BRUTEFORCE_MODE_WEBSITE: "website",
                            COMMAND_BRUTEFORCE_MODE_REVISION: "revision"}

# Bruteforcer template config
bruteforcer_template = {
    "image": [{"profile_name": "Default Profile",
               "profile_active": True,
               "run_confirmation": True,
               "image_names": [],
               "image_names_successes": [],
               "image_extensions": [".jpg", ".png", ".gif"],
               "image_prefixes": [""],
               "image_suffixes": ["", "01", "02", "03", "04", "05", "01_600", "02_600", "03_600", "04_600", "05_600", "_Lead", "_compressed", "_Lead_compressed_600", "_600", "_600b", "_Mercedes", "_watermark_contrast_600", "_watermark_contrast"],
               "request_urls": ["https://edgecast.wizard101.com/image/free/Wizard/C/Wizard-Society/Patch-Notes/{}?v=1", "https://edgecast.wizard101.com/file/free/Wizard/C/Wizard-Society/Patch-Notes/{}?v=1"],
               "request_threading": False,
               "request_threading_count": 16,
               "request_cooldown": 0.05,
               "request_error_threshold": 5,
               "request_error_retry_after": 300,
               "remove_image_when_found": True,
               "discord_notify": True,
               "discord_channel": 0,
               "discord_message": "A new image has been detected!",
               "twitter_notify": False,
               "twitter_message": "A new image has been detected!"}],
    "website": [],
    "revision": []
}

# File name for the bruteforcer config
bruteforcer_path = "bruteforcer.json"

BRUTEFORCE_PROFILE_INFO = 0
BRUTEFORCE_PROFILE_INDEX = 1

# Config options for bruteforcing in general
BRUTEFORCE_PROFILE_NAME = 0
BRUTEFORCE_PROFILE_ACTIVE = 1

# Config options for image bruteforcing mode
BRUTEFORCE_IMAGE_RUN_CONFIRMATION = 2
BRUTEFORCE_IMAGE_IMAGE_NAMES = 3
BRUTEFORCE_IMAGE_IMAGE_NAMES_SUCCESSES = 4
BRUTEFORCE_IMAGE_IMAGE_EXTENSIONS = 5
BRUTEFORCE_IMAGE_IMAGE_PREFIXES = 6
BRUTEFORCE_IMAGE_IMAGE_SUFFIXES = 7
BRUTEFORCE_IMAGE_REQUEST_URLS = 8
BRUTEFORCE_IMAGE_REQUEST_THREADING = 9
BRUTEFORCE_IMAGE_REQUEST_THREADING_COUNT = 10
BRUTEFORCE_IMAGE_REQUEST_COOLDOWN = 11
BRUTEFORCE_IMAGE_REQUEST_ERROR_THRESHOLD = 12
BRUTEFORCE_IMAGE_REQUEST_ERROR_RETRY_AFTER = 13
BRUTEFORCE_IMAGE_REMOVE_IMAGE_WHEN_FOUND = 14
BRUTEFORCE_IMAGE_DISCORD_NOTIFY = 15
BRUTEFORCE_IMAGE_DISCORD_CHANNEL = 16
BRUTEFORCE_IMAGE_DISCORD_MESSAGE = 17
BRUTEFORCE_IMAGE_TWITTER_NOTIFY = 18
BRUTEFORCE_IMAGE_TWITTER_MESSAGE = 19

bruteforce_embed_comments = "__Info__"
bruteforce_embed_comments_idle = "The bruteforcer is currently idle."
bruteforce_back_button = "Back"
bruteforce_close_button = "Close"

bruteforce_image_control_panel_name = "__Bruteforcer Control Panel__"
bruteforce_image_control_panel_instructions = "**Run** - Run the bruteforcer using the current profile\n**Profiles** - Add, remove, or edit bruteforcing profiles\n**Close** - Closes the bruteforcer control panel"

bruteforce_image_run_button = "Run"
bruteforce_image_run_name = "__Run Bruteforce__"
bruteforce_image_run_instructions = "**Start** - Start a bruteforce using the current profile\n**Loop** - Start a bruteforce on loop using the current profile\n**Schedule** - Schedule when the next bruteforce with this profile should occur\n**Back** - Go back to the bruteforcer control panel"
bruteforce_image_run_start_button = "Start"
bruteforce_image_run_loop_button = "Loop"
bruteforce_image_run_schedule_button = "Schedule"
bruteforce_image_run_in_progress_button = "In-Progress"
bruteforce_image_run_inactive_name = "__Bruteforce Inactive__"
bruteforce_image_run_in_progress_name = "__Bruteforce In-Progress__"
bruteforce_image_run_paused_name = "__Bruteforce Paused__"
bruteforce_image_run_completed_name  = "__Bruteforce Completed__"
bruteforce_image_run_progress_embed = "**Bruteforcing query {current_query} of {total_queries}**\n**{percentage}%** completed\n**{estimated_time}** until completion"
bruteforce_image_run_time_to_completion_default = "N/A"

bruteforce_image_profiles_button = "Profiles"

bruteforce_image_settings_button = "Settings"

bruteforce_image_profile_add_term_button = "Add"
bruteforce_image_profile_remove_term_button = "Remove"
bruteforce_image_profile_remove_term_name = "__Remove__"
bruteforce_image_profile_remove_term_instructions = "**Clear** all names from the bruteforce list\n**Remove First** name from the bruteforce list\n**Remove Last** name from the bruteforce list\n**Remove Specific** name from the bruteforce list"

bruteforce_image_browse_terms_button = "Browse"
bruteforce_image_browse_terms_name = "__Bruteforce List__"

# URLs for the bruteforcer to test
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
fallback_revision = 736675
fallback_version_live = "1_510"
fallback_version_live_formatted = "{game}_{version}"
fallback_version_dev = "WizardDev"

version_empty = "{game}_{revision}_{version}"

default_revision_range = 5000

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

BRUTEFORCER_ROUTINE_GAME = 0

BRUTEFORCER_ROUTINE_GAME_WIZARD = 0
BRUTEFORCER_ROUTINE_GAME_PIRATE = 1
BRUTEFORCER_ROUTINE_GAME_BOTH = 2

BRUTEFORCER_ROUTINE_METHOD = 1

BRUTEFORCER_ROUTINE_METHOD_PATCHER = 0
BRUTEFORCER_ROUTINE_METHOD_WEBSITE = 1
BRUTEFORCER_ROUTINE_METHOD_BOTH = 2

BRUTEFORCER_ROUTINE_DURATION = 1
BRUTEFORCER_ROUTINE_FREQUENCY = 2
BRUTEFORCER_ROUTINE_ANNOUNCEMENT_LEVEL = 3

BRUTEFORCER_ROUTINE_ANNOUNCEMENT_LEVEL_NONE = 0
BRUTEFORCER_ROUTINE_ANNOUNCEMENT_LEVEL_MODS = 1
BRUTEFORCER_ROUTINE_ANNOUNCEMENT_LEVEL_ROLE = 2
BRUTEFORCER_ROUTINE_ANNOUNCEMENT_LEVEL_EVERYONE = 3
BRUTEFORCER_ROUTINE_ANNOUNCEMENT_LEVEL_TWEET = 4

BRUTEFORCER_ROUTINE_ANNOUNCEMENT_MESSAGE = 4
BRUTEFORCER_ROUTINE_REPEAT_AFTER_SUCCESS = 5

# Posted when a new test revision has been detected, and the bot is about to commence with auto-spoilers
spoilers_incoming_twitter = "Hello! I am Atmobot.\nThe Test Realm files have just updated, so I'm here to spoil a few things automatically! Plex is datamining manually at the moment, so enjoy these automatic spoilers while you wait.\nAny automatically posted tweets will begin with [BOT]."
spoilers_incoming_discord_title = "Atmobot"
spoilers_incoming_discord_information_title = "Hello! I am Atmobot"
spoilers_incoming_discord_information = "I am a bot created by the Atmoplex team for the purpose of spoiling Test Realm. Test Realm has just updated, so I will begin to post spoilers momentarily."
spoilers_incoming_discord_coming_soon_title = "So what now?"
spoilers_incoming_discord_coming_soon = "I will imminently begin posting in {spoilers_channel}. It may take a while for me to get through everything, but expect messages to appear sporadically as I datamine the update.\n\nIn the meantime, the Atmoplex team is datamining the update manually. Whatever is missed by Atmobot will be posted later. Enjoy these automatic spoilers!"
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
    "CL": "Celestia",
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
    "NV": "Novus",
    "YG": "Yago",
    "WL": "Wallaru",
    "WA": "Wallaru",
    "SI": "Skull Island",
    "MO": "Monquista",
    "MQ": "Monquista",
    "VA": "Valencia",
    "VL": "Valencia",
    "CR": "Cool Ranch",
    "RJ": "Rajah",
    "ED": "El Dorado",
    "TM": "Lighthouse World",
    "NEX": "Nexus City",
    "NC": "Nexus City",
    "TKO": "Tokyo",
    "TK": "Tokyo",
    "RUS": "Russia",
    "RS": "Russia",
    "GR": "Raids",
    "Raids": "Raids"
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
