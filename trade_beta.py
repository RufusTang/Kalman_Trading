# ���뺯����
from __future__ import division      #����������ʾΪfloat
import jqdata               #����ۿ�����
from six import StringIO    #ʹ�þۿ�readfile����

import numpy as np
import pandas as pd

from datetime import timedelta,date,datetime

import random

import talib

# ��ʼ���������趨��׼�ȵ�
def initialize(context):
    # �趨����300��Ϊ��׼
    set_benchmark('000300.XSHG')
    # ������̬��Ȩģʽ(��ʵ�۸�)
    set_option('use_real_price', True)
    # ������ݵ���־ log.info()
    log.info('��ʼ������ʼ������ȫ��ֻ����һ��')
    # ���˵�orderϵ��API�����ı�error����͵�log
    log.set_level('order', 'error')
    
    ### ��Ʊ����趨 ###
    # ��Ʊ��ÿ�ʽ���ʱ���������ǣ�����ʱӶ�����֮��������ʱӶ�����֮����ǧ��֮һӡ��˰, ÿ�ʽ���Ӷ����Ϳ�5��Ǯ
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    ## ���к�����reference_securityΪ����ʱ��Ĳο���ģ�����ı��ֻ���������֣���˴���'000300.XSHG'��'510300.XSHG'��һ���ģ�

    # ����ǰ����

    # ��ӡ���ݣ�������ʹ��
    # ��ӡ����ĳɽ���¼��������ʤ�����
    run_daily(after_market_log_print, time='after_close', reference_security='000300.XSHG')
    

    # ���ɹ����Ʊ�б�
    run_weekly(after_market_close,1,time='after_close', reference_security='000300.XSHG')
    # ÿ�쿪ʼ����
    run_weekly(rebalance,2, time='09:45', reference_security='000300.XSHG') 
    # ÿ�¸����б�
    run_weekly(Update_Pairs,2, time='9:40', reference_security='000300.XSHG') 



    # ���ɹ����Ʊ�б�
    run_weekly(after_market_close,2,time='after_close', reference_security='000300.XSHG')
    # ÿ�쿪ʼ����
    run_weekly(rebalance,3, time='09:45', reference_security='000300.XSHG') 
    # ÿ�¸����б�
    run_weekly(Update_Pairs,3, time='9:40', reference_security='000300.XSHG') 

    # ���ɹ����Ʊ�б�
    run_weekly(after_market_close,3,time='after_close', reference_security='000300.XSHG')
    # ÿ�쿪ʼ����
    run_weekly(rebalance,4, time='09:45', reference_security='000300.XSHG') 
    # ÿ�¸����б�
    run_weekly(Update_Pairs,4, time='9:40', reference_security='000300.XSHG') 



    # ���ɹ����Ʊ�б�
    run_weekly(after_market_close,4,time='after_close', reference_security='000300.XSHG')
    # ÿ�쿪ʼ����
    run_weekly(rebalance,5, time='09:45', reference_security='000300.XSHG') 
    # ÿ�¸����б�
    run_weekly(Update_Pairs,5, time='9:40', reference_security='000300.XSHG') 

    # ���ڿ������룬����ɹ������g.stock_list
    g.buy_list = []
    g.sell_list = []

    # ͳ��ʤ�ʵĲ���
    g.wins = 0
    g.loses = 0
    g.evens = 0
    
    body = read_file("pairs_beta_config.csv")
    g.pairs_info = pd.read_csv(StringIO(body),index_col=0)

    
# ��ӡ����ĳɽ���¼��������ʤ�����
def after_market_log_print(context):
    #�õ��������гɽ���¼
    i = 1
    for sec in context.portfolio.positions.keys():
        log.info('$$%d�� �ֲ֣�%s���ֲ�������%d��ӯ������� %f���ܼ�ֵ��%f' %(i, \
                str(context.portfolio.positions[sec].security), \
                int((context.current_dt - context.portfolio.positions[sec].init_time).days), \
                float((context.portfolio.positions[sec].price - context.portfolio.positions[sec].avg_cost)/context.portfolio.positions[sec].avg_cost), \
                float(context.portfolio.positions[sec].value) 
                ))
        i += 1

    log.info('$$���ն�����Ϣ')
    orders = get_orders()
    for _order in orders.values():
        
        if _order.action == "open":
            log.info("�������룬��Ʊ%s���۸�%f"%(str(_order.security),float(_order.price)))

        if _order.action == "close":
            log.info("������������Ʊ%s���۸�%f��������Ϊ��"%(str(_order.security),float(_order.price)))

    
    # # ����ֲ����
    # log.info("$$�ֲ��ܼ�ֵ��%f���ֲּ�ֵ%f"%(float(context.portfolio.total_value),float(context.portfolio.positions_value)))

    # # ͳ������ز��ʤ�ʽ��
    # log.info("$$ʤ�ܽ��Ϊ��")
    # log.info("1����ʤ������%d"%int(g.wins))
    # log.info("2��ʧ�ܴ�����%d"%int(g.loses))
    # log.info("3��ƽ�ִ�����%d"%int(g.evens))
    # log.info("4������ʤ�ʣ�%f"%float(((g.wins)/( g.wins + g.evens + g.loses))) if (g.wins + g.evens +  g.loses) != 0 else 0)

    # log.info('һ�����')
    # log.info('##############################################################')


