import time
import pyupbit
import pandas as pd
import warnings

#import matplotlib.pyplot as plt


warnings.filterwarnings('ignore')


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 500)

candle_type = '60min'
#candle_type = 'day'

if candle_type == '1min' :
    candle_adapt = 'minute1'
    time_unit = 1
elif candle_type == '3min' :
    candle_adapt = 'minute3'
    time_unit = 3
elif candle_type == '5min' :
    candle_adapt = 'minute5'
    time_unit = 5
elif candle_type == '10min' :
    candle_adapt = 'minute10'
    time_unit = 10
elif candle_type == '15min' :
    candle_adapt = 'minute15'
    time_unit = 15
elif candle_type == '30min' :
    candle_adapt = 'minute30'
    time_unit = 30
elif candle_type == '60min' :
    candle_adapt = 'minute60'
    time_unit = 60
elif candle_type == '240min' :
    candle_adapt = 'minute240'
    time_unit = 240
elif candle_type == 'day' :
    candle_adapt = 'day'
    time_unit = (60 * 24)
elif candle_type == 'month' :
    candle_adapt = 'month'
    time_unit = 60 * 24 * 30


simul_duration = [100, 365]

No_of_1st_target = 1000

#candle_count = int((60/time_unit) * 24 * 365 * 5)
#candle_count = int((60/time_unit) * 24 * 10 * 1)

transaction_fee_ratio = 0.0005   # 거래 수수료 비율

### 거래 후 check 조건값 설정
check_time_dur = 5   # 거래 이후, 몇개 구간 동안의 추이 (거래값 대비 최대값의 비율, 거래값 대비 구간내 평균값의 비율, 거래값 대비 최소값의 비율 등)
start_point = 50


# 투자 대상 코인
coin_No = 7

# Test setting
vol_duration = 12
buy_price_up_unit = 1
sell_price_buffer = 3

### moving average 산출 구간 설정
ma_duration_long = 100
ma_duration_mid = 35
ma_duration_short = 15

'''
### Buy transation 조건값 설정
ratio_ema_mid_rise = [1.0003]
successive_rise = [2]
ratio_ema_mid_long = [0.9]
ratio_vol_curr_prior = [0.8]
diff_m_l_factor = [0.01]
diff_vol_aver = [1.5]
under_long_duration = 20
recent_vol_duration = 10

### Sell transaction 조건값 설정
ratio_sell = [0.9991]
add_ratio_sell = [0.0003]
sell_method_vol_cri = [0.5]
ratio_diff_ema_mid = [0.005]
ratio_sell_forced = [0.05]
'''


### Buy transation 조건값 설정
ratio_ema_mid_rise = [1.0003, 1.0004, 1.0005]
successive_rise = [2, 3]
ratio_ema_mid_long = [0.98, 0.985, 0.99]
ratio_vol_curr_prior = [0.8, 1.0, 1.2]
diff_m_l_factor = [0.01, 0.015, 0.02]
diff_vol_aver = [1.5, 2.0, 2.5]
under_long_duration = 20
recent_vol_duration = 10

### Sell transaction 조건값 설정
ratio_sell = [0.9991, 0.9993, 0.9995]
add_ratio_sell = [0.0003, 0.0005, 0.0007]
sell_method_vol_cri = [0.5, 0.7, 1.0]
ratio_diff_ema_mid = [0.006, 0.007, 0.008]
ratio_sell_forced = [0.05, 0.07, 0.1]

'''
### Buy transation 조건값 설정
ratio_ema_mid_rise = [1.0003, 1.0004]
successive_rise = [2, 3]
ratio_ema_mid_long = [0.98, 0.985]
ratio_vol_curr_prior = [0.8, 1.0]
diff_m_l_factor = [0.01, 0.015]
diff_vol_aver = [1.5, 2.0]
under_long_duration = 20
recent_vol_duration = 10

### Sell transaction 조건값 설정
ratio_sell = [0.9991, 0.9993]
add_ratio_sell = [0.0003, 0.0005]
sell_method_vol_cri = [0.5, 0.7]
ratio_diff_ema_mid = [0.007, 0.008]
ratio_sell_forced = [0.07, 0.1]
'''


tickers = pyupbit.get_tickers()

LIST_coin_KRW = []

for i in range (0, len(tickers), 1):
    if tickers[i][0:3] == 'KRW':
        LIST_coin_KRW.append(tickers[i])

LIST_check_coin_currency = []

for i in range (0, len(LIST_coin_KRW), 1):
    LIST_check_coin_currency.append(LIST_coin_KRW[i][4:])

LIST_check_coin_currency_2 = []

for i in range (0, len(LIST_check_coin_currency), 1) :
    temp = 'KRW-' + LIST_check_coin_currency[i]
    LIST_check_coin_currency_2.append(temp)

DF_volume_cri = pyupbit.get_ohlcv(LIST_check_coin_currency_2[coin_No], count = vol_duration , interval = 'month')
volume_cri = DF_volume_cri['volume'].sum() / int((60/time_unit) * 24 * 30 * vol_duration)

# 매수 최소단위 산출

if DF_volume_cri['open'][-1] >= 1000000 :  # 200만원 이상은 거래단위가 1000원, 100~200만원은 거래단위가 500원이지만 편의상 200만원 이상과 함께 처리
    unit_factor = -3
    unit_value = 1000
