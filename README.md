# Kalman_Trading


## step1：

文件名：KalmanTrading.ipynb
运行环境：joinquant 研究环境
功能：从平台中取出数据，并根据要求进行数据验证，最终输出配对结果，配对结果对应的验证情况

结果：
csv文件，其中包含配对结果，验证情况

## step2：

手工针对数据结果进行筛选，按照行业进行筛选划分

结果：
csv文件，其中仅包含配对结果、beta、alpha等数据，用于进行。
同时每个行业选择一对即可，避免行业风险

样表见：pairs_beta_config.csv

## step3：
文件名：trade.py
运行环境：joinquant 交易环境
功能：使用聚宽平台进行模拟交易

结果：
交易结果信息