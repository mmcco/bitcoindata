#!/usr/bin/env python

# this script simply executes all of the main component scripts in one go

import os

if __name__ == "__main__":

    if not os.path.exists("bitcoinData"):
        os.makedirs("bitcoinData")

    execfile("blocks.py")
    execfile("txs.py")
    execfile("inputs.py")
    execfile("outputs.py")

    execfile("users.py")
    execfile("heurusers.py")
#    execfile("networkXGraph.py")
