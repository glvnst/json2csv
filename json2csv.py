#!/usr/bin/env python
"""
json2csv: Convert a json file into a csv file
"""
import argparse
import sys
import json
import csv
import codecs
import cStringIO
import os
import collections


class UnicodeWriter(object):
    """
    A CSV writer which will write rows to output filehandle "stream",
    which is encoded in the given encoding.
    Mostly from https://docs.python.org/2/library/csv.html
    """

    def __init__(self, stream, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = stream
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, raw_row_values):
        """ Write a row to the output file (with hackery for unicode) """
        safe_row_values = list()
        for value in raw_row_values:
            try:
                if isinstance(value, unicode):
                    safe_row_values.append(value.encode("utf-8"))
                    continue
                safe_row_values.append(value)
            except UnicodeDecodeError:
                print "{}:{}".format(type(value).__name__, value)
                raise
        self.writer.writerow(safe_row_values)
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
        """ Calls writerow on a collection of rows """
        for row in rows:
            self.writerow(row)


def not_none(input_value, replacement_value=""):
    """ If the given input value is None, replace it with something else """
    if input_value is None:
        return replacement_value
    return input_value


def json_to_table(json_filename):
    """
    Convert a list of dicts into a table (list of lists of values). Return the
    headings in the result row
    """
    with open(json_filename, "r") as json_fh:
        records = json.load(json_fh, encoding="utf-8",
                            object_pairs_hook=collections.OrderedDict)
    headings = tuple(records[0].keys())

    return [headings] + [[not_none(record[heading]) for heading in headings]
                         for record in records]


def safe_open(path, read=True, write=False, allow_create=True,
              allow_overwrite=False, file_permissions=0755):
    """ Uses os.open to avoid clobbering files that already exist """
    flags = 0
    mode = 'r'

    if read and write:
        flags |= os.O_RDWR
        mode = 'r+'
    elif read:
        flags |= os.O_RDONLY
        mode = 'r'
    elif write:
        flags |= os.O_WRONLY
        mode = 'r+'
        # This hurts me.
        # 'w' and 'w+' truncate
        # 'a' and 'a+' ONLY append (without regard to seek) on some platforms
    else:
        raise RuntimeError("a file must be opened for reading or writing")

    if allow_create:
        flags |= os.O_CREAT
    if not allow_overwrite:
        if not allow_create:
            raise RuntimeError("safe_open must create or overwrite")
        flags |= os.O_CREAT | os.O_EXCL

    try:
        return os.fdopen(os.open(path, flags, file_permissions), mode)
    except OSError, error:
        print error
        sys.exit(1)


def make_output_filename(input_name, new_extension):
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
        "Create a CVS file from a JSON file. The input files must contain an "
        "array of objects with uniform keys. Output will be written to the "
        "current working directory. For example for the input file "
        "'/something/thing.json' we create './thing.csv'. By default "
        "existing files will not be overwritten."))
    argp.add_argument('inputfile', nargs="+", help=(
        "Input JSON file(s) "))
    argp.add_argument('-w', '--overwrite', action="store_true", help=(
        "Overwrite the output file(s) if they exist"))
    argp.add_argument('-d', '--debug', action="store_true", help=(
        "Print debugging output instead of generating CSV files"))
    args = argp.parse_args()

    # do things
    if args.debug:
        import pprint
        dump = pprint.PrettyPrinter(indent=4).pprint

    for input_filename in args.inputfile:
        table = json_to_table(input_filename)
        if args.debug:
            dump(table)
            continue

        output_filename = make_output_filename(input_filename, '.csv')

        with safe_open(output_filename, write=True,
                       allow_overwrite=args.overwrite) as output:
            writer = UnicodeWriter(output, quoting=csv.QUOTE_MINIMAL)
            writer.writerows(table)
        print "Wrote {} records to {}".format(len(table), output_filename)

    return True


if __name__ == '__main__':
    EXIT_STATUS = main()
    sys.exit(int(not EXIT_STATUS if isinstance(EXIT_STATUS, bool)
                 else EXIT_STATUS))
