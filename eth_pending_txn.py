import sys
import requests
import time
from datetime import datetime
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()
ethScanApiKey = os.getenv("ETH_SCAN_API_KEY")
ethExplorerApiKey = os.getenv("ETH_EXPLORER_API_KEY")
ethCryptoapisApiKey = os.getenv("ETH_CRYPTOAPIS_API_KEY")

connection = pymysql.connect(
    host="localhost", user="root", passwd="", database="eth_transaction")
cursor = connection.cursor()


pendingTransactionsUrl = 'https://api.cryptoapis.io/v1/bc/eth/mainnet/txs/pending?limit=1000'
headers = {'x-api-key': ethCryptoapisApiKey}


response = requests.get(pendingTransactionsUrl, headers=headers)
if response.status_code != 200:
    # This means something went wrong.
    print("Error! ")
    print(response)


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


counter = 1

while True:
    print()
    print("calling api...")
    print(counter)
    pendingTransactionsResponse = requests.get(
        pendingTransactionsUrl, headers=headers).json()
    if 'payload' in pendingTransactionsResponse:
        for payloadItem in pendingTransactionsResponse['payload']:
            payloadItem.update(timestart=round(time.time()))
            insertVal = ""
            for key in payloadItem:
                val = payloadItem[key]
                if is_number(str(val)) == False:
                    insertVal = insertVal + "'" + str(val) + "'" + ", "
                else:
                    insertVal = insertVal + str(val) + ", "
            insertVal = insertVal[:-2]

            SQL_insert = 'INSERT INTO eth_pending_txn (txnHash, nonce, blockHash, blockNumber, txnIndex, sentFrom, sentTo, value, fee, gasPrice, gasLimit, input, timestart) VALUES(%s);' % insertVal
            # print(SQL_insert)
            try:
                cursor.execute(SQL_insert)
                connection.commit()
                print('Data inserted')
            except Exception as error:
                print("we have an error")
                print("Error name: ")
                print(error)
                print(insertVal)
                print(insertVal.count(","))

    time.sleep(60)
    counter = counter + 1


'''def addNewlyFoundPendingTransactions(pendingTransactionsResponse):
  for payloadItem in pendingTransactionsResponse['payload']:
    if payloadItem['hash'] not in hashIdDict:
        payloadItem.update(timestart = datetime.now().timestamp())
        txHash = payloadItem['hash']
        hashIdDict.update({txHash : payloadItem})'''
