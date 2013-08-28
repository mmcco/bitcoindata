'''blocks.py: Writes blocks from ./blocks.csv to ./data/newBlocks.csv.
In the process, it converts each block's timestamp from ISO 8601 to a Unix timestamp.
'''

from dataStructs import parseCSVLine
from dateutil.parser import parse
import calendar
import datetime

with open("blocks.csv", "r") as blocks, open("data/newBlocks.csv", "w") as newBlocks:
    blocks.readline()  # skip first line, which is just column names
    for line in blocks:
        data = parseCSVLine(5)
        timestamp = calendar.timegm(parse(data[3][1:-1]).utctimetuple())  # convert ISO 8601 timestamp to Unix timestamp
        data[3] = str(timestamp)
        newBlocks.write(",".join(data))
