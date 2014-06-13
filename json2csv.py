#!/usr/bin/env python
"""
json2csv: Convert a json table into a csv file
"""
import argparse
import sys
import json
import csv
import codecs
import cStringIO
import os
import collections

#import support_modules

def not_none(input_value, none_replacement=""):
    """ If the given input value is None, replace it with something better """
    if input_value is None:
        return none_replacement
    return input_value


def json_to_table(json_filename):
    """
    Convert a list of dicts in to a table (list of lists of values). Return 
    the headings in the result row
    """
    with codecs.open(json_filename, "r", "utf-8") as json_fh:
        records = json.load(json_fh, encoding="utf-8",
                            object_pairs_hook=collections.OrderedDict)
    headings = records[0].keys()

    return [headings] + [[not_none(record[heading]) for heading in headings]
                         for record in records]


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, raw_row):
        row_values = list()
        for value in raw_row:
            try:
                if isinstance(value, unicode):
                    row_values.append(value.encode("utf-8"))
                    continue
                row_values.append(value)
            except UnicodeDecodeError:
                print "{}:{}".format(type(value).__name__, value)
                raise
        self.writer.writerow(row_values)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def make_output_name(input_name, new_extension):
    """
    Return an output filename based on an input filename; using basename and
    splitext
    """
    return os.path.splitext(os.path.basename(input_name))[0] + new_extension


def main():
    """
    primary function for command-line execution. return an exit status integer
    or a bool type (where True indicates successful exection)
    """
    argp = argparse.ArgumentParser(description=(
        "Convert a json table into a csv file"))
    argp.add_argument('inputfiles', nargs="+", help=(
        "{{Description of input files}}"))
    argp.add_argument('-d', '--debug', action="store_true", help=(
        "enable debugging output"))
    args = argp.parse_args()

    # do things
    if args.debug:
        import pprint
        dump = pprint.PrettyPrinter(indent=4).pprint

    for input_name in args.inputfiles:
        table = json_to_table(input_name)
        if args.debug:
            dump(table)
            continue

        output_name = make_output_name(input_name, '.csv')
        with open(output_name, "wb") as output:
            writer = UnicodeWriter(output, quoting=csv.QUOTE_MINIMAL)
            writer.writerows(table)
        print "Wrote {} records to {}".format(len(table), output_name)

    return True


if __name__ == '__main__':
    EXIT_STATUS = main()
    sys.exit(int(not EXIT_STATUS if isinstance(EXIT_STATUS, bool)
                 else EXIT_STATUS))
