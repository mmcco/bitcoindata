# this section selects the Unix timestamp of each tx's corresponding block and inserts it into the tx
# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
blocktimes = blockTimes()

with open("transactions.csv", "r") as txs, open("bitcoinData/txs.csv", "w") as newTxs:
    txs.readline()  # skip first line, which is just column names
    for line in txs:
        data = parseCSVLine(line, 5)
        blockID = int(data[3])
        timestamp = blocktimes[blockID]
        data.insert(4, timestamp)
        newTxs.write(",".join(data))
