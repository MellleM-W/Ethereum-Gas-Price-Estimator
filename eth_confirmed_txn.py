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


def hexToGwei(hxStr):
    return int(hxStr, 16)/10**9


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


txnHashList = []
updateCol = [
    'timeConfirmed',
    'blockNumCfm',
    'success',
    'txnVal',
    'gasLimitCfm',
    'gasUsedCfm',
    'gasPriceCfm',
    'txnFee'
]


# while True:

SQL_select = 'SELECT txnHash FROM eth_pending_txn WHERE success = 0;'
cursor.execute(SQL_select)
# print('selected')

for row in cursor:
    # print(row)
    txnHashList.append(row[0])
# print('hash')
# print(txnHashList)
counter = 0
for txnHash in txnHashList:
    counter = counter + 1
    progress = str(round(counter * 100 / len(txnHashList), 2)) + '%'
    print()
    print('start checking...')
    print('Hash#', counter)
    print(txnHash)
    print(progress)
    time.sleep(3)
    txnEthplorerurl = "https://api.ethplorer.io/getTxInfo/" + \
        txnHash + "?apiKey=" + ethExplorerApiKey
    #print(txnEthplorerurl)
    txnEthplorerurlResponse = requests.get(txnEthplorerurl).json()

    if 'success' in txnEthplorerurlResponse and txnEthplorerurlResponse['success'] == True:
        getVal = [
            txnEthplorerurlResponse['timestamp'],
            txnEthplorerurlResponse['blockNumber'],
            txnEthplorerurlResponse['success'],
            txnEthplorerurlResponse['value'],
            txnEthplorerurlResponse['gasLimit'],
            txnEthplorerurlResponse['gasUsed']
        ]

        txnEthscanurl = "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash=" + \
            txnHash + "&apikey=" + ethScanApiKey
        # print(txnEthscanurl)
        txnEthscanurlResponse = requests.get(txnEthscanurl).json()
        if txnEthscanurlResponse['result']['gasPrice'] is not None:
            gasPriceGwei = hexToGwei(
                txnEthscanurlResponse['result']['gasPrice'])
            txnFeeVal = gasPriceGwei * \
                txnEthplorerurlResponse['gasUsed'] / 10**9
            getVal.extend([gasPriceGwei, txnFeeVal])

            # print('getVal')
            # print(getVal)

            setClause = ""
            for i in range(len(updateCol)):
                if is_number(str(getVal[i])) == True or str(getVal[i]) == 'True':
                    setClause = setClause + \
                        updateCol[i] + ' = ' + str(getVal[i]) + ', '
                else:
                    setClause = setClause + \
                        updateCol[i] + ' = ' + "'" + \
                        str(getVal[i]) + "'" + ', '
            setClause = setClause + 'txnTime = timeConfirmed - timestart'

            SQL_updateTxn = 'UPDATE eth_pending_txn SET ' + setClause + \
                ' WHERE txnHash = ' + "'" + txnHash + "'" + ';'
            # print('SQL')
            # print(txnHash)
            # print(SQL_updateTxn)
            # print('next')

            try:
                cursor.execute(SQL_updateTxn)
                connection.commit()
                print('updated')

            except Exception as error:
                print("Error occurs when UPDATE")
                print("Error name: ")
                print(error)
                print(getVal)

    elif 'success' not in txnEthplorerurlResponse or txnEthplorerurlResponse['success'] == False:
        SQL_markTxn = 'UPDATE eth_pending_txn SET success = 2 WHERE txnHash = ' + \
            "'" + txnHash + "'" + ';'
        try:
            cursor.execute(SQL_markTxn)
            connection.commit()
            print('failed txn marked')
            print()
        except Exception as error:
            print("Error occurs when UPDATE failed txn")
            print("Error name: ")
            print(error)
            print()
    else:
        1

    # time.sleep(3600)
