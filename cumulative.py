# -*- coding: utf-8 -*-

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
import numpy as np


def cumulative(chat_db, settings):
    time = {}
    n = {}
    dates = {}
    for text in chat_db:
        if text["sender"] in time:
            time[text["sender"]].append(text["datetime"])
        else:
            time[text["sender"]] = [text["datetime"]]

    for name in time:
        n[name] = np.cumsum([1] * len(time[name]))
        dates[name] = mdates.date2num(time[name])

    fig, ax = plt.subplots()
    legend = []
    for name in time:
        ax.plot(time[name], n[name])
        legend.append(name)
    ax.legend(legend, loc=0, prop={"size": 6})
    ax.grid()
    ax.tick_params(axis="both", labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m.%y"))
    plt.title("Cumulative number of texts")
    fig.savefig(
        settings["savepath"] + "cumulative_number_text.png", dpi=settings["dpi"]
    )
    print("\tSaved succesfully cumulative_number_text.png")

    return


def cumulative_char(chat_db, settings):
    time = {}
    n = {}
    dates = {}

    for text in chat_db:
        if text["type"] == 0:
            if text["sender"] in n:
                n[text["sender"]].append(n[text["sender"]][-1] + len(text["message"]))
                time[text["sender"]].append(text["datetime"])
            else:
                n[text["sender"]] = [len(text["message"])]
                time[text["sender"]] = [text["datetime"]]

    for name in time:
        dates[name] = mdates.date2num(time[name])

    fig, ax = plt.subplots()
    legend = []
    for name in time:
        ax.plot(time[name], n[name])
        legend.append(name)
    ax.legend(legend, loc=0, prop={"size": 6})
    ax.grid()
    ax.tick_params(axis="both", labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m.%y"))
    plt.title("Cumulative number of chars")
    fig.savefig(
        settings["savepath"] + "cumulative_number_char.png", dpi=settings["dpi"]
    )
    print("\tSaved succesfully cumulative_number_char.png")

    return
