from itertools import chain
import datetime

call_auction = 0  # 集合竞价
match = 1  # 撮合
continuous_auction = 2  # 连续竞价
closed = 3

t = datetime.time

# 中金所股指期货日盘
CFFEX_sid = (
    [t(9, 25), t(9, 29), call_auction],  # 集合竞价
    [t(9, 29), t(9, 30), call_auction],  # 撮合
    [t(9, 30), t(11, 30), continuous_auction],  # 连续竞价
    [t(13, 0), t(15, 0), continuous_auction],  # 连续竞价
)

# 中金所国债期货日盘
CFFEX_ndd = (
    [t(9, 10), t(9, 14), call_auction],  # 集合竞价
    [t(9, 14), t(9, 15), call_auction],  # 撮合
    [t(9, 15), t(11, 30), continuous_auction],  # 连续竞价
    [t(13, 0), t(15, 0), continuous_auction],  # 连续竞价
)

# 郑商所日盘
CZCE_d = (
    [t(8, 55), t(8, 59), call_auction],  # 集合竞价
    [t(8, 59), t(9, 0), call_auction],  # 撮合
    [t(9, 0), t(10, 15), continuous_auction],  # 连续竞价
    [t(10, 30), t(11, 30), continuous_auction],  # 连续竞价
    [t(13, 30), t(13, 0), continuous_auction],  # 连续竞价
)

# 郑商所夜盘
CZCE_n = (
    [t(20, 55), t(20, 59), call_auction],  # 集合竞价
    [t(20, 59), t(21, 0), call_auction],  # 撮合
    [t(21, 0), t(23, 30), continuous_auction],  # 连续竞价
)

# 大商所日盘
DCE_d = CZCE_d
# 大商所夜盘
DCE_n = CZCE_n

# 上期所日盘
SHFE_d = CZCE_d
# 上期所夜盘
SHFE_n1 = (
    [t(20, 55), t(20, 59), call_auction],  # 集合竞价
    [t(20, 59), t(21, 0), call_auction],  # 撮合
    [t(21, 0), t(23, 59, 59), continuous_auction],  # 连续竞价
    [t(0, 0), t(2, 30), continuous_auction],  # 连续竞价
)
# 上期所深夜盘2
SHFE_n2 = (
    [t(20, 55), t(20, 59), call_auction],  # 集合竞价
    [t(20, 59), t(21, 0), call_auction],  # 撮合
    [t(21, 0), t(23, 59, 59), continuous_auction],  # 连续竞价
    [t(0, 0), t(1, 0), continuous_auction],  # 连续竞价
)
# 上期所深夜盘3
SHFE_n3 = (
    [t(20, 55), t(20, 59), call_auction],  # 集合竞价
    [t(20, 59), t(21, 0), call_auction],  # 撮合
    [t(21, 0), t(23, 0), continuous_auction],  # 连续竞价
)

# 期货交易时间
futures_tradeing_time = {
    # 中金所
    "IC": CFFEX_sid,  # 中证500股指
    "IF": CFFEX_sid,  # 沪深300股指
    "IH": CFFEX_sid,  # 上证50股指
    "TF": CFFEX_ndd,  # 5年国债
    "T": CFFEX_ndd,  # 10年国债

    # 郑商所
    "CF": list(chain(CZCE_d, CZCE_n)),  # 棉花709
    "ZC": list(chain(CZCE_d, CZCE_n)),  # 动力煤ZC709
    "SR": list(chain(CZCE_d, CZCE_n)),  # SR1803
    "RM": list(chain(CZCE_d, CZCE_n)),  # 菜籽粕709
    "MA": list(chain(CZCE_d, CZCE_n)),  # 甲醇MA709
    "PTA": list(chain(CZCE_d, CZCE_n)),  # PTA
    "FG": list(chain(CZCE_d, CZCE_n)),  # 玻璃709
    "OI": list(chain(CZCE_d, CZCE_n)),  # 菜籽油709
    "TA": CZCE_d,  # 化纤709
    "WH": CZCE_d,  # 强筋麦709
    "SM": CZCE_d,  # 锰硅709
    "SF": CZCE_d,  # 硅铁709
    "RS": CZCE_d,  # 油菜籽709
    "RI": CZCE_d,  # 早籼稻709
    "PM": CZCE_d,  # 普通小麦709
    "LR": CZCE_d,  # 晚籼稻709
    "JR": CZCE_d,  # 粳稻709

    # 大商所
    "j": list(chain(DCE_d, DCE_n)),  # 焦炭1709
    "i": list(chain(DCE_d, DCE_n)),  # 铁矿石1709
    "jm": list(chain(DCE_d, DCE_n)),  # 焦煤1709
    "a": list(chain(DCE_d, DCE_n)),  # 黄大豆1号1803
    "y": list(chain(DCE_d, DCE_n)),  # 豆油1709
    "m": list(chain(DCE_d, DCE_n)),  # 豆粕1709
    "b": list(chain(DCE_d, DCE_n)),  # 黄大豆2号1709
    "p": list(chain(DCE_d, DCE_n)),  # 棕榈油1709
    ###################
    "jd": DCE_d,  # 鲜鸡蛋1709
    "l": DCE_d,  # 聚乙烯1709
    "v": DCE_d,  # 聚氯乙烯1709
    "pp": DCE_d,  # 聚丙烯1709
    "fb": DCE_d,  # 纤维板1709
    "cs": DCE_d,  # 玉米淀粉1709
    "c": DCE_d,  # 黄玉米1709
    "bb": DCE_d,  # 胶合板1709

    # 上期所
    "ag": list(chain(SHFE_d, SHFE_n1)),  # 白银1709
    "au": list(chain(SHFE_d, SHFE_n1)),  # 黄金1710
    ##################
    "pb": list(chain(SHFE_d, SHFE_n2)),  # 铅1709
    "ni": list(chain(SHFE_d, SHFE_n2)),  # 镍1709
    "zn": list(chain(SHFE_d, SHFE_n2)),  # 锌1709
    "al": list(chain(SHFE_d, SHFE_n2)),  # 铝1709
    "sn": list(chain(SHFE_d, SHFE_n2)),  # 锡1709
    "cu": list(chain(SHFE_d, SHFE_n2)),  # 铜1709
    #########
    "ru": list(chain(SHFE_d, SHFE_n3)),  # 天然橡胶1709
    "rb": list(chain(SHFE_d, SHFE_n3)),  # 螺纹钢1709
    "hc": list(chain(SHFE_d, SHFE_n3)),  # 热轧板1709
    "bu": list(chain(SHFE_d, SHFE_n3)),  # 沥青1809
    ##############
    "wr": SHFE_d,  # 线材1709
    "fu": SHFE_d,  # 燃料油1709
}


def get_trading_status(future, now=None):
    now = now or datetime.datetime.now().time()
    # 时间列表
    trading_time = futures_tradeing_time[future]
    for b, e, s in trading_time.values():
        # 返回对应的状态
        if b <= now < e:
            return s
    else:
        # 不在列表中则为休市状态
        return closed


