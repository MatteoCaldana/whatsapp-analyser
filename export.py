# -*- coding: utf-8 -*-

from functools import reduce

# export chat database as .csv file
def exporter(chat_db, filename, include_message, settings):
    sep = settings["csv_separator"]
    outfile = open(settings["savepath"]+filename+".csv", "w", encoding='utf-8')
    
    tmp = chat_db[1]
    for key in tmp["time"]:
        outfile.write(key)
        outfile.write(sep)
    if include_message:
        outfile.write("weekday,posix,sender_id,type,message\n")
    else:
        outfile.write("weekday,posix,sender_id,type\n")
        
    for text in chat_db:
        
        for key in text["time"]:
            outfile.write( str(text["time"][key])+sep )

        outfile.write( str(text["datetime"].weekday())+sep )
        outfile.write( str(text["posix"])             +sep )
        outfile.write( str(text["sender_id"])         +sep )
        outfile.write( str(text["type"]) )
        if include_message:
            outfile.write(",\"")
            outfile.write(text["message"].replace("\n"," "))
            outfile.write("\"\n")
        else:
            outfile.write("\n")
    outfile.close()
    print("\tSaved succesfully", filename+".csv")

    return

# export a table made of dictionary with elements dictionaries as .csv file
def export_table(dictionary, filename, settings):

    sep = settings["csv_separator"]
    outfile = open(settings["savepath"]+filename+".csv", "w", encoding='utf-8')

    keys = [k for k in dictionary]
    keys.sort()

    outfile.write(',')
    for key in keys:
        outfile.write(key+sep)
    outfile.write('\n')

    for k1 in keys:
        outfile.write(k1+sep)
        for k2 in keys:
            if k1 != k2:
                outfile.write(str(dictionary[k1][k2]))
            outfile.write(sep)
        outfile.write('\n')

    outfile.close()
    print("\tSaved succesfully", filename+".csv")

    return

# export a dictionary as a .csv file
def export_dict(d, filename, settings):
    sep = settings["csv_separator"]
    filename = filename.replace(" ","")
    
    sorted_words = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
    num_words = reduce((lambda x, y: x + y), list(map(lambda x: x[1], sorted_words)))
    
    outfile = open(settings["savepath"]+filename+"_used_words.csv", "w", encoding='utf-8')
    outfile.write("word,occurences,expected_period\n")
    for pair in sorted_words:
        outfile.write(pair[0]+sep)
        outfile.write(str(pair[1])+sep)
        outfile.write(str(num_words/pair[1])+"\n")
    outfile.close()
    print("\tSaved succesfully", filename+"_used_words.csv")
    
    return