# this script calculates the percentage of coins that fit Ron & Shamir's definition of "old coins"
# specifically, old coins have not been spent in ninety days
# the script generates a CSV file showing the percentages
# the default interval is three days

# all coins are stored in unspent outputs; we can therefore calculate the time distribution of coins simply by going through outputs and collecting unspent outputs

from dataStructs import outputsList, txTimestamps

outputs = outputsList()
timestamps = txTimestamps()

# we generate the percentage of coins that are old every three days
# therefore, we start three days after the first transaction
cutoffTime = timestamps[0] + 259200
# coins generated before this time are considered old
# we will make it ninety days before the cutoff time
oldTime = cutoffTime - 7776000
lastTxID = 0

with open("bitcoinData/oldCoins.csv", "w") as oldCoinsFile:
    while cutoffTime <= timestamps[-1]:
        
        # find the last txID in this timeframe
        while cutoffTime >= timestamps[lastTxID]:
            lastTxID += 1

        for output in outputs:

            if txID > lastTxID:
                break

            # if the output has already been spent, ignore it and continue
            elif output[3] is not None and output[3] <= lastTxID:
                continue

            else:
                if timestamps[output[0]] < oldTime:
                    oldCoins += output[2]
                else:
                    freshCoins += output[2]

            percentOld = float(oldCoins) / (oldCoins + freshCoins)

            oldCoinsFile.write(str(cutoffTime) + "," + percentOld)

            oldCoins = freshCoins = 0
            cutoffTime += 259200
            oldTime += 259200
