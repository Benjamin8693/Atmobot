# Local packages
from hashlib import new
import bot_globals

# Built-in packages
import queue
import threading
import os, requests

# Individual bruteforce function
def bruteforce_list(revision_list, version_list, q):

    # Iterate over all the versions we want to check
    for version in version_list:

        # And all of the revisions in our list
        for revision in revision_list:

            # Generate a patch link to test with
            link = "http://testversionec.us.wizard101.com/WizPatcher/V_r{revision}.{version}/Windows/LatestFileList.bin".format(revision=revision, version=version)
            
            # Only report back if we get a valid error code
            if requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}).status_code == 200:
                new_revision = ["V_r{revision}".format(revision=revision), version]
                q.put(new_revision)

# Bruteforce a revision from the patcher
async def bruteforce_revision(revision_start, revision_range, version_list, q):

    # Range of revisions to bruteforce
    revision_end = revision_start + revision_range
    revision_list = list(range(revision_start, revision_end))

    # Divide our revisions between 16 processes
    revision_lists = [[] for i in range(16)]
    list_length = len(revision_lists)

    i = 0
    while revision_list:
        revision_lists[i].append(revision_list.pop(0))
        i = (i + 1) % list_length

    # Execute all our processes
    processes = []
    for i, l in enumerate(revision_lists):
        p = threading.Thread(target=bruteforce_list, args=(l, version_list, q))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()

class Bruteforcer:

    def __init__(self, bot):

        self.bot = bot

    async def start(self, revision_start, revision_range, version_list):
        q = queue.Queue()

        await bruteforce_revision(revision_start, revision_range, version_list, q)

        new_revision = q.get()
        return new_revision
