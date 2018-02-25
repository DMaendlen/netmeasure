#!/usr/bin/python3

from collections import OrderedDict
from datetime import datetime

import json
import matplotlib.pyplot as plt
import os

"""
Parse iperf3 results from json files, calculate average per hour and plot the
result in a simple line graph
"""
class ResultParser(object):
    """
    Parse iperf3 results from json files, calculate average per hour
    """

    def __init__(self, working_dir="./results"):
        """
        Setup the parser
        """

        self.working_dir = working_dir
        self.result_dirs = []
        self.result_files = {}
        self.iperf_results = {}

    def get_result_dirs(self):
        """
        Walk through working_dir and generate a list of result dirs
        """

        for directory in os.listdir(self.working_dir):
            path = os.path.join(self.working_dir, directory)
            if os.path.isdir(path) and directory.startswith('2018'):
                self.result_dirs.append(path)

        return self.result_dirs

    def get_result_files(self):
        """
        Walk through directory and generate a list of result files
        """

        for directory in self.result_dirs:
            file_list = []
            for filename in os.listdir(directory):
                path = os.path.join(directory, filename)
                if filename.endswith('log'):
                    file_list.append(path)

            self.result_files[directory] = file_list

        return self.result_files

    def parse_result_files(self):
        """
        Iterate over result files,
        parse received bits from files,
        return dict timestamp:average
        """

        self.get_result_dirs()
        self.get_result_files()

        hourly_average = {} # todo naming?
        for directory, file_list in self.result_files.items():
            directory = os.path.basename(os.path.normpath(directory))
            timestamp = datetime.strptime(directory, "%Y-%m-%d_%H-%M")
            file_count = len(file_list)
            received = 0
            average = 0

            for filename in file_list:
                with open(filename) as infile:
                    data = infile.read()

                try:
                    received += json.loads(data)["end"]["sum_received"]["bits_per_second"]
                except json.JSONDecodeError:
                    file_count -= 1
                    print('No json data, got\n{d}'.format(d=data))

            average = (received / file_count)

            hourly_average[timestamp] = average

        return hourly_average

class Plotter(object):
    """
    Plot averaged iperf3 results over time
    """

    def __init__(self, hourly_average):
        """
        Import data in form of {'<timestamp>': average}
        """

        # sort hourly_average by timestamp
        keys = []
        for k in hourly_average.keys():
            keys.append(k)
        sorted_keys = sorted(keys)
        sorted_hourly_average = [(key, hourly_average[key]) for key in sorted_keys]
        self.hourly_average = OrderedDict(sorted_hourly_average)


    def plot(self):
        """
        Generate line chart of average over time
        """

        timestamps = []
        averages = []

        for ts, avg in self.hourly_average.items():
            timestamps.append(datetime.strftime(ts, '%Y-%m-%d_%H-%M'))
            avg = round(avg/1048576, 2) # convert bps to Mbps, round to 2 decimals
            averages.append(avg)

        plt.plot(timestamps, averages)
        plt.title('Average Throughput (download) over Time')
        plt.xlabel('Time')
        plt.ylabel('Average Throughput (download)')
        plt.show()

if __name__ == "__main__":
    parser = ResultParser()
    plotter = Plotter(parser.parse_result_files())
    plotter.plot()
