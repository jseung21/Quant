import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl

###################### 값 설정 #########################
# 해당 주식
stock_list = ['TQQQ']
# 초기 금액
init_cash = 5000
# 백테스트 시작 날짜
back_test_start_date = '2008-02-01'
# 백테스트 기간 (1년 평균 : 240)
test_priod = 2400 
# VR 사이클 (10: 10일 평균 2주)
vr_cycle = 10

# 거래 단위당 투입 금액
input_money_per_trade = 250

# pool 금액
pool_cash = 0






# # 평단가 이하 경우 매수 전략 (1: 하루치 전향 매수) 해당 수치 곱하기 개념
# under_price_buy_strategy = 1
# # 평단가 이상 경우 매수 전략 (2: 하루치 절반 매수) 해당 수치 나누기 개념
# upper_price_buy_strategy = 2
# # 40회차후 매도 전략 (1.05 : 5% 수익시 매도)
# after_40th_buy_strategy = 1.1
########################################################


def value_rebalansing(trade_data) :
    
    
    # pool은 V의 60%를 넘지 않는다 <-- 이렇게 되도록 매매 한다

    _next_expect_value = 0 
    _current_expect_value = 0
    _current_evalution = 0
    _rise_ratio = 0
    _pool = 0
    _next_min_value = 0
    _next_max_value = 0

    # TODO : 값설정
    


    # 상승률 찾기 = pool/현재V기대치, 그리고 현재평가금과 현재V와 비교
    _rise_ratio_tmp = _pool / _current_expect_value
    if _current_evalution < _current_expect_value :
        _rise_ratio = 1 + (_rise_ratio_tmp / 10)
    else :
        _rise_ratio = 1.005 + (_rise_ratio_tmp / 10)

    # 다음V = 현재V * 상승률 + pool
    _next_expect_value = _current_evalution * _rise_ratio + _pool

    # 다음 최소값 = 다음V * 0.8
    _next_min_value = _next_expect_value * 0.8

    # 다음 최대값 = 다음V * 1.25    
    _next_max_value = _next_expect_value * 1.25



for stock in stock_list :

    # 주식 데이터 가지고 오기
    trade_data = yf.download(stock,start = back_test_start_date)
    trade_data = trade_data.reset_index()

    # 거래 사이클 
    _trade_cycle = 1


    # 컬럼 : 날짜, 현재평가금, 현재V기대치, 최소값, 최대값, 거래액, POOL
    # columns : cur_eval, cur_expt_val, min_val, max_val, trade_vol, pool
    score = pd.DataFrame({'date' : [back_test_start_date]
                        ,'cur_eval' : [0]
                        ,'cur_expt_val' : [0]
                        ,'min_val' : [0]
                        ,'max_val' : [0]
                        ,'trade_vol' : [0]
                        , 'pool' : [0]})



    # 테스트 기간만큼 실행
    for i in range(test_priod) :

        # Value Rebalansing
        if _trade_cycle == 1 and _trade_cycle % vr_cycle == 0 :
            
            value_rebalansing(trade_data)

        else :
            1=1




        # 다음 trade
        _trade_cycle += 1

        # 거래 사이클 보다 작을 경우
        # if _trade_cycle < trade_cycle :

            # 당일 주가 확인 후 거래
            # 현재 평가 금액

            # V 기대치

            # 최소 

            # 최대



            ### 다음V = 현재V * 상승률 + pool


        # else :
        #     # 금액 투입
        #     pool_cash += input_money_per_trade

        #     # LOC 매도/매수 설정

        _date = data.Date[i]
        _cur_px = data['Close'][i]
