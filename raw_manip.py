# -*- coding: utf-8 -*-

import re
import datetime


MEDIA_TABLE = ["plaintext", "unknown media", "deleted", "action"]


def separate_chat_file(settings):
    # open file
    print("Reading", settings["filename"])
    chat_file = open(settings["filename"], "r", encoding="utf-8")

    # initialize variables
    add = 0 if settings["yearin2000"] else 2000
    line_count = 0
    chat_db = []
    time_re = settings["time_re"]
    plain_re = settings["plaintext_re"][0] + time_re + settings["plaintext_re"][1]
    media_re = settings["mediatext_re"][0] + time_re + settings["mediatext_re"][1]
    empty_re = settings["emptytext_re"][0] + time_re + settings["emptytext_re"][1]

    media_table = MEDIA_TABLE + settings["mediatype"]

    if len(settings["contacts"]) == 0:
        print("WARNING: no contact was specified")
        settings["contacts"].append("(.*?)")

    for line in chat_file:

        # print progress
        line_count += 1
        if line_count % 987 == 0:
            print("At line", line_count)
        # check if the line is a text
        newtext_match = re.match(plain_re, line)
        if newtext_match:
            type_id = 0
        # check if is a media
        tmp = re.match(media_re, line)
        if tmp:
            newtext_match = tmp
            type_id = 1
        # check if is a deleted text
        tmp = re.match(empty_re, line)
        if tmp:
            newtext_match = tmp
            type_id = 2
        # effective parsing of the text
        if newtext_match:
            time = newtext_match.groupdict()
            # residual is the string that isn't the piece matched by plaintext_re,
            # i.e. everything but the time
            residual = re.split(time_re, line)[-1]

            # loop among members to check who sent the text
            name = ""
            sender_id = 0

            done = False
            for i in range(len(settings["contacts"])):
                person = settings["contacts"][i]
                split = re.split("^" + person + settings["nameseparator"], residual)
                if len(split) >= 2:
                    if person == "(.*?)" and len(split) == 3:
                        person = split[1]
                        split[1] = split[2]
                    name = person
                    message = split[1]
                    sender_id = i + 1
                    done = True
                    break
            if not done:
                type_id = 3

            if name == "":
                message = residual
            # check what type of media is
            if type_id == 1:
                for i in range(len(settings["mediatype"])):
                    if residual.find(settings["mediatype"][i]) != -1:
                        type_id = i + 4
            # convert string to integer in time
            for key in ["year", "month", "day", "hour", "minute", "second"]:
                if key in time:
                    time[key] = int(time[key])
                else:
                    time[key] = 0
            time["year"] += add

            # build the text to insert in the list
            text = {
                "time": {
                    "year": time["year"],
                    "month": time["month"],
                    "day": time["day"],
                    "hour": time["hour"],
                    "minute": time["minute"],
                    "second": time["second"],
                },
                "datetime": datetime.datetime(
                    time["year"],
                    time["month"],
                    time["day"],
                    time["hour"],
                    time["minute"],
                    time["second"],
                ),
                "sender": name,
                "sender_id": sender_id,
                # type 0 indicates a standard message made of text, not a media
                # type 1 indicates a not recognised media type
                # type 2 indicates a deleted text
                # type > 2 indicates is of type settings["mediatype"][type-3]
                "type_id": type_id,
                "type": media_table[type_id],
                "message": message,
            }
            text["posix"] = text["datetime"].timestamp()

            chat_db.append(text)
        else:
            # TODO handle better the case in which 1st read line isn't a proper text
            if line_count == 1:
                print(
                    "First line of the file isn't matched by 'plaintext_re', \
                    please check that the regular expression and that chat file \
                    is plain UTF-8"
                )
            # the line is of the previous text
            chat_db[-1]["message"] += line
    return chat_db
