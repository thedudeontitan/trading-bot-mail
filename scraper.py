import sys
import os
import re
from collections import OrderedDict
from tradingbot import openPosition,connect

def scrapedata(txt):
    
    orders=[]
    symbol_lst = re.findall(r"<span style=\"font-size:24[\.0]*pt;color:red\">([A-Z ()]+)</span>", txt)
    type_lst= re.findall(r"(Buy Dip|Sell Rally)",txt)
    for i in range(len(list(type_lst))):
        if type_lst[i] =="Buy Dip":
            type_lst[i]=("BUY")
        elif type_lst[i] =="Sell Rally":
            type_lst[i]=("SELL")
    stopLoss_lst = re.findall(r"<br>[Buy Dip\|Sell Rally]*: [0-9\. ]+[<br>]*Stop: ([0-9.]+)<br>",txt)
    targetPrice_lst = re.findall(r"[Buy Dip\|Sell Rally]*: [0-9\. ]+[<br>]*Stop: [0-9.]+[<br>]+Target 1: ([0-9.]+)", txt)
    for i in range(len(symbol_lst)):
        
        order = OrderedDict()
        order["symbol"]=symbol_lst[i]
        order["type"]= type_lst[i]
        order["stopLoss"]= float(stopLoss_lst[i])
        order["targetPrice"]= float(targetPrice_lst[i])
        orders.append(order)
        openPosition(order["symbol"],order["type"],order["targetPrice"],order["stopLoss"])
    return orders