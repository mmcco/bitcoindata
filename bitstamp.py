# this script recursively downloads transaction history from Bitstamp (a Bitcoin exchange) and stores the data in a database
# it assumes you already have a MySQL database named "btc"

import urllib2
import json
import MySQLdb
import time

dbConnection = MySQLdb.connect(host = "localhost",
                               user = "root",
                               passwd = "******",
                               db = "btc")

dbConnection.autocommit(True)
cursor = dbConnection.cursor()

cursor.execute("create table if not exists bitstamp (tid INT, timestamp INT, price DOUBLE, amount DOUBLE, PRIMARY KEY (tid));")
# get the number of transactions we already have
cursor.execute("select count(*) from bitstamp;")
# offset is the number of transactions skipped by the JSON call
offset = cursor.fetchone()[0]

while True:

    url = "https://www.bitstamp.net/api/transactions/?sort=asc;limit=5000;offset=" + str(offset)
    response = urllib2.urlopen(url)
    jsonData = json.load(response)

    if len(jsonData) > 5000:
        raise Exception("only 5,000 trades were requested but more were parsed")

    # convert list of dicts to list of lists for insert statement
    jsonValues = []
    for item in jsonData:
        jsonValues.append([unicode(value).encode("utf-8") for value in item.itervalues()])

    for value in jsonValues:
        if len(value) != 4:
            print value
            raise Exception("bad item in jsonValues  -==-  length is " + str(len(value)))

    cursor.executemany("insert into bitstamp (timestamp, tid, price, amount) values (%s, %s, %s, %s);", jsonValues)

    offset += len(jsonData)

    # sleep for longer if we have everything
    if len(jsonData) != 0:
        time.sleep(200)
    else:
        print "scraped all transactions, entering extended sleep"
        time.sleep(3000)


cursor.close()
dbConnection.close()
