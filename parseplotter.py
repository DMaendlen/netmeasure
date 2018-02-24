#!/usr/bin/python3

import datetime
import json
import os
import time

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
            if os.path.isdir(directory) and directory.startswith('2018'):
                self.result_dirs.append(directory)

    def get_result_files(self):
        """
        Walk through directory and generate a list of result files
        """

        file_list = []
        for directory in self.result_dirs:
            for filename in os.listdir(directory):
                if filename.endswith('log'):
                    file_list.append(filename)

            self.result_files[directory] = file_list

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
            timestamp = time.mktime(datetime.datetime.strptime(directory, "%Y-%m-%d_%H-%M").timetuple())
            file_count = len(file_list)
            received = 0
            average = 0

            for filename in file_list:
                with open(os.path.join(directory, filename)) as infile:
                    data = infile.read()
        
                received += json.loads(data)["end"]["sum_received"]["bits_per_second"]

            average = (received / file_count)

            hourly_average[timestamp] = average

        return hourly_average
