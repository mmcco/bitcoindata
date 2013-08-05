'''blocks.py: Writes blocks from ./blocks.csv to ./data/newBlocks.csv.
In the process, it converts each block's timestamp from ISO 8601 to a Unix timestamp.
'''

from dateutil.parser import parse
import calendar
import datetime

# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
blockTimes = []  # location is blockID, value is Unix timestamp

with open("blocks.csv", "r") as blocks, open("data/newBlocks.csv", "w") as newBlocks:
    blocks.readline()  # skip first line, which is just column names
    for line in blocks:
        data = line.split(",", 4)
        if len(data) < 5:
            raise Exception("bad line in blocks.csv")
        if int(data[0]) != len(blockTimes):
            raise Exception("mismatch between blockID (" + data[0] + ") and blockTimes list length " + str(len(blockTimes)) + ")")

        timestamp = calendar.timegm(parse(data[3][1:-1]).utctimetuple())  # convert ISO 8601 timestamp to Unix timestamp
        blockTimes.append(str(timestamp))
        data[3] = str(timestamp)
        newBlocks.write(",".join(data))
