# 导入函数库
from __future__ import division      #除数可以显示为float
import jqdata               #导入聚宽函数库
from six import StringIO    #使用聚宽readfile函数

import numpy as np
import pandas as pd

from datetime import timedelta,date,datetime

import random

import talib

# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    log.set_level('order', 'error')
    
    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）

    # 开盘前运行

    # 打印数据，供分析使用
    # 打印当天的成交记录，并呈现胜率情况
    run_daily(after_market_log_print, time='after_close', reference_security='000300.XSHG')
    

    # 生成购买股票列表
    run_weekly(after_market_close,1,time='after_close', reference_security='000300.XSHG')
    # 每天开始买卖
    run_weekly(rebalance,2, time='09:45', reference_security='000300.XSHG') 
    # 每月更新列表
    run_weekly(Update_Pairs,2, time='9:40', reference_security='000300.XSHG') 



    # 生成购买股票列表
    run_weekly(after_market_close,2,time='after_close', reference_security='000300.XSHG')
    # 每天开始买卖
    run_weekly(rebalance,3, time='09:45', reference_security='000300.XSHG') 
    # 每月更新列表
    run_weekly(Update_Pairs,3, time='9:40', reference_security='000300.XSHG') 

    # 生成购买股票列表
    run_weekly(after_market_close,3,time='after_close', reference_security='000300.XSHG')
    # 每天开始买卖
    run_weekly(rebalance,4, time='09:45', reference_security='000300.XSHG') 
    # 每月更新列表
    run_weekly(Update_Pairs,4, time='9:40', reference_security='000300.XSHG') 



    # 生成购买股票列表
    run_weekly(after_market_close,4,time='after_close', reference_security='000300.XSHG')
    # 每天开始买卖
    run_weekly(rebalance,5, time='09:45', reference_security='000300.XSHG') 
    # 每月更新列表
    run_weekly(Update_Pairs,5, time='9:40', reference_security='000300.XSHG') 

    # 用于控制买入，买入成功后更新g.stock_list
    g.buy_list = []
    g.sell_list = []

    # 统计胜率的参数
    g.wins = 0
    g.loses = 0
    g.evens = 0
    
    body = read_file("pairs_beta_config.csv")
    g.pairs_info = pd.read_csv(StringIO(body),index_col=0)

    
# 打印当天的成交记录，并呈现胜率情况
def after_market_log_print(context):
    #得到当天所有成交记录
    i = 1
    for sec in context.portfolio.positions.keys():
        log.info('$$%d、 持仓：%s，持仓天数：%d，盈亏情况： %f，总价值：%f' %(i, \
                str(context.portfolio.positions[sec].security), \
                int((context.current_dt - context.portfolio.positions[sec].init_time).days), \
                float((context.portfolio.positions[sec].price - context.portfolio.positions[sec].avg_cost)/context.portfolio.positions[sec].avg_cost), \
                float(context.portfolio.positions[sec].value) 
                ))
        i += 1

    log.info('$$当日订单信息')
    orders = get_orders()
    for _order in orders.values():
        
        if _order.action == "open":
            log.info("当天买入，股票%s，价格：%f"%(str(_order.security),float(_order.price)))

        if _order.action == "close":
            log.info("当天卖出，股票%s，价格：%f，收益率为："%(str(_order.security),float(_order.price)))

    
    # # 整体持仓情况
    # log.info("$$持仓总价值：%f，持仓价值%f"%(float(context.portfolio.total_value),float(context.portfolio.positions_value)))

    # # 统计整体回测的胜率结果
    # log.info("$$胜败结果为：")
    # log.info("1、获胜次数：%d"%int(g.wins))
    # log.info("2、失败次数：%d"%int(g.loses))
    # log.info("3、平局次数：%d"%int(g.evens))
    # log.info("4、整体胜率：%f"%float(((g.wins)/( g.wins + g.evens + g.loses))) if (g.wins + g.evens +  g.loses) != 0 else 0)

    # log.info('一天结束')
    # log.info('##############################################################')


## 收盘后运行函数  
# 生成
def after_market_close(context):
    # 生成购买股票列表
    
    g.buy_list = []
    g.sell_list = []
    try:
        g.buy_list ,g.sell_list  = get_balance_list(context)
    except:
        g.buy_list = []
        g.sell_list = []
    
    log.info("$$生成次日购买股票列表")
    i = 1
    for sec in g.buy_list:
        log.info("%d、次日购买股票列表%s"%(int(i),str(sec)))        
        i += 1
    
    log.info("$$生成次日卖出股票列表")
    i = 1
    for sec in g.sell_list:
        log.info("%d、次日卖出股票列表%s"%(int(i),str(sec)))        
        i += 1





def rebalance(context):
    if len(g.sell_list) != 0:
        for sec in g.sell_list:
            log.info("$$卖出股票：%s"%(str(sec)))
            order_target_value(sec, 0)
    
    # 按照买入股票列表下单
    if len(g.buy_list) != 0:
        Operate_list = set(g.buy_list) - set(context.portfolio.positions.keys())
        for sec in Operate_list:
            log.info("$$买入股票：%s"%(str(sec)))
            order_target_value(sec,  context.portfolio.total_value/20)

    
####################################################     开始重写代码部分     #################################################


# 获取需要操作的股票列表
def get_balance_list(context):

    sell_list = []
    buy_list = []
        
    day_count = 200
    end_date =  context.current_dt.strftime('%Y-%m-%d')
    
    # 存储股票的价格原始数据
    for i in range(0,g.pairs_info.shape[0]):
        s1 = g.pairs_info.iloc[i,:]['p1']
        s2 = g.pairs_info.iloc[i,:]['p2']
        stocks = [s1,s2]
        
        df_stocks = pd.DataFrame()
    
        # 开始获取收盘价信息，按列进行
        for stock_name in stocks:
            stock_price = get_price(stock_name, count = day_count, end_date=end_date, frequency='daily', fields='close',fq = "pre")
            stock_price_pd = pd.DataFrame(data = np.array(stock_price['close']),columns = [stock_name])
            df_stocks = pd.concat([df_stocks,stock_price_pd],axis = 1)
            
        df_stocks['residual'] = df_stocks[s2] - g.pairs_info.iloc[i,:]['beta']*df_stocks[s1] - g.pairs_info.iloc[i,:]['alpha']
        
        # 计算z_score
        df_stocks['z_score'] = None 
        df_stocks['z_score'] = pd.rolling_mean(df_stocks['residual'], 2)/pd.rolling_std(df_stocks['residual'], 90)
    
        # 开始判断加入买卖列表
        if df_stocks.iloc[-1,:]['z_score'] < -1:
            buy_list.append(s2)
        # elif df_stocks.iloc[-1,:]['z_score'] > 0.5:
        #     buy_list.append(s1)
    
        # 开始判断加入买卖列表
        if df_stocks.iloc[-1,:]['z_score'] > 0:
            sell_list.append(s2)

        # elif df_stocks.iloc[-1,:]['z_score'] < -0:
        #     sell_list.append(s1)

    return buy_list,sell_list

def Update_Pairs(context):

    body = read_file("pairs_beta_config.csv")

    read_pairs_pd = pd.read_csv(StringIO(body),index_col=0)
    # 如果行数不一致，说明数据有更新，重新赋值，并且清仓
    if g.pairs_info.shape[0] != read_pairs_pd.shape[0]:
        g.pairs_info = read_pairs_pd
        
        for sec in context.portfolio.positions.keys():
            log.info("$$配对信息更新，清仓股票：%s"%(str(sec)))
            order_target_value(sec, 0)
        
