import csv  
import json 
import argparse
import os.path
import logging
import re

# prepare logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(__name__+'.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# Start of execution
logger.info(__name__ + ' execution beginned.')

# argument parsing
parser = argparse.ArgumentParser(description='Convert csv file(s) to json file(s).')
parser.add_argument('filenames', nargs='*', type=str, help='File name', metavar='filename')
args = parser.parse_args()

# if argument(s) is not provided, get input from user
filenames = args.filenames;
if not filenames:
    filenames = input('Please list file names separated by space:').split()
    logger.info('File(s) provided manually on command line: %s', filenames)
else:
    logger.info('File(s) provided as argument(s) to main: %s', filenames)

# set variable for unique id in json
idSet = set()

# iterate csv files for conversions
jsonObjList = []; 
for filename in filenames:
    if not os.path.exists(filename): # if file does not exist, log error and skip this file
        logger.error('\'%s\' does not exist!', filename)
        input('Error(s) occurs. Please see the log file to debug. Enter to exit.')
        #sys.exit(0)
    else:        
        # Open input csv file to read and convert data
        with open(filename, 'rU') as csvFile:
            # for the case that the extension of csv file is not 'csv'
            if filename[-3:] != 'csv': 
                logger.warning('The file \'%s\' is not a csv file.', filename)

            # determine index of four columns
            fieldnames = ["id", "first_name", "last_name", "email"]            
            fieldColumns = [];
            has_header = csv.Sniffer().has_header(csvFile.read(1024))
            csvFile.seek(0)
            if has_header: # if the header row exists, find correct indices for four columns
                firstRow = next(csvFile).strip().split(',')
                for fieldname in fieldnames:
                    index = firstRow.index(fieldname)
                    fieldColumns.append(index)
            else: # if header row does not exist, assume the first four columns in the order of fieldnames
                fieldColumns = [0, 1, 2, 3]

            #regex for validating each cell
            regex = [".", "^[a-zA-Z]+$", "^[a-zA-Z]+$", r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"]
                                          
            # construct jsonObjList from rows
            for row in csv.reader(csvFile):     
                jsonObj = {}
                bContinue = False
                # iterate for 4 key/value pairs
                for i in range(0, len(fieldnames)):
                    # add key : value
                    key = fieldnames[i]
                    value = row[fieldColumns[i]]
                    if key == "id":
                        tmpSet = set()
                        tmpSet.add(value)
                        # if already included, skip this object
                        if tmpSet & idSet: 
                            bContinue = True
                            break
                        idSet.add(value)                      
                    jsonObj[key] = value
                    # validate paired key : value 
                    if not re.match(regex[i], value):
                        logger.debug("%s : %s is not matched in %s", key, value, row)
                #append json object to list
                if bContinue : continue
                jsonObjList.append(jsonObj)


# open json file to write json output
with open('result.json', 'w') as jsonFile: 
    jsonFile.writelines(json.dumps(jsonObjList))              

# End of execution
logger.info(__name__ + ' execution ended.')