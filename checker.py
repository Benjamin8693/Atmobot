# Local packages
import bot_globals

# Build-in packages
import datetime
import hashlib
import requests
from urllib.request import urlopen, Request

class Checker:

    def __init__(self, bot):
        
        self.bot = bot

        self.url_cache = {}
        
    def startup(self):

        # Hash current website info
        important_urls = self.get_important_urls()
        for url in important_urls:
            url_request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            url_response = urlopen(url_request).read()
            url_hash = hashlib.sha224(url_response).hexdigest()

            self.url_cache[url] = [url_request, url_hash]

    # To grab important urls we should check
    def get_important_urls(self):

        # You know, at first I was just going to reference "self.startup_time", but I realized that in the odd
        # case this bot manages to stay up for more than a few days at a time, it could start producing
        # undesirable results. In which case, we'll grab a new datetime whenever this function is ran.
        current_time = datetime.datetime.now()

        # Grab the month and year strings
        month_string = current_time.strftime("%B").lower()
        year_string = current_time.strftime("%Y")

        # Plug them into our update notes url
        update_notes_url = bot_globals.update_notes_url.format(month=month_string, year=year_string)

        # Return our urls to check
        important_urls = [bot_globals.test_patch_client_url, update_notes_url]
        return important_urls

    # Ran whenver we want to check to see if a url has updated
    def check_url_status(self):

        # Whether one of the urls has changed
        changed = False

        # Iterate over our urls to determine if any have changed
        important_urls = self.get_important_urls()
        for url in important_urls:

            # Just in case something goes wrong here
            try:

                # Load up our prior request and hash
                cache = self.url_cache[url]
                request = cache[bot_globals.URL_CACHE_REQUEST]
                old_hash = cache[bot_globals.URL_CACHE_HASH]

                # Make a new request and hash the response
                new_url_response = urlopen(request).read()
                new_hash = hashlib.sha224(new_url_response).hexdigest()

                # The url has changed
                if old_hash != new_hash:
                    changed = True

                # Insert new hash back into the dict
                cache[bot_globals.URL_CACHE_HASH] = new_hash
                self.url_cache[url] = cache

            # Uh oh, that's not good
            except Exception as e:
                print("Error has occurred: {}".format(e))

        return changed

    # Used to check whether the patcher is online
    def check_patcher(self):

        # Status code of the patcher
        status_code = 0

        # We're making this a try in the case we cannot cannot (which is actually most of the time)
        try:

            # Make a request to the patcher to determine the status code
            patcher_url = self.grab_patcher_url()
            patcher_request = requests.head(patcher_url)
            status_code = patcher_request.status_code

            return status_code

        # If we cannot connect, that's a status code too
        except requests.ConnectionError:

            return status_code

    def grab_patcher_url(self, service=bot_globals.TEST_REALM, server=bot_globals.VERSIONEC, game=bot_globals.WIZARD101, wad=bot_globals.fallback_wad):

        # Grab our server name
        service_name = bot_globals.service_names.get(service)
        server_name = bot_globals.server_options.get(server)
        full_server_name = service_name + server_name

        # Game longhand and shorthand
        game_longhand = bot_globals.game_longhands.get(game)
        game_shorthand = bot_globals.game_shorthands.get(game)

        # Latest revision
        latest_revision = self.bot.bot_settings.get("latest_revision", "")

        # Format everything together into our patcher url
        patcher_url = bot_globals.patcher_url.format(server=full_server_name, game_longhand=game_longhand, game_shorthand=game_shorthand, revision=latest_revision, wad_name=wad)
        return patcher_url
