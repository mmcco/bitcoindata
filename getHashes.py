### !!! This script is deprecated, as its functionality is included in btc.py !!! ###

from sys import argv
# takes the following arguments in order:
txs = open(argv[1], "r")
inputs = open(argv[2], "r")
outputs = open(argv[3], "r")
newinputs = open(argv[4], "w")
newoutputs = open(argv[5], "w")
# and fills a new field, txHash, in inputs and outputs

txsList = []
for line in txs:
    data = line.split(",", 2)
    if len(txsList) != int(data[0]):
        raise Exception("txIDs and txsList do not match - len(txsList) is " + str(len(txsList)) + " while the txID is " + data[0])
    txsList.append(data[1])

for line in inputs:
    data = line.split(",", 1)
    newinputs.write(data[0] + "," + txsList[int(data[0])] + "," + data[1])

for line in outputs:
    data = line.split(",", 1)
    newoutputs.write(data[0] + "," + txsList[int(data[0])] + "," + data[1])

txs.close()
inputs.close()
outputs.close()
newinputs.close()
newoutputs.close()
