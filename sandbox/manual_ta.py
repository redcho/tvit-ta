# # Consistent
# df['MA'] = ma(df)
#
#
# # Consistent
# df['EMA'] = ema(df)
# df['btaEma'] = btalib.ema(df.close, period=3).df
#
# # Consistent
# df['MACD'], df['Signal'] = macd(df)
# btamacd = btalib.macd(df.close).df

def ma(data):
    return data.close.rolling(window=9, min_periods=1).mean()


def ema(data):
    return data.close.ewm(span=3, adjust=False).mean()


def macd(data):
    exp1 = data.close.ewm(span=12, adjust=False).mean()
    exp2 = data.close.ewm(span=26, adjust=False).mean()

    macd = exp1-exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal