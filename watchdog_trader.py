from tqsdk import TqApi, TqAuth, TqAccount, TargetPosTask
import ast
import re
import threading
import time
import hashlib
import json


file_path = "target_position.json"
api = TqApi(TqAccount("D东海期货", "5200979", "heyisheng99"), auth=TqAuth("heyisheng99", "heyisheng99"))      # 创建 TqApi 实例, 指定
#api = TqApi(web_gui=True,auth=TqAuth("heyisheng99", "heyisheng99"))   #模拟盘


# 需要解决已有仓位的问题
def get_contract_pos(SYMBOL):
    pass

def send_order(data):
    try:
        if(data):
            for item in data:
                try:
                    print(item)
                    quote = api.get_quote(item) #读取连续合约行情
                    #print(quote)
                    ask1 = quote['ask_price1']
                    bid1 = quote['bid_price1']
                    print(ask1,bid1)
                    SYMBOL=quote.underlying_symbol #读取主力合约
                    target_lots = int(data[item])
                    print('SYMBOL:',SYMBOL, ' volume:',target_lots)

                    #t_1 = TargetPosTask(api,SYMBOL)
                    #t_1.set_target_volume(lots)   #set_target_volume 只会执行一次
                    # 读取当前持仓数量
                    position_data = api.get_position(SYMBOL)
                    long_position = position_data['volume_long']
                    short_position = position_data['volume_short']
                    #print(SYMBOL,' volume_long:',long_position)
                    #print(SYMBOL,' volume_short:',short_position)
                    # 交易净头寸
                    if(long_position*short_position>0):
                        print("有对锁单")
                        cover_lots = min(long_position,short_position)
                        api.insert_order(symbol=SYMBOL, direction="BUY", offset="CLOSE", volume=cover_lots,limit_price = ask1)
                        api.insert_order(symbol=SYMBOL, direction="SELL", offset="CLOSE", volume=cover_lots,limit_price = bid1)
                    else:
                        print("无对锁单")
                    
                    #下单分：加仓、减仓、反向
                    #order to target
                    net_pos = long_position - short_position
                    lots = target_lots - net_pos
                    if(target_lots*net_pos>0):  #同方向单子
                        if(target_lots>0 and target_lots>net_pos): #加多
                            api.insert_order(symbol=SYMBOL, direction="BUY", offset="OPEN", volume=lots,limit_price = ask1)
                        if(target_lots<0 and target_lots<net_pos): #加空
                            api.insert_order(symbol=SYMBOL, direction="SELL", offset="OPEN", volume=-lots,limit_price = bid1)
                        if(target_lots>0 and target_lots<net_pos): #平多
                            api.insert_order(symbol=SYMBOL, direction="SELL", offset="CLOSE", volume=-lots,limit_price = bid1)
                        if(target_lots<0 and target_lots>net_pos): #平空
                            api.insert_order(symbol=SYMBOL, direction="BUY", offset="CLOSE", volume=lots,limit_price = ask1)
                    if(target_lots*net_pos<0): 
                        if(net_pos>0): #平多开空
                            api.insert_order(symbol=SYMBOL, direction="SELL", offset="CLOSE", volume=net_pos,limit_price = bid1)
                            api.insert_order(symbol=SYMBOL, direction="SELL", offset="OPEN", volume=-target_lots,limit_price = bid1)
                        if(net_pos<0): #平空开多
                            api.insert_order(symbol=SYMBOL, direction="BUY", offset="CLOSE", volume=-net_pos,limit_price = ask1)
                            api.insert_order(symbol=SYMBOL, direction="BUY", offset="OPEN", volume=target_lots,limit_price =ask1)    
                    if(net_pos==0):
                        if(target_lots>0):
                            api.insert_order(symbol=SYMBOL, direction="BUY", offset="OPEN", volume=target_lots,limit_price =ask1)
                        if(target_lots<0):
                            api.insert_order(symbol=SYMBOL, direction="SELL", offset="OPEN", volume=-target_lots,limit_price =bid1)
                    if(target_lots ==0):
                        if(net_pos>0):
                            api.insert_order(symbol=SYMBOL, direction="SELL", offset="CLOSE", volume=net_pos,limit_price = bid1)
                        if(net_pos<0):
                            api.insert_order(symbol=SYMBOL, direction="BUY", offset="CLOSE", volume=-net_pos,limit_price = ask1)
                    api.wait_update() #等待执行结束
                    position_data = api.get_position(SYMBOL)
                    long_position = position_data['volume_long']
                    short_position = position_data['volume_short']
                    #print(position_data)
                    print(SYMBOL,' volume_long:',long_position)
                    print(SYMBOL,' volume_short:',short_position)
                    api.wait_update()
                except:
                    print(SYMBOL,' send order failed.')
    except:
        print('send order failed')
        
        
def get_file_hash(file_path):
    """
    计算文件的哈希值
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


'''
def excute_order(t_1,lots):
    order_times = 0
    while True:
        api.wait_update()
        if(order_times<1):
            try:
                t_1.set_target_volume(lots)
                print('order excuted.')
            except:
                print('order failed')
            order_times += 1
'''

def load_and_process_data():
    """
    加载并处理文件数据的逻辑
    """
    data={}
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            # 进行你的处理（比如打印数据）
        print("Data loaded:", data)
        print('Tradeing Started.')
        thread = threading.Thread(target=send_order, args=(data,))
        thread.start()
        #send_order(data)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file {file_path}.")
        
def monitor_file_changes(file_path):
    """
    监控文件内容变化
    """
    #current_hash = get_file_hash(file_path)
    current_hash = ''
    while True:
        new_hash = get_file_hash(file_path)
        if new_hash != current_hash:
            print(f"{file_path} content has changed. Reloading data...")
            current_hash = new_hash
            load_and_process_data()
        time.sleep(3)  # 轮询间隔，可以根据实际需求调整
if __name__ == "__main__":
    # 初始加载数据
    #load_and_process_data()
    #time.sleep(3)
    monitor_file_changes(file_path)


'''
api = TqApi(TqAccount("D东海期货", "5200979", "heyisheng99"), auth=TqAuth("heyisheng99", "heyisheng99"))    # 创建 TqApi 实例, 指定交易账户

q_1 = api.get_quote("SHFE.rb2405")                         # 订阅近月合约行情
t_1 = TargetPosTask(api, "SHFE.rb2405")
#t_1.set_target_volume(0)
account = api.get_account()
print(account.balance)
#api.insert_order(symbol="SHFE.rb2401", direction="BUY", offset="OPEN", volume=1,limit_price = 3920)


order_times=0
position = api.get_position()
print(position)

while True:
	api.wait_update()
	if(order_times<1):
		try:
			#api.insert_order(symbol="SHFE.rb2405", direction="BUY", offset="OPEN", volume=1,limit_price = 3920)
			#api.cancel_order('PYSDK_insert_870398fe841b2c2624276efddb8cbf6d')
			api.cancel_order('OTG.5.25186e0f.1')
		except:
			print('order failed')
		order_times += 1
		
'''


