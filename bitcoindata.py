#!/usr/bin/env python

# this script simply executes all of the component scripts in one go
import os

if __name__ == "__main__":
    if not os.path.exists("bitcoinData"):
        os.makedirs("bitcoinData")

    execfile("btc.py")
    execfile("users.py")
    execfile("heurusers.py")
    execfile("networkXGraph.py")
