import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# 종목
# stock_list = ['TQQQ','SOXL','TNA','FNGU','UDOW'
#              ,'FAS','SPXL','UPRO','LABU','YINN'
#              ,'DFEN','TECL','BNKU','TMF','DRN'
#              ,'URTY','DPST','NAIL','NRGU','DUSL']


################## 값 설정 #########################

# 해당 주식
stock_list = ['TQQQ']

# 초기 금액
init_cash = 10000
# 백테스트 시작 날짜
back_test_start_date = '2021-10-01'
# 백테스트 기간
# 평단가 이하 경우 매수 전략 (1: 하루치 전향 매수) 해당 수치 곱하기 개념
under_price_buy_strategy = 1
# 평단가 이상 경우 매수 전략 (2: 하루치 절반 매수) 해당 수치 나누기 개념
upper_price_buy_strategy = 2
# 40회차후 매도 전략 (1.05 : 5% 수익시 매도)
after_40th_buy_strategy = 1.1



###########################################


for stock in stock_list :

    # 주식 데이터 가지고 오기
    data = yf.download(stock,start = back_test_start_date)
    data=data.reset_index()

    # 컬럼 : 날짜, 잔액, 주식명, 거래회차, 평균단가, 보유수량, 현재가, 전체평가액
    # columns : date, cash, stock, nth, avg_px, hold_nm, cur_px, est_val
    score = pd.DataFrame({'date' : [back_test_start_date]
                        ,'cash' : [init_cash]
                        ,'stock' : [stock]
                        ,'nth' : [0]
                        ,'avg_px' : [0]
                        ,'hold_nm' : [0]
                        , 'cur_px' : [0]
                        , 'est_val' : [0]})
    # print(score)
    cur_score = pd.Series({'date' : back_test_start_date
                        ,'cash' : init_cash
                        ,'stock' : stock
                        ,'nth' : 0
                        ,'avg_px' : 0
                        ,'hold_nm' : 0
                        , 'cur_px' : 0
                        , 'est_val' : 0})
    # print(cur_score)


    # 하루 매수 최대치 수량
    day_lim_vol = cur_score.cash / 40

    for i in range(240):

        # 매도후 하루 매수 최대치 수량 재설정
        if cur_score.nth == 0 :
            day_lim_vol = cur_score.cash / 40
        
        _date = data.Date[i]
        _cur_px = data['Close'][i]
        
        # 매수 수량
        _buy_vol = 0
        # 전날 액
        _before_cash = 0
        # 당일 잔액
        _after_cash = 0
        # 회차
        _nth = cur_score.nth
        # 평균 매수 단가
        _avg_px = cur_score.avg_px
        # 보유 수량
        _hold_nm = cur_score.hold_nm
        # 전체 평가액
        _est_val = 0
        
        
        # nth가 첫 거래 일때
        if cur_score.nth == 0 :
    #         print("\n 1 -----------------------------------------------")
            _buy_nm = int(day_lim_vol * under_price_buy_strategy / _cur_px)
            _buy_vol = _buy_nm * _cur_px
            _before_cash = cur_score.cash
            _nth = 1
            _avg_px = _cur_px
            _hold_nm = _buy_nm
            _after_cash = _before_cash - (_buy_nm*_cur_px)
            _est_val = _hold_nm * _cur_px + _after_cash
            
        # 40회차 이상일 경우
        elif cur_score.nth >= 40:
            # 이득일때 전량 매도
            if _avg_px * after_40th_buy_strategy <= _cur_px :
                _before_cash = cur_score.cash
                _after_cash = _before_cash + (_cur_px * _hold_nm)
                _nth = 0
                _avg_px = 0
                _hold_nm = 0
                _est_val = _after_cash
            # 아무것도 하지 않음
            else :
                _buy_nm = 0
                _buy_vol = _buy_nm * _cur_px
                _before_cash = cur_score.cash
                _nth = cur_score.nth
                _avg_px = cur_score.avg_px
                _hold_nm = cur_score.hold_nm
                _after_cash = _before_cash
                _est_val = _hold_nm * _cur_px + _after_cash
                
        # 40회차 이내 경우
        else:
            # 10% 이득 일때 전량 매도
            if _avg_px * 1.1 <= _cur_px :
    #             print("\n 2 -----------------------------------------------")
                _before_cash = cur_score.cash
                _after_cash = _before_cash + (_cur_px * _hold_nm)
                _nth = 0
                _avg_px = 0
                _hold_nm = 0
                _est_val = _after_cash
                
            # 10% 이득보다 낮은 경우
            else:
                # 현재가 < 평단 경우 그날 한계 수량 매수
                if _cur_px < _avg_px:
    #                 print("\n 3 -----------------------------------------------")
                    # 모두 매수
                    _buy_nm = int(day_lim_vol * under_price_buy_strategy / _cur_px)
                    _buy_vol = _buy_nm * _cur_px
                    _before_cash = cur_score.cash
                    _nth += 1
                    _avg_px = ((_avg_px*_hold_nm)+(_buy_vol))/(_hold_nm+_buy_nm)
                    _hold_nm += _buy_nm
                    _after_cash = _before_cash - (_buy_vol)
                    _est_val = _hold_nm * _cur_px + _after_cash
                    
                # 평단이 현재가 보다 높을 경우 절반 매수
                else :
    #                 print("\n 4 -----------------------------------------------")
                    # 절반 매수
                    _buy_nm = int(day_lim_vol / upper_price_buy_strategy / _cur_px)
                    _buy_vol = _buy_nm * _cur_px
                    _before_cash = cur_score.cash
                    _nth += 1
                    _avg_px = ((_avg_px*_hold_nm)+(_buy_vol))/(_hold_nm+_buy_nm)
                    _hold_nm += _buy_nm
                    _after_cash = _before_cash - (_buy_vol)
                    _est_val = _hold_nm * _cur_px + _after_cash
            
        new_score = {'date' : _date
                    ,'cash' : _after_cash
                        ,'stock' : 'TQQQ'
                        ,'nth' : _nth
                        ,'avg_px' : _avg_px
                        ,'hold_nm' : _hold_nm
                        , 'cur_px' : _cur_px
                        , 'est_val' : _est_val
                        }
        score = score.append(new_score, ignore_index=True)
    #     print(score)
        
        cur_score.date = _date
        cur_score.cash = _after_cash
        cur_score.stock ='TQQQ'
        cur_score.nth = _nth
        cur_score.avg_px = _avg_px
        cur_score.hold_nm = _hold_nm
        cur_score.cur_px = _cur_px
        cur_score.est_val = _est_val
    #     print(cur_score)
            
    #     print("\n_date=[{}],\_cur_px=[{}],\n_before_cash=[{}],\n_buy_vol=[{}],\n_after_cash=[{}],\n_nth=[{}],\n_avg_px=[{}],\n_hold_nm=[{}],\n_est_val=[{}]"
    #           .format(_date,_cur_px,_before_cash,_buy_vol,_after_cash,_nth,_avg_px,_hold_nm,_est_val))

        if i+1 == len(data) :
            break

    # score.tail()


    # 그래프 그리기
    fig, ax = plt.subplots()
    fig.subplots_adjust(right=0.85)

    twin1 = ax.twinx()
    twin2 = ax.twinx()

    # Offset the right spine of twin2.  The ticks and label have already been
    # placed on the right by twinx above.
    twin2.spines['right'].set_position(("axes", 1.1))

    p1, = ax.plot(score.est_val[1:], "b-", label=stock+' Evaluation')
    p2, = twin1.plot(score.cur_px[1:], "r-", label=stock+' Stock_val')
    p3, = twin2.plot(score.nth[1:], "g--", label=stock+' Nth', linestyle='--')

    ax.set_xlabel("Day")
    ax.set_ylabel("Evaluation")
    twin1.set_ylabel("Stock_val")
    twin2.set_ylabel("Nth")

    ax.yaxis.label.set_color(p1.get_color())
    twin1.yaxis.label.set_color(p2.get_color())
    twin2.yaxis.label.set_color(p3.get_color())

    tkw = dict(size=4, width=1.5)
    ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
    twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
    twin2.tick_params(axis='y', colors=p3.get_color(), **tkw)
    ax.tick_params(axis='x', **tkw)

    ax.legend(handles=[p1, p2, p3])

    plt.show()