elif DF_volume_cri['open'][-1] >= 100000 :
    unit_factor = -2
    unit_value = 50
elif DF_volume_cri['open'][-1] >= 10000 :
    unit_factor = -1
    unit_value = 10
elif DF_volume_cri['open'][-1] >= 1000 :
    unit_factor = -1
    unit_value = 5
elif DF_volume_cri['open'][-1] >= 100 :
    unit_factor = 0
    unit_value = 1
else :
    DF_volume_cri['open'][-1] <= 100   # 100원 미만은 별도로 code에서 int형이 아닌 float형으로 형변환 해줘야함
    unit_factor = 1
    unit_value = 0.1

print ('DF_volume_cri[open][-1] : {0}  / unit_value : {1}'.format(DF_volume_cri['open'][-1], unit_value))


DF_result = pd.DataFrame(columns = ['Coin_No', 'Coin', 'simul_day', 'No_of_buy', 'No_of_N_sell', 'No_of_SC_sell', 'No_of_price_diff_sell', 'No_of_L_sell', 'average_Highest_ratio', 'average_aver_ratio_duration', 'average_L_ratio', 'std_open_value', 'Ref_value', 'residual_money', 'residual_value', \
                         'ratio_ema_mid_rise', 'successive_rise', 'ratio_ema_mid_long', 'ratio_vol_curr_prior', 'diff_m_l_factor', 'diff_vol_aver', 'under_long_duration', 'recent_vol_duration', \
                         'ratio_sell', 'add_ratio_sell', 'sell_method_vol_cri', 'ratio_diff_ema_mid', 'ratio_sell_forced'])


temp_data = {'Coin_No' : [0], 'Coin' : ['name'], 'simul_day' : [0], 'No_of_buy' : [0], 'No_of_N_sell' : [0], 'No_of_SC_sell' : [0], 'No_of_price_diff_sell' : [0], 'No_of_L_sell' : [0], 'average_Highest_ratio' : [0.0], 'average_aver_ratio_duration' : [0.0], 'average_L_ratio' : [0.0], 'std_open_value' : [0.0], 'Ref_value' : [0.0], 'residual_money' : [0.0], 'residual_value' : [0.0], \
             'ratio_ema_mid_rise': [0.0], 'successive_rise': [0], 'ratio_ema_mid_long': [0.0], 'ratio_vol_curr_prior': [0.0], 'diff_m_l_factor': [0.0], 'diff_vol_aver': [0], 'under_long_duration': [0], 'recent_vol_duration': [0], \
             'ratio_sell': [0.0], 'add_ratio_sell': [0.0], 'sell_method_vol_cri': [0.0], 'ratio_diff_ema_mid': [0.0], 'ratio_sell_forced': [0.0]}

DF_immediate = pd.DataFrame(temp_data)


candle_count = int((60 / time_unit) * 24 * simul_duration[0])
DF_short = pyupbit.get_ohlcv(LIST_check_coin_currency_2[coin_No], count=candle_count, interval=candle_adapt)

DF_short['ratio_prior_to_cur'] = DF_short['open'] / DF_short['open'].shift(1)

DF_short['ema_long'] = DF_short['open'].ewm(span=ma_duration_long, adjust=False).mean()
DF_short['ema_mid'] = DF_short['open'].ewm(span=ma_duration_mid, adjust=False).mean()
DF_short['ema_short'] = DF_short['open'].ewm(span=ma_duration_short, adjust=False).mean()

DF_short['ratio_ema_long'] = DF_short['ema_long'] / DF_short['ema_long'].shift(1)

DF_short['fall_check'] = 0
DF_short.loc[(DF_short['ratio_ema_long'] < 1), 'fall_check'] = 1

DF_short['ratio_ema_mid'] = DF_short['ema_mid'] / DF_short['ema_mid'].shift(1)

DF_short['rise_check_mid'] = 0
DF_short.loc[(DF_short['ratio_ema_mid'] > 1), 'rise_check_mid'] = 1

DF_short['ratio_ema_short'] = DF_short['ema_short'] / DF_short['ema_short'].shift(1)

DF_short['rise_check_short'] = 0
DF_short.loc[(DF_short['ratio_ema_short'] > 1), 'rise_check_short'] = 1

DF_short['diff_m_l'] = DF_short['ema_mid'] - DF_short['ema_long']

DF_short['mid_under_long'] = 0
DF_short.loc[(DF_short['diff_m_l'] > 0), 'mid_under_long'] = 1

DF_short['vol_amount'] = 0.0

DF_short.loc[(DF_short['volume'] >= (2.0 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 2.0
DF_short.loc[(DF_short['volume'] < (2.0 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (1.8 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 1.8
DF_short.loc[(DF_short['volume'] < (1.8 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (1.6 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 1.6
DF_short.loc[(DF_short['volume'] < (1.6 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (1.4 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 1.4
DF_short.loc[(DF_short['volume'] < (1.4 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (1.2 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 1.2
DF_short.loc[(DF_short['volume'] < (1.2 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (1.0 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 1.0
DF_short.loc[(DF_short['volume'] < (1.0 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (0.8 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 0.8
DF_short.loc[(DF_short['volume'] < (0.8 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (0.6 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 0.6
DF_short.loc[(DF_short['volume'] < (0.6 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (0.4 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 0.4
DF_short.loc[(DF_short['volume'] < (0.4 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())) & \
            (DF_short['volume'] >= (0.2 * DF_short.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_short)))['volume'].mean())), 'vol_amount'] = 0.2

DF_short['recent_vol_aver'] = 0.0

for k in range(0, len(DF_short), 1):
    DF_short['recent_vol_aver'][k] = DF_short.iloc[(k - recent_vol_duration): k]['vol_amount'].sum()

print ('simul_duration : ', simul_duration[0])

for v_0 in ratio_ema_mid_rise :
    for v_1 in successive_rise :
        for v_2 in ratio_ema_mid_long :
            for v_3 in ratio_vol_curr_prior :
                for v_4 in diff_m_l_factor :
                    for v_5 in diff_vol_aver :
                        for v_6 in ratio_sell :
                            for v_7 in add_ratio_sell :
                                for v_8 in sell_method_vol_cri :
                                    for v_9 in ratio_diff_ema_mid  :
                                        for v_10 in ratio_sell_forced :

                                            print (v_0, v_1, v_2, v_3, v_4, v_5, v_6, v_7, v_8, v_9, v_10)

                                            test_money = 1000000

                                            DF_test = DF_short.copy ()


                                            # Buy / Sell logic

                                            DF_test['buy_signal'] = 0
                                            DF_test['buy_signal_flag'] = 0
                                            DF_test['sell_signal'] = 0
                                            DF_test['sell_normal'] = 0
                                            DF_test['sell_state_change'] = 0
                                            DF_test['sell_price_diff'] = 0
                                            DF_test['sell_loss'] = 0
                                            DF_test['sold_price'] = 0
                                            buy_price = 0
                                            buy_time = 0
                                            sell_force = 0

                                            for k in range(start_point + 1, len(DF_test), 1):
                                                if (DF_test['buy_signal_flag'][k - 1] == 0):
                                                    if (DF_test['ratio_ema_long'][k - 2] > 1.0001) and (DF_test['ratio_ema_long'][k - 1] > 1.0001) and (DF_test['ratio_ema_long'][k] > 1.0001) and (DF_test['ratio_ema_mid'][k] > v_0) and \
                                                        (DF_test.iloc[(k - (v_1 + 1)): (k + 1)]['rise_check_short'].sum() >= (v_1 - 1)) and \
                                                        ((DF_test['ema_mid'][k] / DF_test['ema_long'][k]) > v_2) and \
                                                        (DF_test['volume'][k - 1] >= (v_3 * DF_test.iloc[(k - 3):(k - 1)]['volume'].mean())) and \
                                                        (DF_test.iloc[(k - under_long_duration): k]['mid_under_long'].sum() == 0) and (- DF_test.loc[DF_test.iloc[(k - under_long_duration): k]['diff_m_l'].idxmin()]['diff_m_l'] > (v_4 * DF_test['open'][k])) and \
                                                        ((DF_test.loc[DF_test.iloc[(k - 5): (k - 1)]['recent_vol_aver'].idxmax()]['recent_vol_aver'] - DF_test['recent_vol_aver'][k - 1]) < v_5):
                                                        DF_test['buy_signal'][k] = 1
                                                        DF_test['buy_signal_flag'][k] = 1
                                                        buy_price = DF_test['open'][k] + (buy_price_up_unit * unit_value)
                                                        buy_time = DF_test.index[k]
                                                        # print ('buy_price :', buy_price)

                                                # 매도 로직
                                                if DF_test['buy_signal_flag'][k - 1] == 1:
                                                    DF_test['buy_signal_flag'][k] = 1
                                                    DF_test['sold_price'][k] = DF_test['sold_price'][k - 1]

                                                    if ((DF_test['volume'][k - 1] >= (v_8 * DF_test.iloc[(k - 4):(k - 1)]['volume'].mean())) and (DF_test.iloc[(k - 9):(k + 1)]['ratio_ema_long'].mean() < v_6)):
                                                        DF_test['sell_signal'][k] = 1
                                                        DF_test['buy_signal_flag'][k] = 0
                                                        DF_test['sell_normal'][k] = 1
                                                        DF_test['sold_price'][k] = DF_test['open'][k]

                                                    elif (DF_test['volume'][k - 1] < (v_8 * DF_test.iloc[(k - 4):(k - 1)]['volume'].mean())) and (DF_test['ratio_ema_long'][k] < (v_6 + v_7)):
                                                        DF_test['sell_signal'][k] = 1
                                                        DF_test['buy_signal_flag'][k] = 0
                                                        DF_test['sell_state_change'][k] = 1
                                                        DF_test['sold_price'][k] = DF_test['open'][k]

                                                    elif (DF_test['volume'][k - 1] < (v_8 * DF_test.iloc[(k - 4):(k - 1)]['volume'].mean())) and ((DF_test.loc[DF_test.iloc[(k - 5): k]['ema_mid'].idxmax()]['ema_mid'] - DF_test['ema_mid'][k]) > (v_9 * DF_test['open'][k])):
                                                        DF_test['sell_signal'][k] = 1
                                                        DF_test['buy_signal_flag'][k] = 0
                                                        DF_test['sell_price_diff'][k] = 1
                                                        DF_test['sold_price'][k] = DF_test['open'][k]

                                                    elif ((DF_test['low'][k] / buy_price) < (1 - v_10)):
                                                        DF_test['sell_signal'][k] = 1
                                                        DF_test['buy_signal_flag'][k] = 0
                                                        DF_test['sell_loss'][k] = 1
                                                        DF_test['sold_price'][k] = (buy_price * (1 - v_10))

                                            DF_test['H_duration'] = 0
                                            DF_test['H_ratio'] = 0.0
                                            DF_test['L_duration'] = 0
                                            DF_test['L_ratio'] = 0.0
                                            DF_test['aver_ratio_duration'] = 0.0
                                            # DF_test['std'] = 0
                                            No_of_test_stock = 0
                                            transaction_No = 0

                                            for l in range(check_time_dur, (len(DF_test) - check_time_dur), 1):
                                                if (DF_test['buy_signal'][l] == 1):
                                                    DF_test['H_duration'][l] = DF_test.loc[DF_test.iloc[l: (l + check_time_dur)]['high'].idxmax()]['high']
                                                    DF_test['L_duration'][l] = DF_test.loc[DF_test.iloc[l: (l + check_time_dur)]['low'].idxmin()]['low']

                                            for m in range(check_time_dur, (len(DF_test) - check_time_dur), 1):
                                                if (DF_test['buy_signal'][m] == 1):
                                                    DF_test['H_ratio'][m] = DF_test['H_duration'][m] / DF_test['open'][m]
                                                    DF_test['L_ratio'][m] = DF_test['L_duration'][m] / DF_test['open'][m]
                                                    DF_test['aver_ratio_duration'][m] = DF_test.iloc[(m + 1): ((m + 1) + check_time_dur)]['ratio_prior_to_cur'].sum() / check_time_dur

                                            No_of_test_stock = 0
                                            transaction_No = 0

                                            for n in range(0, len(DF_test), 1):
                                                if DF_test['buy_signal'][n] == 1:
                                                    transaction_No = transaction_No + 1
                                                    No_of_test_stock = (test_money / (DF_test['open'][n] + (buy_price_up_unit * unit_value))) * (1 - transaction_fee_ratio)
                                                    test_money = test_money - ((DF_test['open'][n] + (buy_price_up_unit * unit_value)) * No_of_test_stock)
                                                    #print('\n[transaction_BUY] {0}  transaction_No : {1}  / residual_money : {2:,}  / No_of_stock : {3}'.format(DF_test.index[n], transaction_No, test_money, No_of_test_stock))


                                                elif DF_test['sell_signal'][n] == 1:
                                                    if DF_test['sell_normal'][n] == 1:
                                                        test_money = test_money + (((DF_test['sold_price'][n] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                                                        No_of_test_stock = 0
                                                        #print('[transaction_SELL_Normal] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test.index[n], transaction_No, DF_test['sell_normal'][n], DF_test['sell_state_change'][n], DF_test['sell_price_diff'][n], DF_test['sell_loss'][n], test_money, No_of_test_stock))

                                                    elif DF_test['sell_state_change'][n] == 1:
                                                        test_money = test_money + (((DF_test['open'][n] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                                                        No_of_test_stock = 0
                                                        #print('[transaction_SELL_state_change] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test.index[n], transaction_No, DF_test['sell_normal'][n], DF_test['sell_state_change'][n], DF_test['sell_price_diff'][n], DF_test['sell_loss'][n], test_money, No_of_test_stock))

                                                    elif DF_test['sell_price_diff'][n] == 1:
                                                        test_money = test_money + (((DF_test['open'][n] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                                                        No_of_test_stock = 0
                                                        #print('[sell_price_diff] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test.index[n], transaction_No, DF_test['sell_normal'][n], DF_test['sell_state_change'][n], DF_test['sell_price_diff'][n], DF_test['sell_loss'][n], test_money, No_of_test_stock))

                                                    elif DF_test['sell_loss'][n] == 1:
                                                        test_money = test_money + (((DF_test['sold_price'][n] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                                                        No_of_test_stock = 0
                                                        #print('[transaction_SELL_Loss] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test.index[n], transaction_No, DF_test['sell_normal'][n], DF_test['sell_state_change'][n], DF_test['sell_price_diff'][n], DF_test['sell_loss'][n], test_money, No_of_test_stock))

                                            DF_bought = DF_test[DF_test['buy_signal'] == 1]
                                            #print('[Final result] \nNo. of transaction : {0}  / resisual money : {1:,}  / residual stocks : {2} / ref_value__stock price x stocks : {3:,}'.format(transaction_No, test_money, No_of_test_stock, (DF_test['open'][-1] * No_of_test_stock)))
                                            #print('\nNo. of normal selling : {0}  / state_change selling : {1}  /  price_diff_selling : {2}'.format(DF_test['sell_normal'].sum(), DF_test['sell_state_change'].sum(), DF_test['sell_price_diff'].sum()))
                                            #print('\n[Simul_Result]\nNo_of_buy : {0}  /  average_H_ratio : {1}  / average_aver_ratio_duration : {2}  / average_L_ratio : {3}'.format(len(DF_bought), DF_bought['H_ratio'].mean(), DF_bought['aver_ratio_duration'].mean()))

                                            #DF_test.to_excel('DF_test_multi_{0}_{1}_days.xlsx'.format(LIST_check_coin_currency[coin_No], i))

                                            DF_immediate['Coin_No'] = coin_No
                                            DF_immediate['Coin'] = LIST_check_coin_currency_2[coin_No]
                                            DF_immediate['simul_day'] = simul_duration[0]
                                            DF_immediate['No_of_buy'] = DF_test['buy_signal'].sum()
                                            DF_immediate['No_of_N_sell'] = DF_test['sell_normal'].sum()
                                            DF_immediate['No_of_SC_sell'] = DF_test['sell_state_change'].sum()
                                            DF_immediate['No_of_price_diff_sell'] = DF_test['sell_price_diff'].sum()
                                            DF_immediate['No_of_L_sell'] = DF_test['sell_loss'].sum()
                                            DF_immediate['average_Highest_ratio'] = DF_bought['H_ratio'].mean()
                                            DF_immediate['average_aver_ratio_duration'] = DF_bought['aver_ratio_duration'].mean()
                                            DF_immediate['average_L_ratio'] = DF_bought['L_ratio'].mean()
                                            DF_immediate['std_open_value'] = DF_test['open'].std()
                                            DF_immediate['Ref_value'] = (DF_bought['H_ratio'].mean() * DF_bought['aver_ratio_duration'].mean() * DF_bought['L_ratio'].mean())
                                            DF_immediate['residual_money'] = test_money
                                            DF_immediate['residual_value'] = (DF_test['open'][-1] * No_of_test_stock)
                                            DF_immediate['ratio_ema_mid_rise'] = v_0
                                            DF_immediate['successive_rise'] = v_1
                                            DF_immediate['ratio_ema_mid_long'] = v_2
                                            DF_immediate['ratio_vol_curr_prior'] = v_3
                                            DF_immediate['diff_m_l_factor'] = v_4
                                            DF_immediate['diff_vol_aver'] = v_5
                                            DF_immediate['under_long_duration'] = under_long_duration
                                            DF_immediate['recent_vol_duration'] = recent_vol_duration
                                            DF_immediate['ratio_sell'] = v_6
                                            DF_immediate['add_ratio_sell'] = v_7
                                            DF_immediate['sell_method_vol_cri'] = v_8
                                            DF_immediate['ratio_diff_ema_mid'] = v_9
                                            DF_immediate['ratio_sell_forced'] = v_10

                                            DF_result = pd.concat([DF_result, DF_immediate], axis=0)

#DF_result.to_excel('DF_result_{0}.xlsx'.format(LIST_check_coin_currency[coin_No]))
DF_result.to_excel('DF_result_{0}.xlsx')


DF_result.loc[(DF_result['residual_money'] > DF_result['residual_value']), 'residual_value'] = DF_result['residual_money']
DF_1st_selected = DF_result.sort_values('residual_value', ascending=False).head(No_of_1st_target)
print ('DF_1st_selected\n', DF_1st_selected)

########## 장기간 시뮬레이션 #############

print ('\nsimul_duration : ', simul_duration[1])

DF_resul2 = pd.DataFrame(columns = ['Coin_No', 'Coin', 'simul_day', 'No_of_buy', 'No_of_N_sell', 'No_of_SC_sell', 'No_of_price_diff_sell', 'No_of_L_sell', 'average_Highest_ratio', 'average_aver_ratio_duration', 'average_L_ratio', 'std_open_value', 'Ref_value', 'residual_money', 'residual_value', \
                         'ratio_ema_mid_rise', 'successive_rise', 'ratio_ema_mid_long', 'ratio_vol_curr_prior', 'diff_m_l_factor', 'diff_vol_aver', 'under_long_duration', 'recent_vol_duration', \
                         'ratio_sell', 'add_ratio_sell', 'sell_method_vol_cri', 'ratio_diff_ema_mid', 'ratio_sell_forced'])

temp_dat2 = {'Coin_No' : [0], 'Coin' : ['name'], 'simul_day' : [0], 'No_of_buy' : [0], 'No_of_N_sell' : [0], 'No_of_SC_sell' : [0], 'No_of_price_diff_sell' : [0], 'No_of_L_sell' : [0], 'average_Highest_ratio' : [0.0], 'average_aver_ratio_duration' : [0.0], 'average_L_ratio' : [0.0], 'std_open_value' : [0.0], 'Ref_value' : [0.0], 'residual_money' : [0.0], 'residual_value' : [0.0], \
             'ratio_ema_mid_rise': [0.0], 'successive_rise': [0], 'ratio_ema_mid_long': [0.0], 'ratio_vol_curr_prior': [0.0], 'diff_m_l_factor': [0.0], 'diff_vol_aver': [0], 'under_long_duration': [0], 'recent_vol_duration': [0], \
             'ratio_sell': [0.0], 'add_ratio_sell': [0.0], 'sell_method_vol_cri': [0.0], 'ratio_diff_ema_mid': [0.0], 'ratio_sell_forced': [0.0]}

DF_immediat2 = pd.DataFrame(temp_dat2)

candle_count = int((60 / time_unit) * 24 * simul_duration[1])
DF_long = pyupbit.get_ohlcv(LIST_check_coin_currency_2[coin_No], count=candle_count, interval=candle_adapt)


DF_long['ratio_prior_to_cur'] = DF_long['open'] / DF_long['open'].shift(1)

DF_long['ema_long'] = DF_long['open'].ewm(span=ma_duration_long, adjust=False).mean()
DF_long['ema_mid'] = DF_long['open'].ewm(span=ma_duration_mid, adjust=False).mean()
DF_long['ema_short'] = DF_long['open'].ewm(span=ma_duration_short, adjust=False).mean()

DF_long['ratio_ema_long'] = DF_long['ema_long'] / DF_long['ema_long'].shift(1)

DF_long['fall_check'] = 0
DF_long.loc[(DF_long['ratio_ema_long'] < 1), 'fall_check'] = 1

DF_long['ratio_ema_mid'] = DF_long['ema_mid'] / DF_long['ema_mid'].shift(1)

DF_long['rise_check_mid'] = 0
DF_long.loc[(DF_long['ratio_ema_mid'] > 1), 'rise_check_mid'] = 1

DF_long['ratio_ema_short'] = DF_long['ema_short'] / DF_long['ema_short'].shift(1)

DF_long['rise_check_short'] = 0
DF_long.loc[(DF_long['ratio_ema_short'] > 1), 'rise_check_short'] = 1

DF_long['diff_m_l'] = DF_long['ema_mid'] - DF_long['ema_long']

DF_long['mid_under_long'] = 0
DF_long.loc[(DF_long['diff_m_l'] > 0), 'mid_under_long'] = 1

DF_long['vol_amount'] = 0.0

DF_long.loc[(DF_long['volume'] >= (2.0 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 2.0
DF_long.loc[(DF_long['volume'] < (2.0 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (1.8 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 1.8
DF_long.loc[(DF_long['volume'] < (1.8 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (1.6 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 1.6
DF_long.loc[(DF_long['volume'] < (1.6 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (1.4 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 1.4
DF_long.loc[(DF_long['volume'] < (1.4 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (1.2 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 1.2
DF_long.loc[(DF_long['volume'] < (1.2 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (1.0 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 1.0
DF_long.loc[(DF_long['volume'] < (1.0 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (0.8 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 0.8
DF_long.loc[(DF_long['volume'] < (0.8 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (0.6 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 0.6
DF_long.loc[(DF_long['volume'] < (0.6 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (0.4 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 0.4
DF_long.loc[(DF_long['volume'] < (0.4 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())) & \
            (DF_long['volume'] >= (0.2 * DF_long.sort_values('volume', ascending=False).tail(round(0.9 * len(DF_long)))['volume'].mean())), 'vol_amount'] = 0.2

DF_long['recent_vol_aver'] = 0.0

for l in range(0, len(DF_long), 1):
    DF_long['recent_vol_aver'][l] = DF_long.iloc[(l - recent_vol_duration): l]['vol_amount'].sum()

for m in range (0, len(DF_1st_selected), 1) :
    print ('{0}th candidate trial'.format(m))

    DF_test_long = DF_long.copy()

    test_money = 1000000

    #print('\n\n\n[ {0} ] Days simulation ------------------------------------'.format(i))

    # Buy / Sell logic

    DF_test_long['buy_signal'] = 0
    DF_test_long['buy_signal_flag'] = 0
    DF_test_long['sell_signal'] = 0
    DF_test_long['sell_normal'] = 0
    DF_test_long['sell_state_change'] = 0
    DF_test_long['sell_price_diff'] = 0
    DF_test_long['sell_loss'] = 0
    DF_test_long['sold_price'] = 0
    buy_price = 0
    buy_time = 0
    sell_force = 0

    for k in range(start_point + 1, len(DF_test_long), 1):
        if (DF_test_long['buy_signal_flag'][k - 1] == 0):
            if (DF_test_long['ratio_ema_long'][k - 2] > 1.0001) and (DF_test_long['ratio_ema_long'][k - 1] > 1.0001) and (DF_test_long['ratio_ema_long'][k] > 1.0001) and (DF_test_long['ratio_ema_mid'][k] > DF_1st_selected['ratio_ema_mid_rise'].values[m]) and \
                (DF_test_long.iloc[(k - (DF_1st_selected['successive_rise'].values[m] + 1)): (k + 1)]['rise_check_short'].sum() >= (DF_1st_selected['successive_rise'].values[m] - 1)) and \
                ((DF_test_long['ema_mid'][k] / DF_test_long['ema_long'][k]) > DF_1st_selected['ratio_ema_mid_long'].values[m]) and \
                (DF_test_long['volume'][k - 1] >= (DF_1st_selected['ratio_vol_curr_prior'].values[m] * DF_test_long.iloc[(k - 3):(k - 1)]['volume'].mean())) and \
                (DF_test_long.iloc[(k - under_long_duration): k]['mid_under_long'].sum() == 0) and (- DF_test_long.loc[DF_test_long.iloc[(k - under_long_duration): k]['diff_m_l'].idxmin()]['diff_m_l'] > (DF_1st_selected['diff_m_l_factor'].values[m] * DF_test_long['open'][k])) and \
                ((DF_test_long.loc[DF_test_long.iloc[(k - 5): (k - 1)]['recent_vol_aver'].idxmax()]['recent_vol_aver'] - DF_test_long['recent_vol_aver'][k - 1]) < DF_1st_selected['diff_vol_aver'].values[m]):
                DF_test_long['buy_signal'][k] = 1
                DF_test_long['buy_signal_flag'][k] = 1
                buy_price = DF_test_long['open'][k] + (buy_price_up_unit * unit_value)
                buy_time = DF_test_long.index[k]
                # print ('buy_price :', buy_price)

        # 매도 로직
        if DF_test_long['buy_signal_flag'][k - 1] == 1:
            DF_test_long['buy_signal_flag'][k] = 1
            DF_test_long['sold_price'][k] = DF_test_long['sold_price'][k - 1]

            if ((DF_test_long['volume'][k - 1] >= (DF_1st_selected['sell_method_vol_cri'].values[m] * DF_test_long.iloc[(k - 4):(k - 1)]['volume'].mean())) and (DF_test_long.iloc[(k - 9):(k + 1)]['ratio_ema_long'].mean() < DF_1st_selected['ratio_sell'].values[m])):
                DF_test_long['sell_signal'][k] = 1
                DF_test_long['buy_signal_flag'][k] = 0
                DF_test_long['sell_normal'][k] = 1
                DF_test_long['sold_price'][k] = DF_test_long['open'][k]

            elif (DF_test_long['volume'][k - 1] < (DF_1st_selected['sell_method_vol_cri'].values[m] * DF_test_long.iloc[(k - 4):(k - 1)]['volume'].mean())) and (DF_test_long['ratio_ema_long'][k] < (DF_1st_selected['ratio_sell'].values[m] + DF_1st_selected['add_ratio_sell'].values[m])):
                DF_test_long['sell_signal'][k] = 1
                DF_test_long['buy_signal_flag'][k] = 0
                DF_test_long['sell_state_change'][k] = 1
                DF_test_long['sold_price'][k] = DF_test_long['open'][k]

            elif (DF_test_long['volume'][k - 1] < (DF_1st_selected['sell_method_vol_cri'].values[m] * DF_test_long.iloc[(k - 4):(k - 1)]['volume'].mean())) and ((DF_test_long.loc[DF_test_long.iloc[(k - 5): k]['ema_mid'].idxmax()]['ema_mid'] - DF_test_long['ema_mid'][k]) > (DF_1st_selected['ratio_diff_ema_mid'].values[m] * DF_test_long['open'][k])):
                DF_test_long['sell_signal'][k] = 1
                DF_test_long['buy_signal_flag'][k] = 0
                DF_test_long['sell_price_diff'][k] = 1
                DF_test_long['sold_price'][k] = DF_test_long['open'][k]

            elif ((DF_test_long['low'][k] / buy_price) < (1 - DF_1st_selected['ratio_sell_forced'].values[m])):
                DF_test_long['sell_signal'][k] = 1
                DF_test_long['buy_signal_flag'][k] = 0
                DF_test_long['sell_loss'][k] = 1
                DF_test_long['sold_price'][k] = (buy_price * (1 - DF_1st_selected['ratio_sell_forced'].values[m]))

    DF_test_long['H_duration'] = 0
    DF_test_long['H_ratio'] = 0.0
    DF_test_long['L_duration'] = 0
    DF_test_long['L_ratio'] = 0.0
    DF_test_long['aver_ratio_duration'] = 0.0
    # DF_test_long['std'] = 0
    No_of_test_stock = 0
    transaction_No = 0

    for l in range(check_time_dur, (len(DF_test_long) - check_time_dur), 1):
        if (DF_test_long['buy_signal'][l] == 1):
            DF_test_long['H_duration'][l] = DF_test_long.loc[DF_test_long.iloc[l: (l + check_time_dur)]['high'].idxmax()]['high']
            DF_test_long['L_duration'][l] = DF_test_long.loc[DF_test_long.iloc[l: (l + check_time_dur)]['low'].idxmin()]['low']

    for o in range(check_time_dur, (len(DF_test_long) - check_time_dur), 1):
        if (DF_test_long['buy_signal'][o] == 1):
            DF_test_long['H_ratio'][o] = DF_test_long['H_duration'][o] / DF_test_long['open'][o]
            DF_test_long['L_ratio'][o] = DF_test_long['L_duration'][o] / DF_test_long['open'][o]
            DF_test_long['aver_ratio_duration'][o] = DF_test_long.iloc[(o + 1): ((o + 1) + check_time_dur)]['ratio_prior_to_cur'].sum() / check_time_dur

    No_of_test_stock = 0
    transaction_No = 0

    for n in range(0, len(DF_test_long), 1):
        if DF_test_long['buy_signal'][n] == 1:
            transaction_No = transaction_No + 1
            No_of_test_stock = (test_money / (DF_test_long['open'][n] + (buy_price_up_unit * unit_value))) * (1 - transaction_fee_ratio)
            test_money = test_money - ((DF_test_long['open'][n] + (buy_price_up_unit * unit_value)) * No_of_test_stock)
            #print('\n[transaction_BUY] {0}  transaction_No : {1}  / residual_money : {2:,}  / No_of_stock : {3}'.format(DF_test_long.index[n], transaction_No, test_money, No_of_test_stock))


        elif DF_test_long['sell_signal'][n] == 1:
            if DF_test_long['sell_normal'][n] == 1:
                test_money = test_money + (((DF_test_long['sold_price'][n] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                No_of_test_stock = 0
                #print('[transaction_SELL_Normal] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test_long.index[n], transaction_No, DF_test['sell_normal'][n], DF_test['sell_state_change'][n], DF_test['sell_price_diff'][n], DF_test['sell_loss'][n], test_money, No_of_test_stock))

            elif DF_test_long['sell_state_change'][n] == 1:
                test_money = test_money + (((DF_test_long['open'][n] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                No_of_test_stock = 0
                #print('[transaction_SELL_state_change] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test_long.index[n], transaction_No, DF_test['sell_normal'][n], DF_test['sell_state_change'][n], DF_test['sell_price_diff'][n], DF_test['sell_loss'][n], test_money, No_of_test_stock))

            elif DF_test_long['sell_price_diff'][n] == 1:
                test_money = test_money + (((DF_test_long['open'][n] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                No_of_test_stock = 0
                #print('[sell_price_diff] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test_long.index[n], transaction_No, DF_test['sell_normal'][n], DF_test['sell_state_change'][n], DF_test['sell_price_diff'][n], DF_test['sell_loss'][n], test_money, No_of_test_stock))

            elif DF_test_long['sell_loss'][n] == 1:
                test_money = test_money + (((DF_test_long['sold_price'][n] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                No_of_test_stock = 0
                #print('[transaction_SELL_Loss] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test_long.index[n], transaction_No, DF_test['sell_normal'][n], DF_test['sell_state_change'][n], DF_test['sell_price_diff'][n], DF_test['sell_loss'][n], test_money, No_of_test_stock))

    DF_bought = DF_test_long[DF_test_long['buy_signal'] == 1]
    #print('[Final result] \nNo. of transaction : {0}  / resisual money : {1:,}  / residual stocks : {2} / ref_value__stock price x stocks : {3:,}'.format(transaction_No, test_money, No_of_test_stock, (DF_test['open'][-1] * No_of_test_stock)))
    #print('\nNo. of normal selling : {0}  / state_change selling : {1}  /  price_diff_selling : {2}'.format(DF_test_long['sell_normal'].sum(), DF_test_long['sell_state_change'].sum(), DF_test['sell_price_diff'].sum()))
    #print('\n[Simul_Result]\nNo_of_buy : {0}  /  average_H_ratio : {1}  / average_aver_ratio_duration : {2}  / average_L_ratio : {3}'.format(len(DF_bought), DF_bought['H_ratio'].mean(), DF_bought['aver_ratio_duration'].mean()))

    #DF_test_long.to_excel('DF_test_long_{0}_{1}_days.xlsx'.format(LIST_check_coin_currency[coin_No], i))

    DF_immediat2['Coin_No'] = coin_No
    DF_immediat2['Coin'] = LIST_check_coin_currency_2[coin_No]
    DF_immediat2['simul_day'] = simul_duration[1]
    DF_immediat2['No_of_buy'] = DF_test_long['buy_signal'].sum()
    DF_immediat2['No_of_N_sell'] = DF_test_long['sell_normal'].sum()
    DF_immediat2['No_of_SC_sell'] = DF_test_long['sell_state_change'].sum()
    DF_immediat2['No_of_price_diff_sell'] = DF_test_long['sell_price_diff'].sum()
    DF_immediat2['No_of_L_sell'] = DF_test_long['sell_loss'].sum()
    DF_immediat2['average_Highest_ratio'] = DF_bought['H_ratio'].mean()
    DF_immediat2['average_aver_ratio_duration'] = DF_bought['aver_ratio_duration'].mean()
    DF_immediat2['average_L_ratio'] = DF_bought['L_ratio'].mean()
    DF_immediat2['std_open_value'] = DF_test_long['open'].std()
    DF_immediat2['Ref_value'] = (DF_bought['H_ratio'].mean() * DF_bought['aver_ratio_duration'].mean() * DF_bought['L_ratio'].mean())
    DF_immediat2['residual_money'] = test_money
    DF_immediat2['residual_value'] = (DF_test_long['open'][-1] * No_of_test_stock)
    DF_immediat2['ratio_ema_mid_rise'] = DF_1st_selected['ratio_ema_mid_rise'].values[m]
    DF_immediat2['successive_rise'] = DF_1st_selected['successive_rise'].values[m]
    DF_immediat2['ratio_ema_mid_long'] = DF_1st_selected['ratio_ema_mid_long'].values[m]
    DF_immediat2['ratio_vol_curr_prior'] = DF_1st_selected['ratio_vol_curr_prior'].values[m]
    DF_immediat2['diff_m_l_factor'] = DF_1st_selected['diff_m_l_factor'].values[m]
    DF_immediat2['diff_vol_aver'] = DF_1st_selected['diff_vol_aver'].values[m]
    DF_immediat2['under_long_duration'] = under_long_duration
    DF_immediat2['recent_vol_duration'] = recent_vol_duration
    DF_immediat2['ratio_sell'] = DF_1st_selected['ratio_sell'].values[m]
    DF_immediat2['add_ratio_sell'] = DF_1st_selected['add_ratio_sell'].values[m]
    DF_immediat2['sell_method_vol_cri'] = DF_1st_selected['sell_method_vol_cri'].values[m]
    DF_immediat2['ratio_diff_ema_mid'] = DF_1st_selected['ratio_diff_ema_mid'].values[m]
    DF_immediat2['ratio_sell_forced'] = DF_1st_selected['ratio_sell_forced'].values[m]

    DF_resul2 = pd.concat([DF_resul2, DF_immediat2], axis=0)


DF_resul2.loc[(DF_resul2['residual_money'] > DF_resul2['residual_value']), 'residual_value'] = DF_resul2['residual_money']

print (DF_resul2.sort_values('residual_value', ascending=False).head(10))


DF_resul2.to_excel('DF_resul2_{0}.xlsx'.format(LIST_check_coin_currency[coin_No]))



