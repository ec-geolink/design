""" settings.py

    Functions related to saving/load settings.
"""

import json
import os


def initializeSettings(filename):
    """ Read in settings from json file located at `filename` and return
        a Dict of settings.
    """

    settings = {}

    if not os.path.exists(filename):
        return settings

    with open(filename, "rb") as settings_file:
        try:
            settings = json.load(settings_file)
        except ValueError:
            settings = {}

    return settings


def saveSettings(settings, filename):
    """ Save settings in Dict `settings` to json file located at `filename`
    """

    with open(filename, "wb") as settings_file:
        settings_file.write(json.dumps(settings,
                            sort_keys=True,
                            indent=2,
                            separators=(',', ': ')))
