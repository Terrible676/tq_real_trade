from tqsdk import TqApi, TqAuth, TqAccount, TargetPosTask
import ast
import re
from time import sleep
from datetime import datetime

api = TqApi(TqAccount("D东海期货", "5200979", "heyisheng99"), auth=TqAuth("heyisheng99", "heyisheng99"))      # 创建 TqApi 实例, 指定交易账户


def get_order_alive(order):
    if(not order):
        return ''
    data_string = str(order)
    matches = re.findall(r"D\({.*?}\)", data_string)
    # 提取每个匹配项中的 "status" 值为 "ALIVE" 的数据
    alive_data = []
    for match in matches:
        status_match = re.search(r"'status': 'ALIVE'", match)
        if status_match:
            alive_data.append(match)
    for data in alive_data:
        print("提取到的 status: ALIVE 数据:", data)
    alive_order_ids = []
    for match in alive_data:
        order_id_match = re.search(r"'order_id': '(.*?)'", match)
        if order_id_match:
            order_id = order_id_match.group(1)
            alive_order_ids.append(order_id)
    return alive_order_ids



account = api.get_account()
order = api.get_order()
while True:
    now = datetime.now()
    alive_order_ids = get_order_alive(order)
    print(now,'alive order:',alive_order_ids)
    sleep(2)
    
    

