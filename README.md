# slaveo
常用的金融证券交易相关的功能

## 安装
```
pip install git+https://github.com/lamter/slaveo.git#egg=slaveo
```

## 功能
各个功能直接封装成逐个模块包

### 交易时间段

期货定义了以下状态，"处于交易中"通常单指```continuous_auction = 3  # 连续竞价```阶段。

```
closed = 0
call_auction = 1  # 集合竞价
match = 2  # 撮合
continuous_auction = 3  # 连续竞价
```

对交易时间的判断
```python
import tradingtime as tt

# 当前至少有一个期货品种处于交易阶段
tt.is_any_trading()

# 获得给定的时间点，对应的期货品种是否正处于交易阶段
import arrow
status = tt.get_trading_status(
    "rb",
    now=arrow("2016/12/08 21:00:20"),
)

# 处于连续竞价阶段
status == tt.continuous_auction
```


