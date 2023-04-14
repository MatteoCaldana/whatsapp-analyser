# -*- coding: utf-8 -*-

# returns list of texts that start a conversation
def conversation_start(chat_db, threshold):
    data = []
    
    for i in range(1, len(chat_db)):
        if chat_db[i]["posix"] - chat_db[i-1]["posix"] > threshold:
            data.append(chat_db[i])
        
    return data

# returns a list of "conversation"s
def extract_conversations(chat_db, threshold):
    conversations = []

    users = set(map(lambda x: x["sender"], chat_db))

    conversations.append(initialize_conversation(chat_db[0], users, 0))
    if chat_db[0]["sender"] != chat_db[1]["sender"]:
        update_followup_tab(conversations[-1]["followup_tab"], chat_db, 0, users, threshold)

    for i in range(1, len(chat_db)):

        if i % 721 == 0:
            print("Splitting chat into conversations, at %d %%" % int(i*100/len(chat_db)), end="\r")

        if chat_db[i]["posix"] - chat_db[i-1]["posix"] > threshold:
            conversations[-1]["end"] = chat_db[i-1]["datetime"]
            conversations.append(initialize_conversation(chat_db[i], users, i))
        else:
            conversations[-1]["n_texts"][chat_db[i]["sender"]] += 1
            conversations[-1]["n_chars"][chat_db[i]["sender"]] += len(chat_db[i]["message"])
            if chat_db[i]["type"] != 0:
                conversations[-1]["n_media"][chat_db[i]["sender"]] += 1

            if i < len(chat_db)-1:
                if chat_db[i]["sender"] != chat_db[i+1]["sender"]:
                    update_followup_tab(conversations[-1]["followup_tab"], chat_db, i, users, threshold)

    return conversations

# defines the structure of a "conversation"
def initialize_conversation(text, users, idx):

    conversation = {
        "start":        text["datetime"],
        "end":          text["datetime"],
        "start_id":     idx,
        "n_texts":      {},
        "n_chars":      {},
        "n_media":      {},
        "followup_tab": initialize_followup_tab(users)
    }
    for user in users:
        conversation["n_texts"][user] = 0
        conversation["n_chars"][user] = 0
        conversation["n_media"][user] = 0

    conversation["n_texts"][text["sender"]] += 1
    conversation["n_chars"][text["sender"]] += len(text["message"])
    if text["type"] != 0:
        conversation["n_media"][text["sender"]] += 1
    
    return conversation

# define the structure of a table of followup times
def initialize_followup_tab(users):

    # followup_tab[u1][u2] is the time of followup that u2 has took to answer u1 text
    followup_tab = {}

    for u1 in users:
        followup_tab[u1] = {}
        for u2 in users:
            if u1 != u2:
                followup_tab[u1][u2] = []

    return followup_tab

# updates the followup table wrt the followup time of all the user to the text chat_db[idx]
def update_followup_tab(followup_tab, chat_db, idx, users, threshold):

    sender = chat_db[idx]["sender"]

    i = 1
    n = len(chat_db)-1
    max_idx = min([i*20+idx, n])
    while chat_db[max_idx]["posix"] - chat_db[idx]["posix"] < threshold:
        i += 1
        max_idx = min([i*20+idx, n])
        if max_idx == n:
            break

    for u in users:
        if u != sender:
            followup_tab[sender][u].append( min_followup(u, chat_db, idx, threshold, max_idx) )

    return

# returns the minimum followup time of the user u to the text chat_db[idx]
def min_followup(u, chat_db, idx, threshold, max_idx):

    for i in range(idx+1, max_idx+1):
        if chat_db[i]["sender"] == u:
            followup = chat_db[i]["posix"] - chat_db[idx]["posix"]
            if followup < threshold:
                return followup

    return float('Inf')

# given the conversations returns the mean follow-up times for each couple of users
# and the answer rate
def flatten_followup(conversations):

    followup_tab = conversations[0]["followup_tab"].copy()

    for i in range(1, len(conversations)):
        for k1 in conversations[i]["followup_tab"]:
            for k2 in conversations[i]["followup_tab"][k1]:
                followup_tab[k1][k2] += conversations[i]["followup_tab"][k1][k2]
    
    answer_rate = {}
    for k1 in followup_tab:
        answer_rate[k1] = {}
        for k2 in followup_tab[k1]:
            answer_rate[k1][k2] = followup_tab[k1][k2].count(float('Inf'))

    for k1 in followup_tab:
        for k2 in followup_tab[k1]:
            followup_tab[k1][k2] = list(filter(lambda x: x != float('Inf'), followup_tab[k1][k2]))

    for k1 in followup_tab:
        for k2 in followup_tab[k1]:
            n = len( followup_tab[k1][k2] )
            s = sum(followup_tab[k1][k2])
            [n, s] = [n, s] if int(n) else [float('NaN')]*2
            answer_rate [k1][k2] = n / ( answer_rate[k1][k2] + n )
            followup_tab[k1][k2] = s / n

    return [followup_tab, answer_rate]

