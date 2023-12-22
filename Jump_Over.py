import pandas as pd
from tqsdk import TqApi, TqAuth, TqSim, TargetPosTask
from tqsdk.tafunc import ma
import datetime
from tqsdk import TqAccount
import threading
import time
from tqsdk.algorithm import Twap
from tqsdk.ta import ATR
#from tqsdk.risk_rule import TqRuleAccOpenVolumesLimit
import asyncio
import websockets
import json
import fcntl


# to do list:
# 换月问题
# 

def write_target(SYMBOL, lots=1):
    file_path = "target_position.json"
    data = {}
    # 使用文件锁
    with open(file_path, "r+") as json_file:
        try:
            fcntl.flock(json_file, fcntl.LOCK_EX)  # 获取锁
            data = json.load(json_file)
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file {file_path}.")
        
        data[SYMBOL] = lots
        
        # 将文件指针移到文件开头，以便写入数据
        json_file.seek(0)
        json_file.truncate()
        json.dump(data, json_file)
        fcntl.flock(json_file, fcntl.LOCK_UN)  # 释放锁

'''
def write_target(SYMBOL,lots=1):
    file_path = "target_position.json"
    data = {}
    try:
        # 尝试打开 JSON 文件
        with open(file_path, "r") as json_file:
            if(json_file):
                data = json.load(json_file)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file {file_path}.")
    data[SYMBOL]=lots
    with open("target_position.json", "w") as json_file:
        json.dump(data, json_file)
'''
def strategy_jump_over(CONTRACT,PERIOD,api,lots=1):
    try:
        print("initializing jump over....")
        quote = api.get_quote(CONTRACT)
        account = api.get_account()
        #print(quote)
        SYMBOL=quote.underlying_symbol
        print(SYMBOL)
        data_length = 200
        klines = api.get_kline_serial(SYMBOL, duration_seconds=PERIOD, data_length=data_length)
        virtual_position = 0  # 记录当前策略的持仓
        TradedThisBar = False # 记录当前Bar是否有过交易、每个Bar只交易一次
        k_num = 0
        try:
            print(str(SYMBOL))
        except:
            print('custom print error.')
        while True:
            if (k_num == 0): #初始化运行程序时先运行一次仓位
                pass
            else:
                api.wait_update()
            try:
                if(k_num == 0 or api.is_changing(klines.iloc[-1], "datetime")): #实盘监控
                    klines.dropna()
                    TradedThisBar = False #
                    print('kline started.')
                    for i in range(len(klines)):
                        if(k_num > 0 and i<(len(klines)-1)): # 开始监听行情时，只运行最后一根k线
                            continue
                        try:
                            open0 = klines.open.iloc[i+1]
                            close1 = klines.close.iloc[i]
                            JumpRatio = (open0/close1-1)*100
                            #print(JumpRatio)
                            if(virtual_position!=1 and JumpRatio>0.7):
                                print(SYMBOL,' JumpUp')
                                write_target(CONTRACT,lots)
                                virtual_position = 1
                            if(virtual_position!=-1 and JumpRatio<-0.7):
                                write_target(CONTRACT,-lots)
                                print(SYMBOL,' JumpDown')
                                virtual_position = -1
                        except:
                            continue
                    k_num += 1
                    print('waiting next bar..')
            except:
                print("data process failed.")
                continue
    
    except:
        print(CONTRACT," Jump Over start failed.")


def strategy_ma_single(CONTRACT,PERIOD,api,lots=1):
    try:
        print("initializing jump over....")
        quote = api.get_quote(CONTRACT)
        account = api.get_account()
        #print(quote)
        SYMBOL=quote.underlying_symbol
        print(SYMBOL)
        data_length = 500
        klines = api.get_kline_serial(SYMBOL, duration_seconds=PERIOD, data_length=data_length)
        virtual_position = 0  # 记录当前策略的持仓
        TradedThisBar = False # 记录当前Bar是否有过交易、每个Bar只交易一次
        k_num = 0
        try:
            print(str(SYMBOL))
        except:
            print('custom print error.')
        while True:
            if (k_num == 0): #初始化运行程序时先运行一次仓位
                pass
            else:
                api.wait_update()
            try:
                if(k_num == 0 or api.is_changing(klines.iloc[-1], "datetime")): #实盘监控
                    klines.dropna()
                    TradedThisBar = False #
                    print('kline started.')
                    for i in range(len(klines)):
                        if(k_num > 0 and i<(len(klines)-1)): # 开始监听行情时，只运行最后一根k线
                            continue
                        if i<200:
                            continue
                        if i == 300:
                            print(klines)
                        try:
                            ma158h = (klines.high.iloc[i-158:i]).mean()
                            ma158l = (klines.low.iloc[i-158:i]).mean()
                            cp = klines.close.iloc[i]
                            condition1 = cp>ma158h
                            condition2 = cp<ma158l
                            
                            #print(JumpRatio)
                            if(virtual_position!=1 and condition1):
                                trade_time = klines.datetime.iloc[i]
                                print(trade_time,' ',SYMBOL,' MA LONG')
                                write_target(CONTRACT,lots)
                                virtual_position = 1
                            if(virtual_position!=-1 and condition2):
                                trade_time = klines.datetime.iloc[i]
                                print(trade_time,' ',SYMBOL," MA SHORT")
                                write_target(CONTRACT,-lots)
                                virtual_position = -1
                        except:
                            continue
                    k_num += 1
                    print('waiting next bar..')
            except:
                print("data process failed.")
                continue
    
    except:
        print(CONTRACT," MA single start failed.")




def main():
    file_path = "target_position.json" #创建一个文件
    with open(file_path, "w"):
        pass
    api={}
    period = 3600 #3600为小时线
    #contract_list = ['KQ.m@DCE.eb','KQ.m@CZCE.TA','KQ.m@SHFE.rb','KQ.m@DCE.i','KQ.m@DCE.eg','KQ.m@CFFEX.IF']
    #contract_list = ['KQ.m@INE.sc']
    #contract_list = ['KQ.m@SHFE.rb']
    contract1 = 'KQ.m@INE.sc'
    contract2= 'KQ.m@SHFE.rb'
    api[contract1]=TqApi(TqAccount("D东海期货", "5200979", "heyisheng99"), auth=TqAuth("heyisheng99", "heyisheng99"))
    api[contract2]=TqApi(TqAccount("D东海期货", "5200979", "heyisheng99"), auth=TqAuth("heyisheng99", "heyisheng99")) 
    thread1 =  threading.Thread(target=strategy_jump_over,args= (contract1, period,api[contract1], 1))
    thread2 = threading.Thread(target=strategy_ma_single,args= (contract2, period,api[contract2], 1))
    
    #thread1.start()
    thread2.start()
    '''
    for contract in contract_list:
        try:
            api[contract]=TqApi(TqAccount("D东海期货", "5200979", "heyisheng99"), auth=TqAuth("heyisheng99", "heyisheng99")) 
            thread =  threading.Thread(target=strategy_jump_over,args=(contract, period, api[contract]))
            thread.start()
            print("thread ",contract,' started.')
        except:
            print("thread ",contract,' starting failed.')
    '''
if __name__ == "__main__":
    main()
    
    
    
