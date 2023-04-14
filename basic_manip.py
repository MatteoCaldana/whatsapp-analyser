# -*- coding: utf-8 -*-

import re

def basic_stats(chat_db, settings):
    basic_stat = {}
    for text in chat_db:
        if text["sender"] in basic_stat:
            basic_stat[text["sender"]][text["type"]] += 1
        else:
            basic_stat[text["sender"]] = [0] * (len(settings["mediatype"]) + 3)
            basic_stat[text["sender"]][text["type"]] = 1
    return basic_stat

def mean_length(chat_db, basic_stat):
    mean_length = {}
    for text in chat_db:
        if text["type"] == 0:
            if text["sender"] in mean_length:
                mean_length[text["sender"]] += len(text["message"])
            else:
                mean_length[text["sender"]] = len(text["message"])
    for person in mean_length:
        mean_length[person] /= basic_stat[person][0] 
    return mean_length

def print_stats(basic_stat, mean_len, settings): 
    sep = settings["csv_separator"]
    outfile = open(settings["savepath"]+"basic_stats.csv", "w", encoding='utf-8')
    outfile.write("name,#text,#media,#deleted,")
    for key in settings["mediatype"]:
        outfile.write("#"+key+sep)
    outfile.write("mean_length\n")
    
    for name in basic_stat:
        outfile.write(name+sep)
        for n in basic_stat[name]:
            outfile.write(str(n)+sep)
        if name in mean_len:
            outfile.write(str(mean_len[name])+"\n")
        else:
            outfile.write("NaN\n")
    outfile.close()
    print("\tSaved succesfully basic_stats.csv")

    return
      
def used_words(chat_db):
    dictionary = {}
    for text in chat_db:
        if text["type"] == 0:
            if text["sender"] not in dictionary:
                dictionary[text["sender"]] = {}
    
    for text in chat_db:
        if text["type"] == 0:
            temp = re.split("\W", text["message"])
            name = text["sender"] 
            for word in temp:
                if word != '' :
                    word = word.lower()
                    if word in dictionary[name]:
                        dictionary[name][word] += 1
                    else:
                        dictionary[name][word] = 1
    return dictionary