from sys import argv
from dateutil.parser import parse
import calendar
import datetime

if len(argv) != 3:
    raise Exception("blocktime.py takes two arguments: the input and output files; " + str(len(argv) - 1) + " were given")

blocks = open(argv[1], "r")
newblocks = open(argv[2], "w")

for line in blocks:
    data = line.split(",", 4)
    if len(data) < 5:
        print len(data)
        print line
        raise Exception("bad line in input file")
    timestamp = calendar.timegm(parse(data[3][1:][:-1]).utctimetuple())
    newblocks.write(",".join([data[0], data[1], data[2], str(timestamp), data[4]]))

blocks.close()
newblocks.close()
