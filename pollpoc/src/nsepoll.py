import math
import requests
import os
import sys
import json
import pandas as pd

from datetime import datetime
import time

import xlwings as xw


def getCostData():
    inp_dict = json.loads(sys.argv[1])
    print(inp_dict)
    filename = inp_dict["filename"]
    interval = inp_dict["interval"]
    option = inp_dict["option"]
    expiry = inp_dict["expiry"]
    # filename = sys.argv[1]
    # interval = sys.argv[2]
    # option = sys.argv[3]
    # expiry = sys.argv[4]
    print("filename", filename)
    print("interval", interval)
    print("option", option)

    # expiry string - remove first 2 chars in year
    # Parse the date string
    # date_object = datetime.strptime(expiry, "%d-%b-%Y")

    # Format the date object into the desired format
    # expiry = date_object.strftime("%d-%b-%y")

    print("expiry", expiry)

    url = ""
    if len(option) > 0:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={option}"
    else:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,en-IN;q=0.8",
        "Referer": "https://www.nseindia.com/option-chain",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    }

    response = requests.get(url, headers=headers)

    responseData = response.json()
    print("6")

    exp_list = responseData["records"]["expiryDates"]

    print(exp_list)
    print(expiry in exp_list)

    if expiry in exp_list:
        exp_date = expiry
    else:
        exp_date = exp_list[0]

    ce = {}
    pe = {}
    n = 0
    m = 0

    for i in responseData["records"]["data"]:
        if i["expiryDate"] == exp_date:
            try:
                ce[n] = i["CE"]
                n = n + 1
            except:
                pass

            try:
                pe[m] = i["PE"]
                m = m + 1
            except:
                pass

    # underlying = ce_df["underlying"].iloc[0]
    print("5")

    ce_df = pd.DataFrame.from_dict(ce).transpose()
    # Drop the column named 'expiryDate' and 'underlying'
    ce_df.drop(columns=["expiryDate"], inplace=True)
    ce_df.drop(columns=["underlying"], inplace=True)
    ce_df.columns += "_Calls"

    pe_df = pd.DataFrame.from_dict(pe).transpose()
    # Drop the column named 'expiryDate' and 'underlying'
    pe_df.drop(columns=["expiryDate"], inplace=True)
    pe_df.drop(columns=["underlying"], inplace=True)
    pe_df.columns += "_Puts"

    df = pd.concat([ce_df, pe_df], axis=1)
    # print(df)
    print("4")

    # create_workbook("TryWings2.xlsx")
    wb = xw.Book("nse2excel.xlsx")
    print("wb", wb)
    # wb = xw.Book(
    #     f"{filename}.xlsx"
    # )  # same filename that you'll place inside paret poolpoc folder

    sheet1 = wb.sheets["Sheet1"]
    sheet2 = wb.sheets["Sheet2"]

    print("3")

    # get the last row that have been worked on inside the excel file
    last_row = sheet1.cells(sheet1.cells.last_cell.row, 1).end("up").row

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    sheet1.range(f"A{last_row+2}").value = current_time
    sheet1.range(f"B{last_row+2}").value = "Expiry Date"
    sheet1.range(f"C{last_row+2}").value = exp_date
    sheet1.range(f"C{last_row+2}").api.Font.Bold = True
    sheet1.range(f"D{last_row+2}").value = option
    sheet1.range(f"D{last_row+2}").api.Font.Bold = True
    # sheet1.range(f"D{last_row+2}").value = "Underlying Asset"
    # sheet1.range(f"E{last_row+2}").value = underlying
    # sheet1.range(f"E{last_row+2}").api.Font.Bold = True

    # for comparing
    df["strikePrice_Calls"] = df["strikePrice_Calls"].astype(float)
    df["underlyingValue_Puts"] = df["underlyingValue_Puts"].astype(float)

    sheet1.range(f"A{last_row+3}").value = df

    sheet2.clear()
    sheet2.range("A1").options(transpose=True).value = exp_list
    print("2")

    # print(responseData)

    # print(responseData["data"]["BTC"]["ohlc"]["c"])
    # variationPercent = responseData["data"]["BTC"]["change"]["percent"]
    # currentCost = responseData["data"]["BTC"]["ohlc"]["c"]
    # print(variationPercent)

    colorBearishOrBullish(sheet1, last_row, df)
    print("1")

    # df = pd.DataFrame([[1, 2], [3, 4]], columns=["a", "b"])
    # costData = [current_time, currentCost, variationPercent]
    # return responseData


# colors cells according to strike price and underlying asset value
def colorBearishOrBullish(sheet, last_row, df):
    # Bold Headings
    # for col in range(1, math.floor(df.shape[1])):
    #     sheet.cells[last_row + 1, col].api.Font.Bold = True

    # Color required cells
    for row in range(last_row + 3, last_row + 3 + len(df)):
        underlyingAssetValue = sheet.cells[row, df.shape[1]].value
        currentStrikePrice = sheet.cells[row, 1].value

        if (
            isinstance(currentStrikePrice, float)
            and isinstance(underlyingAssetValue, float)
            and currentStrikePrice < underlyingAssetValue
        ):
            for col in range(3, math.floor(df.shape[1] / 2) + 1):
                sheet.cells[row, col].color = (222, 214, 162, 0.41)  # Yellow color
        else:
            for col in range(math.floor(df.shape[1] / 2) + 3, df.shape[1]):
                sheet.cells[row, col].color = (222, 214, 162, 0.41)  # Yellow color


def create_workbook(filename):
    if os.path.exists(filename):
        print(f"The file '{filename}' already exists.")
        wb = xw.Book(filename)
        if len(wb.sheets) < 2:
            # Add Sheet1 if it doesn't exist
            if "Sheet1" not in [sheet.name for sheet in wb.sheets]:
                wb.sheets.add("Sheet1")
            # Add Sheet2 if it doesn't exist
            if "Sheet2" not in [sheet.name for sheet in wb.sheets]:
                wb.sheets.add("Sheet2")
        wb.save()
        wb.close()
    else:
        # Create a new instance of Excel
        app = xw.App(visible=True)

        # Add a new workbook
        wb = app.books.add()

        # Add Sheet1 and Sheet2
        wb.sheets.add("Sheet1")
        wb.sheets.add("Sheet2")

        # Change the sheet name
        wb.sheets[0].name = "Sheet1"
        wb.sheets[1].name = "Sheet2"

        # Write some data
        wb.sheets["Sheet1"].range("A1").value = "Hello"
        wb.sheets["Sheet1"].range("B1").value = "World!"
        wb.sheets["Sheet2"].range("A1").value = "Data"
        wb.sheets["Sheet2"].range("B1").value = "Analysis"

        # Save the workbook
        wb.save(filename)

        # Close the workbook
        wb.close()

        # Close the Excel application
        app.quit()


def execute():

    # checking if interval is provided
    # if sys.argv[2]:
    #     interval = sys.argv[2]
    # else:
    #     interval = 15
    # import pandas as pd
    # import xlwings as xw

    while True:
        try:
            getCostData()

            time.sleep(15)
        except:
            print("Retrying")
            time.sleep(15)


execute()
# getCostData()
