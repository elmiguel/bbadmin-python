# Simple CLI to convert CSV files to Excel using Python while Obfuscating data
---

This small CLI just takes in CSV files and based off some configuration settings, obfucate data fields and creates xlsx files.

## Requirements

- Python 3.5 or higher
- openpyxl for creating Excel Documents
- docopt for creating the CLI help screen and CLI base object
```
pip install openpyxl docopt
```


Usage:
```
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
```

Example:
```
$ clear; python csv2xlsx-func.py ./CSVOutput/GradebookData.csv ./CSVOutput/ActivityAccumulator.csv  -s"~" -q"\`" -o ./ExcelOutput/ -f GradebookDataConverted,ActivityAccumulatorConverted -O ./obfuscate_data.json


Configuring the output directory...
./ExcelOutput/
Configuring the filename...
GradebookData
Saving the excel file to: ./ExcelOutput/GradebookDataConverted.xlsx
Configuring the output directory...
./ExcelOutput/
Configuring the filename...
ActivityAccumulator
Saving the excel file to: ./ExcelOutput/ActivityAccumulatorConverted.xlsx
Job Complete!!

```

After running that command (of course modify the file names to suit your needs), there will be the two CSV files converted to xlsx files in the ExcelOutput directory. Based off the configuration in the obfuscate_data.json file, the USER_ID, FIRSTNAME, and LASTNAME fields should be masked using generated data located in the same configuration file!

# TODO:
---
- [ ] Add support for connecting to a Database: SQLAlchemy
- [ ] Add local storage: Mongo DB.
- [ ] Add a more flexible configuration spec: Suggestions Welcome!
