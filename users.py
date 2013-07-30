# This script generates a CSV file associating Bitcoin addresses based on the entity that is suspected to own them
# It uses the classic heuristic of assuming all addresses owning inputs to a transaction are owned by the same entity
# This is carried out using the union-find algorithm

# note that sets are used heavily - they're somewhat slower than lists but are more bug-resistant
# if you're looking to make performance improvements, convert sets to lists where possible

# temporary path extension to fix symlink bug
import sys
sys.path.append("/home/mike/bitcoindata")
from dataStructs import getAddresses, inputAddresses


# returns the given addresses's root and rank in a tuple
def getRoot(addr):
    if type(addresses[addr]) == int:
        return addr
    else:
        # three-step technique used for path compression
        root = getRoot(addresses[addr])
        addresses[addr] = root
        return root


def union(args):
    
    if len(args) < 2:
        raise Exception("union() passed a list of length < 2")

    roots = set(map (getRoot, args))

    # if the roots are already equal, we're done
    if len(roots) == 1:
        return

    rootTuple = [(root, addresses[root]) for root in roots]
    parent = max (rootTuple, key = (lambda x: x[1]))
    rootTuple.remove(parent)
    # make everyone child root point to the parent root
    for child in rootTuple:
        addresses[child[0]] = parent[0]
    
    # increment the root's rank if we're connecting a tree of equal rank
    for child in rootTuple:
        if child[1] == parent[1]:
            addresses[parent[0]] += 1
            break
        elif child[1] > parent[1]:
            raise Exception("parent selected did not have the highest rank")


# index is txID, value is a list of its inputs' addresses
# WARNING: the only duplicate check is in the function
txs = inputAddresses()
    
print "list of addresses associated by transaction filled"

addresses = dict() # associates address with user

# populate addresses dict, making an index of value 0 for each address
for address in getAddresses():
    addresses[address] = 0

print "dictionary of addresses for union-find filled"

for tx in txs:
    if len(tx) > 1:
        union(tx)

print "union-find completed"

usersDict = dict() # associates users' address sets with their roots

for key, value in addresses.iteritems():
    
    root = key
    while type(addresses[root]) != int:
        root = addresses[root]

    if not root in usersDict:
        usersDict[root] = set([key])

    else:
        usersDict[root].add(key)

print "dictionary of users indexed by root populated"

# write each user to a CSV file
with open("bitcoinData/users.csv", "w") as userFile, open("bitcoinData/usersCount.csv", "w") as countFile:

    users = []

    for counter, (key, user) in enumerate(usersDict.iteritems()):
        if len(user) == 0:
            raise Exception("trying to write a user with no addresses")
        countFile.write(str(counter) + "," + str(len(user)) + '\n')
        for address in user:
            userFile.write(address + "," + str(counter) + "\n")
