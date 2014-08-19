"""
DB Benchmarking Application
===========================

Main.py

This file houses the core of the application, and is where all of the read/write
commands are issued from, timed, and all data is analyzed.  Results from the
trials are printed to the console by default, but can optionally be printed to a
file to keep a record of.  This is particularly helpful when benchmarking
multiple DB's in a row to see which one is best for deployment purposes.

"""

# TODO(kmjungersen) - create terminal line arguments that enable certain options
# such as the number of trials, file report, etc.

import sys
import time
import string
import random

from tabulate import tabulate

from numpy import array, average

from mongodb.mongo_db import BenchmarkMongo
from riakdb.riak_db import BenchmarkRiak


class Benchmark():

    def __init__(self, db):
        """ The init method is passed a single parameter upon initialization in
        order to define which database should be benchmarked.  Other important
        values are defined here, such as the entry length and the number of
        trials to execute.

        :param db: The desired db to be benchmarked
        """

        self.entry_length = 10
        self.number_of_trials = 100
        self.number_of_nodes = 4

        self.write_times = []
        self.read_times = []

        self.collection = 'test'
        self.sorting_index = 'ID'
        self.reports_dir = 'generated_reports/'

        self.time_and_date = time.strftime("%a, %d %b, %Y %H:%M:%S")

        #TODO - do this better.  This sucks, but works for now.
        self.db_name = db.upper()

        registered_dbs = {
            'riak': BenchmarkRiak(),
            'mongo': BenchmarkMongo(),
        }

        self.database = registered_dbs.get(db)

        # A simple check to see if the desired database is registered
        if self.database:

            self.database.setup(self.collection)

        else:

            print 'Not a valid db!'

    def random_entry(self, entry_type='string'):
        """ This function generates a random string or random number depending on
        the arguments passed in.  The string is generated from all ascii letters
        and the number is generated from numbers 0-9.

        :param entry_type: the specified type of random entry, either 'string'
                    or 'number'

        :return: the random string or number that was just generated
        """

        entry = ''

        if entry_type == 'string':

            selection = string.ascii_letters

        else:

            selection = string.digits

        for x in range(self.entry_length):

            entry += random.choice(selection)

        return entry

    def run(self):
        """ This function will keep track of and call the read/ write functions
        for benchmarking.  For each iteration, a new DB entry will be created,
        written to the DB,  and then read back from it.

        """

        for index in range(self.number_of_trials):

            item_number = self.random_entry(entry_type='number')
            info = self.random_entry(entry_type='string')

            entry = {
                'Index': index,
                'Number': item_number,
                'Info': info
            }

            if not self.writes(entry):
                print 'WRITE ERROR'

            if not self.reads(index):
                print 'WRITE ERROR'

        self.compile_data()

    def writes(self, entry):
        """ This function handles all DB write commands, and times that action
        as well.  It takes a single parameter ('entry'), which is the data to be
        written to the DB.

        :param entry: The entry to be recorded to the DB

        :return: True, if all operations successfully completed
        """

        write_start_time = time.time()

        self.database.write(entry)

        write_stop_time = time.time()

        write_time = write_stop_time - write_start_time

        self.write_times.append(write_time)

        return True

    def reads(self, index):
        """ This function handles all DB read commands, and times that action as
        well.  It takes a single parameter, which is the index of an entry to
        retrieve from the DB.

        :param index: The index of the item to be retrieved from the DB

        :return: True, if all operations successfully completed
        """

        read_start_time = time.time()

        self.database.read(index)

        read_stop_time = time.time()

        read_time = read_stop_time - read_start_time

        self.read_times.append(read_time)

        return True

    def compile_data(self, return_results=False):
        """ This function takes all the data collected from the trials (read and
        write times) and then calculates some important statistics about said
        data.  Without altering functionality, a report will be generated upon
        completion of analysis.

        :param return_results=False: This parameter can be optionally passed as
                    True if the user wants to have the dict of results returned
                    instead of generating a report with said results

        :return results: The compiled results from the statistical analysis of
                    the trial data as a dict
        """

        self.write_times = array(self.write_times)
        self.read_times = array(self.read_times)

        # self.write_times = 234
        # self.read_times = 34565

        write_avg = average(self.write_times)
        write_stdev = 0
        write_max = 0
        write_min = 0

        read_avg = average(self.read_times)
        read_stdev = 0
        read_max = 0
        read_min = 0

        if return_results:

            results = {
                'database': self.db_name,
                'trial_number': self.number_of_trials,
                'entry_length': self.entry_length,
                'node_number': self.number_of_nodes,
                'write_avg': write_avg,
                'write_stdev': write_stdev,
                'write_max': write_max,
                'write_min': write_min,
                'read_avg': read_avg,
                'read_stdev': read_stdev,
                'read_max': read_max,
                'read_min': read_min,
            }

            return results

        else:

            param_header = [
                'Parameter',
                'Value',
            ]

            param_values = [
                ['Database Tested', self.db_name],
                ['Number of Trials', str(self.number_of_trials)],
                ['Length of Each Entry Field', str(self.entry_length)],
                ['Number of Nodes in Cluster', str(self.number_of_nodes)],
            ]

            data_header = [
                'Operation',
                'Average',
                'St. Dev.',
                'Max Time',
                'Min Time',
            ]

            data_values = [
                ['Writes', write_avg, write_stdev, write_max, write_min],
                ['Reads', read_avg, read_stdev, read_max, read_min],
            ]

            param_table = tabulate(
                tabular_data=param_values,
                headers=param_header,
                tablefmt='pipe',
            )

            data_table = tabulate(
                tabular_data=data_values,
                headers=data_header,
                tablefmt='pipe',
            )

            report_info = {
                'database': self.db_name,
                'time_and_date': self.time_and_date,
                'param_table': param_table,
                'data_table': data_table,
            }

            self.generate_report(report_info)

    def generate_report(self, final_report):

        report_name = '{parent_dir}/{db}.report.md'.format(
            parent_dir=self.reports_dir,
            db=self.db_name
        )

        with open('report_template2.md', 'r') as infile, \
                open(report_name, 'w+') as outfile:

            template = infile.read()

            report = template.format(**final_report)

            print report

            outfile.write(report)


if __name__ == '__main__':

    chosen_database = sys.argv[1]

    foo = Benchmark(db=chosen_database)

    foo.run()