## ���̺����к���  
# ����
def after_market_close(context):
    # ���ɹ����Ʊ�б�
    
    g.buy_list = []
    g.sell_list = []
    try:
        g.buy_list ,g.sell_list  = get_balance_list(context)
    except:
        g.buy_list = []
        g.sell_list = []
    
    log.info("$$���ɴ��չ����Ʊ�б�")
    i = 1
    for sec in g.buy_list:
        log.info("%d�����չ����Ʊ�б�%s"%(int(i),str(sec)))        
        i += 1
    
    log.info("$$���ɴ���������Ʊ�б�")
    i = 1
    for sec in g.sell_list:
        log.info("%d������������Ʊ�б�%s"%(int(i),str(sec)))        
        i += 1





def rebalance(context):
    if len(g.sell_list) != 0:
        for sec in g.sell_list:
            log.info("$$������Ʊ��%s"%(str(sec)))
            order_target_value(sec, 0)
    
    # ���������Ʊ�б��µ�
    if len(g.buy_list) != 0:
        Operate_list = set(g.buy_list) - set(context.portfolio.positions.keys())
        for sec in Operate_list:
            log.info("$$�����Ʊ��%s"%(str(sec)))
            order_target_value(sec,  context.portfolio.total_value/20)

    
####################################################     ��ʼ��д���벿��     #################################################


# ��ȡ��Ҫ�����Ĺ�Ʊ�б�
def get_balance_list(context):

    sell_list = []
    buy_list = []
        
    day_count = 200
    end_date =  context.current_dt.strftime('%Y-%m-%d')
    
    # �洢��Ʊ�ļ۸�ԭʼ����
    for i in range(0,g.pairs_info.shape[0]):
        s1 = g.pairs_info.iloc[i,:]['p1']
        s2 = g.pairs_info.iloc[i,:]['p2']
        stocks = [s1,s2]
        
        df_stocks = pd.DataFrame()
    
        # ��ʼ��ȡ���̼���Ϣ�����н���
        for stock_name in stocks:
            stock_price = get_price(stock_name, count = day_count, end_date=end_date, frequency='daily', fields='close',fq = "pre")
            stock_price_pd = pd.DataFrame(data = np.array(stock_price['close']),columns = [stock_name])
            df_stocks = pd.concat([df_stocks,stock_price_pd],axis = 1)
            
        df_stocks['residual'] = df_stocks[s2] - g.pairs_info.iloc[i,:]['beta']*df_stocks[s1] - g.pairs_info.iloc[i,:]['alpha']
        
        # ����z_score
        df_stocks['z_score'] = None 
        df_stocks['z_score'] = pd.rolling_mean(df_stocks['residual'], 2)/pd.rolling_std(df_stocks['residual'], 90)
    
        # ��ʼ�жϼ��������б�
        if df_stocks.iloc[-1,:]['z_score'] < -1:
            buy_list.append(s2)
        # elif df_stocks.iloc[-1,:]['z_score'] > 0.5:
        #     buy_list.append(s1)
    
        # ��ʼ�жϼ��������б�
        if df_stocks.iloc[-1,:]['z_score'] > 0:
            sell_list.append(s2)

        # elif df_stocks.iloc[-1,:]['z_score'] < -0:
        #     sell_list.append(s1)

    return buy_list,sell_list

def Update_Pairs(context):

    body = read_file("pairs_beta_config.csv")

    read_pairs_pd = pd.read_csv(StringIO(body),index_col=0)
    # ���������һ�£�˵�������и��£����¸�ֵ���������
    if g.pairs_info.shape[0] != read_pairs_pd.shape[0]:
        g.pairs_info = read_pairs_pd
        
        for sec in context.portfolio.positions.keys():
            log.info("$$�����Ϣ���£���ֹ�Ʊ��%s"%(str(sec)))
            order_target_value(sec, 0)
        
