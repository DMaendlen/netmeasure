#!/usr/bin/python3
"""
netmeasure.sh creates up-/download files that contain network throughput in bps

This analyzer takes those files, parses them and calculates the average
throughput in Mbps at any given timestamp for the 8 servers that are tested.

This average is then plotted.
"""

from collections import OrderedDict
from datetime import datetime

import json
import os

import matplotlib.pyplot as plt


class NetMeasureAnalyzer(object):
    """
    Parse iperf3 results from json files, calculate average per hour
    """

    def __init__(self, working_dir="./results"):
        """
        Setup the parser
        """

        self.working_dir = working_dir
        self.directions = ["upload", "download"]
        self.dirs = []
        self.fig, self.axf = plt.subplots(2, sharex=True)
        self.iperf_results = {}

    def __get_dirs__(self):
        """
        Walk through working_dir and generate a list of result dirs
        """

        for directory in os.listdir(self.working_dir):
            path = os.path.join(self.working_dir, directory)
            if os.path.isdir(path) and directory.startswith('2018'):
                self.dirs.append(path)

        return self.dirs

    def __get_files__(self):
        """
        Walk through directory and generate a list of result files
        """

        for direction in self.directions:
            for directory in self.dirs:
                file_list = []
                for filename in os.listdir(directory):
                    path = os.path.join(directory, filename)
                    if filename.endswith(direction):
                        file_list.append(path)

                getattr(self, direction)[directory] = file_list

    def parse_files(self):
        """
        Iterate over result files,
        parse received bits from files,
        """

        srec = "sum_received"
        bps = "bits_per_second"

        for direction in self.directions:
            hourly_average = {}         # todo naming?
            for directory, file_list in getattr(self, direction).items():
                directory = os.path.basename(os.path.normpath(directory))
                timestamp = datetime.strptime(directory, "%Y-%m-%d_%H-%M")
                file_count = len(file_list)
                received = 0

                for filename in file_list:
                    with open(filename) as infile:
                        data = infile.read()

                    try:
                        received += json.loads(data)["end"][srec][bps]
                    except json.JSONDecodeError:
                        file_count -= 1
                        print('No json data, got\n{d}'.format(d=data))

                if file_count:
                    hourly_average[timestamp] = (received / file_count)

            self.iperf_results[direction] = OrderedDict(sorted(
                hourly_average.items(), reverse=True))

            return self.iperf_results

    def plot(self, save=False, show=True):
        """
        Plot a line chart
        """

        self.__get_dirs__()
        self.__get_files__()
        self.parse_files()

        index = 0
        for direction, hourly_average in self.iperf_results.items():
            timestamps = []
            averages = []

            for tstamp, avg in hourly_average.items():
                timestamps.append(datetime.strftime(tstamp, '%Y-%m-%d_%H-%M'))
                avg = round(avg/(10**6), 2)  # bps to Mbps, round to 2 decimals
                averages.append(avg)

            self.axf[index].plot(timestamps, averages)
            self.axf[index].set_title('Average {d} over Time'.format(
                d=direction))
            self.axf[index].set_xlabel('Time [Timestamp]')
            self.axf[index].set_ylabel('{d} [Mbps]'.format(d=direction))
            index += 1

        if save:
            self.fig.savefig('fig.png', dpi=600)

        if show:
            plt.show()

        return self.fig

if __name__ == "__main__":
    PLOTTER = NetMeasureAnalyzer()
    PLOTTER.plot(True)
