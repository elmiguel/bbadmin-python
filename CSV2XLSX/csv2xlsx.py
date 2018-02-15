"""csv2xlsx convertor

Usage:
    csv2xlsx FILE ... [options]
    csv2xlsx -h | --help
    csv2xlsx --version

Inputs:
    FILE ...        File(s) to be converted.

Options:
    -h, --help      Show this screen.
    --version       Show version.
    -s <separator>, --separator <separator> Override the default separator. [default: |]
    -q <qualifier>, --qualifier <qualifier> Override the default text qualifier (quotes).
                                            If using the back tick, use -q "\`". [default: "]
    -o <outdir>, --outdir <outdir>          Override the output directory. [default: .]
    -f <filename>..., --filename <filename>...    Override the incoming filename. Extension is not needed.
    -O <obfuscated_data>, --obfuscate <obfuscated_data> Import a obfuscated_data model.
        Should be a JSON file that contains field_name: [list, of, data to replace]
"""

from openpyxl import Workbook
from datetime import datetime
from docopt import docopt
from os import path
import csv
import json
import random
import sys

# setup a placeholder for generated name mappings
generated_names = {}

# setup obfuscate_options if supplied
obfuscate_options = None


def obfuscate_field(record, map_field, map_values):
    global generated_names
    global obfuscate_options
    # print("generated_names:",  generated_names)
    # print("obfuscate_options:", obfuscate_options)
    # print(record, map_field, map_values)
    obj = {
        record[map_field]: {}
    }

    for map_value in map_values:
        obj[record[map_field]].update({map_value: random.choice(obfuscate_options[map_value])})
    generated_names.update(obj)
    return obj


def process(args):
    global obfuscate_options
    global generated_names
    if args['--obfuscate']:
        with open(args['--obfuscate']) as options:
            obfuscate_options = json.loads(options.read())
        # print(obfuscate_options)
    # print(args)
    # sys.exit(1)
    for i, FILE in enumerate(args['FILE']):
        with open(FILE) as f:

            print('Configuring the output directory...')
            if args['--outdir'] != '.':
                output_path = args['--outdir']
            else:
                output_path = FILE.replace(path.basename(FILE), '')
            print(output_path)

            print('Configuring the filename...')
            if args['--filename']:
                output_file = args['--filename'].split(',')[i]
            else:
                output_file = path.basename(FILE)[:4]
            print(output_file)

            records = csv.DictReader(
                f, delimiter=args['--separator'], quotechar=args['--qualifier'], skipinitialspace=True)
            headers = records.fieldnames

            # create a Workbook
            wb = Workbook()
            ws = wb.active
            # if exclude_fields, then remove them
            if obfuscate_options['config'][output_file]['exclude_fields']:
                headers = [header for header in headers if header not in obfuscate_options[
                    'config'][output_file]['exclude_fields']]
            ws.append(headers)
            # print(headers)
            # debug
            # line = 0
            for record in records:
                # if obfuscate_options, then manipulate data
                if obfuscate_options:
                    for map_field, map_values in obfuscate_options['config'][output_file]['map_fields'].items():
                        # print(map_field, map_values)
                        if record[map_field] not in generated_names:
                            generated_name = obfuscate_field(record, map_field, map_values)
                        else:
                            generated_name = {record[map_field]: generated_names[record[map_field]]}

                        # print(generated_name)
                    record.update(generated_name[record[map_field]])
                # if we need to remove some fields then do so
                if obfuscate_options['config'][output_file]['exclude_fields']:
                    record = {k: v for k, v in record.items() if k not in obfuscate_options[
                        'config'][output_file]['exclude_fields']}
                    # record = ObfuscatedRecord(**record)
                # print(record)

                # if there are any reference_fields, then pull that data from generated_name
                try:

                    if obfuscate_options['config'][output_file]['reference_fields']:
                        # we need to iterate over the reference_fields, and pull each mapping
                        # once that is complete join the
                        for reference_field in obfuscate_options['config'][output_file]['reference_fields']:
                            # print(reference_field)
                            # reference_field dict
                            result = reference_field["result"]
                            _result = tuple([generated_names[record[reference_field['field']]][com]
                                             for com in reference_field['computed']])
                            # for com in reference_field['computed']:
                            #     print(record)
                            #     print(generated_names)
                            # print(generated_names[record[reference_field]][com])
                            # print(_result)
                            record.update(
                                {reference_field['field']: result % _result})
                            # print(record)
                except KeyError:
                    pass

                # reset the record back to a list based off the headers
                record = [record[field] for field in headers]
                if record != '':
                    ws.append(record)

                # debug
                # line += 1
                # if line >= 5:
                #     break

            print('Saving the excel file to:', path.join(output_path, output_file + '.xlsx'))
            wb.save(path.join(output_path, output_file + '.xlsx'))

    print("Job Complete!!")


if __name__ == '__main__':
    args = docopt(__doc__, version='csv2xlsx 1.0')
    process(args)
