# -*- coding: utf-8 -*-

import json
import os


def check_settings(settings):

    for key in [
        "filename",
        "yearin2000",
        "time_re",
        "plaintext_re",
        "mediatext_re",
        "emptytext_re",
        "nameseparator",
        "contacts",
        "mediatype",
        "dpi",
        "savepath",
        "csv_separator",
    ]:
        if key not in settings:
            print("WARNING, 'config.json' does not contain", key)
    for key in [
        "?P<year>",
        "?P<month>",
        "?P<day>",
        "?P<hour>",
        "?P<minute>",
        "?P<second>",
    ]:
        if settings["time_re"].find(key) == -1:
            print("WARNING, 'time_re' does not contain", key)
    if not os.path.isdir(settings["savepath"]):
        print("WARNING, 'savepath' does not exist, creating:", settings["savepath"])
        os.mkdir(settings["savepath"])
    return


def initialize(config_path):
    with open(config_path, encoding="utf-8") as json_data_file:
        settings = json.load(json_data_file)
    check_settings(settings)
    return settings
