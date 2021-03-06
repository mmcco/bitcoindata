'''txs.py: Writes transactions from ./transactions.csv to ./data/txs.csv.
In the process, it inserts the transaction's blocktime.
It is assumed that blocks.py has already been run and that ./data/newBlocks.csv exists.
'''

from dataStructs import blockTimes, parseCSVLine
import os.path

if not os.path.isfile("data/newBlocks.csv"):
    raise RuntimeError("Error: must run blocks.py and have its output file (data/newBlocks.csv) before running this script")

# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
blocktimes = blockTimes()

with open("transactions.csv", "r") as txs, open("data/txs.csv", "w") as newTxs:
    txs.readline()  # skip first line, which is just column names
    for line in txs:
        data = parseCSVLine(line, 5)
        blockID = int(data[3])
        timestamp = blocktimes[blockID]
        data.insert(4, str(timestamp))
        newTxs.write(",".join(data))
