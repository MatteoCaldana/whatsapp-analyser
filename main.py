# -*- coding: utf-8 -*-
import time
import numpy as np

from initialize import initialize
from raw_manip import separate_chat_file
from basic_manip import basic_stats, mean_length, print_stats, used_words
from cumulative import cumulative, cumulative_char
from histogram import time_histograms, text_histograms, tgap_histogram
from export import exporter, export_table, export_dict
from conversation import conversation_start, extract_conversations, flatten_followup
from operator import sub

start = time.time()

print("Reading 'config.json'")
settings = initialize("config.json")
chat_db = separate_chat_file(settings)
print("Sorting based on POSIX timestamp")
chat_db.sort(key=lambda x: x["posix"])
print("Database formed,", len(chat_db), "texts found")

print("Time elapsed", time.time() - start)

print("Basic stats")
basic_stat = basic_stats(chat_db, settings)
mean_len = mean_length(chat_db, basic_stat)
print_stats(basic_stat, mean_len, settings)

print("Counting most used words")
d = used_words(chat_db)
# for name in d:
#     save_dict(d[name], name, settings)
#
# print("Saving database as .csv")
# exporter(chat_db, "database", True, settings)
#
print("Saving figures")
cumulative(chat_db, settings)
cumulative_char(chat_db, settings)
time_histograms(chat_db, settings)
text_histograms(chat_db, settings)
tgap_histogram(chat_db, settings)

# how many seconds need to pass between two texts to be considered a different conversation
# to make an idea of a good estimate use the minumun shown in tgap_histogram()
threshold = 5 * 3600

# print("WARNING: Filtering!")
# ## filter by field of the text
# chat_db = list(filter(lambda x: x["posix"] >= 1535759459.0, chat_db))
# ## filter that takes only messages that stat (an heuristically defined) conversation
# chat_db = conversation_start(chat_db, threshold)

print("Manip on heuristically defined conversation")
convs = extract_conversations(chat_db, threshold)
[mean_followup, answer_rate] = flatten_followup(convs)
export_table(mean_followup, "mean_followup", settings)
export_table(answer_rate, "answer_rate", settings)

table = list(mean_followup.keys())
table.remove("")

mean_followup_array = np.empty((len(table),) * 2)
answer_rate_array = np.empty((len(table),) * 2)
for i in range(len(table)):
    for j in range(len(table)):
        try:
            mean_followup_array[i, j] = mean_followup[table[i]][table[j]]
            answer_rate_array[i, j] = answer_rate[table[i]][table[j]]
        except:
            mean_followup_array[i, j] = float("nan")
            answer_rate_array[i, j] = float("nan")
