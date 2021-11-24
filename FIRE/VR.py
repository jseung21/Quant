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


def value_rebalansing(vr_score, day_score) :
    
    
    # pool은 V의 60%를 넘지 않는다 <-- 이렇게 되도록 매매 한다

    _next_expect_value = 0 
    _current_expect_value = vr_cycle.cur_expt_val.values[-1]
    # 현재평가금
    _current_evalution = day_score.cur_eval.values[-1]
    _rise_ratio = 0
    _pool = day_score.cash.values[-1]
    _next_min_value = 0
    _next_max_value = 0


    # 상승률 찾기 = pool/현재V기대치, 그리고 현재평가금과 현재V와 비교
    _rise_ratio_tmp = _pool / _current_expect_value
    # 기대치보다 적게 오른 경우, 현재평가금 < 현재기대치
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


    # 날짜와 현재 평가액 세팅
    vr_score.date.values[-1] = day_score.date.values[-1]
    vr_score.cur_eval.values[-1] = day_score.cur_eval.values[-1]
    
    new_vr_score = {'date' : ''
                    ,'stock_nm' : stock
                    ,'cur_eval' : ''
                    ,'cur_expt_val' : _next_expect_value
                    ,'min_val' : _next_min_value
                    ,'max_val' : _next_max_value
                    ,'trade_vol' : ''
                    ,'pool' : ''}
    vr_score = vr_score.append(new_vr_score, ignore_index=True)



# init
for stock in stock_list :

    # 주식 데이터 가지고 오기
    trade_data = yf.download(stock,start = back_test_start_date)
    trade_data = trade_data.reset_index()
#                Date        Open        High         Low       Close   Adj Close    Volume
# 0    2010-02-11    0.813750    0.869792    0.811146    0.865104    0.862942   1728000
# 1    2010-02-12    0.841563    0.876146    0.836667    0.868646    0.866475   4300800
# 2    2010-02-16    0.889063    0.904375    0.875104    0.902292    0.900037   4809600
# 3    2010-02-17    0.914375    0.917813    0.900625    0.917604    0.915311   9590400


    # 거래 사이클 
    _trade_cycle_cnt = 1


    # 컬럼 : 날짜, 주식명,  현재평가금, 현재V기대치, 최소값, 최대값, 거래액, POOL
    # columns : date, stock_nm, cur_eval, cur_expt_val, min_val, max_val, trade_vol, pool
    vr_score = pd.DataFrame(columns=['date','stock_nm','cur_eval','cur_expt_val','min_val','max_val','trade_vol','pool'])
    # vr_score = pd.DataFrame({'date' : [back_test_start_date]
    #                      ,'stock_nm' : [stock]
    #                      ,'cur_eval' : [0]
    #                      ,'cur_expt_val' : [0]
    #                      ,'min_val' : [0]
    #                      ,'max_val' : [0]
    #                      ,'trade_vol' : [0]
    #                      ,'pool' : [init_cash]})

    day_score = pd.DataFrame(columns=['date','stock_nm','cur_px','hold_vol','cur_eval','cash'])




    # 테스트 기간만큼 실행
    for i in range(test_priod) :

        # 첫날 거래
        if i == 0 :
            _date = trade_data.Date[i]
            _cur_px = trade_data.Close[i]
            _hold_vol = init_cash // _cur_px
            _cur_eval = _cur_px * _hold_vol
            new_day_score = {'date' : _date
                           ,'stock_nm' : stock
                           ,'cur_px' : _cur_px
                           ,'hold_vol' : _hold_vol
                           ,'cur_eval' : _cur_eval
                           ,'cash' : init_cash - _cur_eval}
            day_score = day_score.append(new_day_score, ignore_index=True)
            
            new_vr_score = {'date' : _date
                            ,'stock_nm' : stock
                            ,'cur_eval' : _cur_eval
                            ,'cur_expt_val' : init_cash
                            ,'min_val' : 0
                            ,'max_val' : 0
                            ,'trade_vol' : 0
                            ,'pool' : init_cash - _cur_eval}
            vr_score = vr_score.append(new_vr_score, ignore_index=True)
            
            
            value_rebalansing(vr_score, day_score)
            
            
        # TODO : Day 거래
        else :
            1 ==1


        # Value Rebalansing
        if _trade_cycle_cnt % vr_cycle == 0 :
            
            value_rebalansing(vr_score, trade_data)

  
        # 다음 trade
        _trade_cycle_cnt += 1
