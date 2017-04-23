import time
import os, glob
import csv, json
import numpy as np
import matplotlib.pyplot as plt

by_stop_line = {}
by_stop = {}
by_line = {}

def aggregate(filename):
    split = filename[12:].split("_")
    stop = split[0]
    line = split[1] + "_" + split[2][:-4]
    name = stop + "_" + line
    # keep prediction times for each trip for each day
    pre_dict = {}
    min_dict = {}

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
        for row in reader:
            if row[5] == "tripTag":
                continue
            p = time.localtime(int(row[0][:-3]))
            trip_day = str(p.tm_yday) + row[5]
            if trip_day not in pre_dict.keys():
                pre_dict[trip_day] = [p]
                min_dict[trip_day] = [row[2]]
            else:
                pre_dict[trip_day].append(p)
                min_dict[trip_day].append(row[2])
    # calculate arrival and prediction times for each stop
    trips = {}
    trips_alt = {}
    for t in pre_dict.keys():
        data = {}
        until = 90
        i = 0
        while i < len(min_dict[t]):
            if int(min_dict[t][i]) < 25:
                break
            until = int(min_dict[t][i])
            i += 1
        if (until >= 25 and until <= 35):
            data['arrival'] = pre_dict[t][-1]
            data['prediction'] = pre_dict[t][i - 1]
            data['delay'] = time.mktime(pre_dict[t][-1]) - time.mktime(pre_dict[t][i - 1])
            trips[t] = data
            trips_alt[t + "_" + stop] = data
    by_stop_line[name] = trips
    if stop in by_stop.keys():
        by_stop[stop].update(trips)
    else:
        by_stop[stop] = trips
    if line in by_line.keys():
        by_line[line].update(trips_alt)
    else:
        by_line[line] = trips_alt

# each of these returns summary stats, as well as delays in chronological order
def get_stats(database, query):
    stats = {}
    times = []
    delays = []
    time_to_delay = {}
    late = 0
    vlate = 0
    hist_data = [0] * 36; #30 min time intervals from 6AM to 12AM
    entries = database[query]
    for i in entries.keys():
        t = entries[i]['arrival']
        d = entries[i]['delay']
        times.append(t)
        delays.append(d)
        minutes = t[3] * 60 + t[4] # minutes since midnight
        index = (minutes - 360) // 30
        if index < 0:
            index = 0
        if index > 35:
            index = 35
        # increment count if late
        if (d > 300):
            late += 1
            hist_data[index] += 1
        if (d > 600):
            vlate += 1

    stats['mean'] = np.mean(delays)
    stats['median'] = np.median(delays)
    stats['std'] = np.std(delays)
    stats['late'] = late
    stats['vlate'] = vlate
    stats['length'] = len(times)
    stats['hist'] = hist_data
    return stats

# utility functions
def sformat(seconds):
    return "%02d:%02d" % (int(seconds) // 60, int(seconds) % 60)

def sort_by_time(time):
    return time[3] * 10000 + time[4] * 1000 + time[5]

def main():
    summary = {}

    print("Aggregating data from ACTransit polling...")
    for filename in glob.glob("predictions/*_*.csv"):
        aggregate(filename)
        print("\t- " + filename)
    print("Aggregation complete.")

    # print(by_stop_line["50400_65_To Senior Ave. loop"])
    print("Calculating statistics by stop and line...")
    for sl in by_stop_line.keys():
        stats = get_stats(by_stop_line, sl)
        summary[sl] = stats
        print("\t- " + sl)
    print("Calculation 1/3 complete.")

    print("Calculating statistics by stop...")
    for s in by_stop.keys():
        stats = get_stats(by_stop, s)
        summary[s] = stats
        print("\t- " + s)
    print("Calculation 2/3 complete.")

    print("Calculating statistics by line...")
    for l in by_line.keys():
        stats = get_stats(by_line, l)
        summary[l] = stats
        print("\t- " + l)
    print("Calculation 3/3 complete.")

    with open('data.json', 'w') as fp:
        json.dump(summary, fp)

main()
