import win32com.client
import time

import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import sqlite3


# *****************************
# [def] 종목별 설정기간 csv 파일 생성
# *****************************
def makeStockTradeHistory(startDate, endDate):

    # 종목별 데이터 가지고 오기
    for i in range(0, cntStock - 1):
        # 주식코드
        stockCode = instCpStockCode.GetData(0, i)
        # 주식명
        stockName = instCpStockCode.GetData(1, i)
        print("[{}] 주식코드:{}, 주식명:{}".format(i, stockCode, stockName))

        # 파일생성
        fileName = "data/{}_{}_{}to{}.csv".format(stockCode, stockName, startDate, endDate)
        f = open(fileName, 'wt', encoding='utf-8')
        f.write(
            'stockCode,stackName,date,startPrice,highPrice,lowPrice,finalPrice,amountTrade,amounForeigner,amountAgencyBuy\n')

        # SetInputValue
        instStockChart.SetInputValue(0, stockCode)
        instStockChart.SetInputValue(1, ord('1'))
        instStockChart.SetInputValue(2, endDate)
        instStockChart.SetInputValue(3, startDate)
        instStockChart.SetInputValue(5, (0, 2, 3, 4, 5, 8, 16, 20))
        instStockChart.SetInputValue(6, ord('D'))
        instStockChart.SetInputValue(9, ord('1'))

        # BlockRequest
        instStockChart.BlockRequest()

        # GetHeaderValue
        numData = instStockChart.GetHeaderValue(3)
        numField = instStockChart.GetHeaderValue(1)

        # GetDataValue
        for i in range(numData):
            f.write(stockCode + ',' + stockName + ',')
            for j in range(numField):
                row = instStockChart.GetDataValue(j, i)
                f.write(str(row))
                if j == numField - 1:
                    f.write('\n')
                else:
                    f.write(',')

        time.sleep(0.5)  # 증권사 API 처리량 조절을 위해

        f.close()




# *****************************
# [def] DB 데이터 생성 From csv file
# *****************************
def makeDBdata():
    # directory 설정
    readDir = 'data'

    conn_string = "host=34.97.231.194 dbname='quants' user='monday' password='monday1!'"
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()

    # cur.execute("select 1")
    # result = cur.fetchall()
    # print(result)

    # Drop TABLE
    cur.execute('DROP TABLE if exists Origin_Trade')

    # 디렉토리안 모든 csv 파일 가지고 오기
    globbed_files = glob.glob(readDir + '/*.csv')  # creates a list of all csv files

    # 파일별 데이터 생성처리
    for file in globbed_files:
        data = pd.read_csv(file, engine='python', encoding='utf8')
        data.to_sql('Origin_Trade', conn, index=False, if_exists='append')

        fineName = os.path.basename(file[:-4])
        print('Insering {}'.format(fineName))


if __name__ == '__main__':

    # *****************************
    # CybosPlus 접속 확인
    # *****************************
    instCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    if instCpCybos.IsConnect == 1:
        print('Connected.... Good Luck !!!')
    else:
        print('Not Connected !!!')

    # *****************************
    # 전 종목 갯수 조회
    # *****************************

    # CYBOS에서 사용되는 주식코드 조회 작업을 함.
    instCpStockCode = win32com.client.Dispatch("CpUtil.CpStockCode")
    # 주식, 업종, ELW의 차트데이터를 수신합니다.
    instStockChart = win32com.client.Dispatch("CpSysDib.StockChart")

    # 종목코드 갯수
    cntStock = instCpStockCode.GetCount()
    print("종목수 : {}".format(cntStock))

    # *****************************
    # 종목별 설정기간 csv 파일 생성
    # *****************************
    startDate = 20090101
    endDate = 20191122
    makeStockTradeHistory(startDate, endDate);
