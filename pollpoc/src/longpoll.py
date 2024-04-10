import requests
import json

from datetime import datetime
import time


def getCostData():
    url = "https://production.api.coindesk.com/v2/tb/price/ticker?assets=BTC"
    # "https://jsonplaceholder.typicode.com/todos/1"
    # "https://www.coingecko.com/coins/price_percentage_change?ids=26377,33895,30815,691,34563,34366,1,279,325,825,4128,44,6319,13442,975,12559,5,1094,877,12171,4713,7598,17980,14495,12504,11939,780,2,9956,17233,28452,1481,8418,25751,453,2069,10365,26455,25244,12882,100,12817,1167,4463,31967,3688,31079,13573,16547,30980,7310,28205,69,11636,13397,26375,1364,20764,6595,3370,4380,12335,32417,6799,30162,15628,11610,13446,12645,33345,32594,4284,4984,3449,3406,2538,4001,28624,12129,13029,30666,34182,22457,28453,16724,8834,28573,27045,1047,24383,976,17500,22617,31924,12493,878,480,20009,738,13079,28284,5681,692,13162,9761,4343&vs_currency=usd"

    headers = {"accept": "application/json, text/plain, */*"}

    response = requests.get(url, headers=headers)

    responseData = response.json()

    # print(responseData)

    # print(responseData["data"]["BTC"]["ohlc"]["c"])
    variationPercent = responseData["data"]["BTC"]["change"]["percent"]
    currentCost = responseData["data"]["BTC"]["ohlc"]["c"]
    # print(variationPercent)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    # df = pd.DataFrame([[1, 2], [3, 4]], columns=["a", "b"])
    costData = [current_time, currentCost, variationPercent]
    return costData


def execute():
    # import pandas as pd
    import xlwings as xw

    wb = xw.Book("TryWings.xlsx")
    sheet1 = wb.sheets["Sheet1"]
    while True:
        try:
            nextCostData = getCostData()
            # getting last edited row
            last_row = sheet1.cells(sheet1.cells.last_cell.row, 1).end("up").row
            print(last_row)
            sheet1[f"A{last_row+1}"].value = nextCostData
            time.sleep(45)
        except:
            print("Retrying")
            time.sleep(15)


execute()
