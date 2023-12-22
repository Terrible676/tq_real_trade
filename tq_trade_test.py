from tqsdk import TqApi, TqAuth, TqAccount, TargetPosTask
import ast
import re
api = TqApi(TqAccount("D东海期货", "5200979", "heyisheng99"), auth=TqAuth("heyisheng99", "heyisheng99"))      # 创建 TqApi 实例, 指定交易账户


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










# 监控订单情况
'''
order = api.insert_order(symbol="DCE.m2105", direction="BUY", offset="OPEN", volume=5, limit_price=2750)

while True:
    api.wait_update()
    if api.is_changing(order, ["status", "volume_orign", "volume_left"]):
        print("单状态: %s, 已成交: %d 手" % (order.status, order.volume_orign - order.volume_left))
    if api.is_changing(position, "pos_long_today"):
        print("今多头: %d 手" % (position.pos_long_today))
    if api.is_changing(account, "available"):
        print("可用资金: %.2f" % (account.available))



api.get_order()
api.get_trade()

'order_id': 'PYSDK_insert_870398fe841b2c2624276efddb8cbf6d'
'PYSDK_insert_870398fe841b2c2624276efddb8cbf6d'
<tqsdk.objs.Order object at 0x7f27817ad090>

'{'order_id': 'PYSDK_insert_870398fe841b2c2624276efddb8cbf6d', 'exchange_order_id': '    42616934', 'exchange_id': 'SHFE', 'instrument_id': 'rb2401', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 1, 'limit_price': 3920.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1701914399000000000, 'last_msg': '未成交', 'status': 'ALIVE', 'is_dead': False, 'is_online': True, 'is_error': False, 'trade_price': nan, 'seqno': 8, 'user_id': '5200979', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}'
'''



'''
klines = api.get_kline_serial("SHFE.rb2405", 10)
while True:
    # 通过wait_update刷新数据
    api.wait_update()
'''


'''
t_1910 = TargetPosTask(api, "SHFE.rb1910")                    # 创建近月合约调仓工具
q_2001 = api.get_quote("SHFE.rb2001")                         # 订阅远月合约行情
t_2001 = TargetPosTask(api, "SHFE.rb2001")                    # 创建远月合约调仓工具

while True:
  api.wait_update()                                           # 等待数据更新
  spread = q_1910.last_price - q_2001.last_price        # 计算近月合约-远月合约价差
  print("当前价差:", spread)
  if spread > 250:
    print("价差过高: 空近月，多远月")
    t_1910.set_target_volume(-1)                              # 要求把1910合约调整为空头1手
    t_2001.set_target_volume(1)                               # 要求把2001合约调整为多头1手
  elif spread < 200:
    print("价差回复: 清空持仓")                               # 要求把 1910 和 2001合约都调整为不持仓
    t_1910.set_target_volume(0)
    t_2001.set_target_volume(0)
'''


'''
<tqsdk.entity.Entity object at 0x7f78bec3e350>, 
D(
	{
	'SHFE.rb2401': <tqsdk.objs.Position object at 0x7f78bec3dd90>, 
		D(
			{
			'exchange_id': 'SHFE', 'instrument_id': 'rb2401', 'pos_long_his': 0, 'pos_long_today': 0, 'pos_short_his': 0, 'pos_short_today': 1, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 1, 'volume_short_his': 0, 'volume_short': 1, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': nan, 'open_price_short': 3908.000000000001, 'open_cost_long': nan, 'open_cost_short': 39080.00000000001, 'position_price_long': nan, 'position_price_short': 3908.000000000001, 'position_cost_long': nan, 'position_cost_short': 39080.00000000001, 'float_profit_long': nan, 'float_profit_short': -59.999999999992724, 'float_profit': -59.999999999992724, 'position_profit_long': nan, 'position_profit_short': -59.999999999992724, 'position_profit': -59.999999999992724, 'margin_long': nan, 'margin_short': 5862.0, 'margin': 5862.0, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': -1, 'pos_long': 0, 'pos_short': 1, 'user_id': '5200979', 'volume_long_yd': 0, 'volume_short_yd': 0, 'last_price': 3914.0
			}
		)
	}
)
>>> type(position)

'''
















