# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
import numpy as np
from math import log

# distribution of the timestamp of the texts
def time_histograms(chat_db, settings):
    time = []
    month = []
    weekday = []
    daytime = []
    for text in chat_db:
        time.append(mdates.date2num(text["datetime"]))
        month.append(text["time"]["month"] + (text["time"]["day"] - 1) / 30)
        weekday.append(text["datetime"].weekday())
        daytime.append(text["time"]["hour"] + text["time"]["minute"] / 60)

    fig, ax = plt.subplots()
    ax.hist(time, bins=50, edgecolor="black")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m.%y"))
    plt.title("Message distribution in time")
    fig.savefig(settings["savepath"] + "texts_distr_in_time.png", dpi=settings["dpi"])
    print("\tSaved succesfully texts_distr_in_time.png")

    fig, ax = plt.subplots()
    ax.hist(month, bins=24, edgecolor="black")
    plt.xticks(
        np.arange(1.5, 13.5, 1.0),
        (
            "gen",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ),
    )
    plt.title("Message distribution during year")
    fig.savefig(settings["savepath"] + "texts_distr_in_months.png", dpi=settings["dpi"])
    print("\tSaved succesfully texts_distr_in_months.png")

    fig, ax = plt.subplots()
    ax.hist(weekday, bins=7, edgecolor="black")
    plt.xticks(
        np.linspace(0.5, 5.5, 7), ("mon", "tue", "wen", "thu", "fri", "sat", "sun")
    )
    plt.title("Message distribution during week")
    fig.savefig(settings["savepath"] + "texts_distr_in_week.png", dpi=settings["dpi"])
    print("\tSaved succesfully texts_distr_in_week.png")

    fig, ax = plt.subplots()
    ax.hist(daytime, bins=48, edgecolor="black")
    plt.title("Message distribution during day")
    fig.savefig(settings["savepath"] + "texts_distr_in_day.png", dpi=settings["dpi"])
    print("\tSaved succesfully texts_distr_in_day.png")

    return


# histogram of the length of the messages, by user
# uses linear-log binning
def text_histograms(chat_db, settings):
    # parameters
    q = 99  # percentile at which stop linear binning
    b = 1.2  # parameter of logarithm binning, if len1*b=len2 then len1 and len2 are 1 bin apart
    nbins = 50  # number of bins

    text_length_distr = {}

    for text in chat_db:
        if text["type_id"] == 0:
            if text["sender"] not in text_length_distr:
                text_length_distr[text["sender"]] = []

    for text in chat_db:
        if text["type_id"] == 0:
            txt_len = len(text["message"])
            if txt_len > 0:
                text_length_distr[text["sender"]].append(txt_len)

    max_len = 0  # max text length
    max_per = 0  # max q-th percentile of the length among sender
    for sender in text_length_distr:
        max_len = max(text_length_distr[sender] + [max_len])
        max_per = max([np.percentile(text_length_distr[sender], q), max_per])

    # perform a linear-log transformation
    # linear is good to display short text distribution, log for long texts
    bin_len = max_per / nbins
    log_base = b ** (1 / bin_len)
    for sender in text_length_distr:
        for i in range(0, len(text_length_distr[sender])):
            if text_length_distr[sender][i] > max_per:
                text_length_distr[sender][i] = max_per + log(
                    text_length_distr[sender][i] - max_per + 1, log_base
                )

    max_len = max_per + log(max_len, log_base)

    ylim = 0
    for sender in text_length_distr:
        ylim = max([max(np.histogram(text_length_distr[sender], bins=nbins)[0]), ylim])

    for sender in text_length_distr:
        fig, ax = plt.subplots()
        ax.hist(
            text_length_distr[sender],
            bins=nbins,
            edgecolor="black",
            log=True,
            range=(0, max_len),
        )
        plt.xticks(
            np.concatenate(
                (np.arange(0, max_per, 50), np.arange(max_per, max_len, 40))
            ),
            np.concatenate(
                (
                    np.arange(0, max_per, 50),
                    log_base ** (np.arange(max_per, max_len, 40) - max_per)
                    + max_per
                    - 1,
                )
            ).astype(int),
        )
        plt.ylim((0.7, ylim))
        fig.savefig(
            settings["savepath"] + sender.replace(" ", "") + "_texts_len_distr.png",
            dpi=settings["dpi"],
        )
        print("\tSaved succesfully", sender.replace(" ", "") + "_texts_len_distr.png")

    return


# distribution of the time gap between texts
def tgap_histogram(chat_db, settings):

    tgap_lim = 300  # seconds to consider two consecutives messages different

    distribution = []
    for i in range(0, len(chat_db) - 1):
        # consider two consecutives messages as different if the sender is different or too much time is passed
        if (
            chat_db[i]["sender"] != chat_db[i + 1]["sender"]
            or chat_db[i + 1]["posix"] - chat_db[i]["posix"] > tgap_lim
        ):
            distribution.append(chat_db[i + 1]["posix"] - chat_db[i]["posix"] + 1)

    fig, ax = plt.subplots()
    ax.hist(np.log10(distribution), bins=40, edgecolor="black")
    plt.xticks(
        np.log10([1, 10, 60, 600, 3600, 5 * 3600, 86400, 7 * 86400, 30 * 86400]),
        ("1s", "10s", "1min", "10min", "1h", "5h", "1d", "7d", "30d"),
    )
    plt.title("Time gap between messages")
    fig.savefig(settings["savepath"] + "time_gap_distr.png", dpi=settings["dpi"])
    print("\tSaved succesfully time_gap_distr.png")

    return
