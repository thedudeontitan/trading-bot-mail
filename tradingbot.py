import MetaTrader5 as mt5
from datetime import datetime

account = int()
password=""
server=""

def connect(account,password,server):
    account = int(account)
    mt5.initialize()
    authorized=mt5.login(account,password,server)

    if authorized:
        print("Connected: Connecting to MT5 Client")
    else:
        print("Failed to connect at account #{}, error code: {}"
              .format(account, mt5.last_error()))

def openPosition(pair, order_type, tp ,sl):
    symbol_info = mt5.symbol_info(pair)
    filling_mode = mt5.symbol_info(pair).filling_mode-1
    if symbol_info is None:
        print(pair, "not found")
        return

    if not symbol_info.visible:
        print(pair, "is not visible, trying to switch on")
        if not mt5.symbol_select(pair, True):
            print("symbol_select({}}) failed, exit",pair)
            return
    print(pair, "found!")

    point = symbol_info.point
    
    if(order_type == "BUY"):
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pair).ask
            
    if(order_type == "SELL"):
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(pair).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pair,
        "volume": 0.90,
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": 234000,
        "comment": "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to send order :({mt5.last_error}")
    else:
        print ("Order successfully placed!")


connect(account,password,server)

