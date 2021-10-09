import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

ticker = "JNJ"
plot_chart = False  # show graph or not

# download the data from Yahoo! Finance (GSPC = S&P 500)
df = yf.download(ticker, start="2018-01-01", end="2021-10-01")
df["MA200"] = df['Adj Close'].rolling(window=200).mean()
# get rid of empty records (NaN)
df = df.dropna()

# print a nice graph
plt.plot(df['Adj Close'], label="Price")
plt.plot(df["MA200"], label="MA 200")
plt.xlabel('Date')
plt.ylabel(f'{ticker} Moving Average for last 200 days')
plt.legend(loc='best', ncol=2, mode=None, shadow=False, fancybox=False)
# show graph
plt.show() if plot_chart else None

# add a new column - price change
# remove some weird error message (https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html#options)
pd.set_option("mode.chained_assignment", None)
df['price change'] = df['Adj Close'].pct_change()
df = df.dropna()

# calculate RSI (Wilder's Smoothing Method)
df['Upmove'] = df['price change'].apply(lambda x: x if x > 0 else 0)
df['Downmove'] = df['price change'].apply(lambda x: abs(x) if x < 0 else 0)
df['avg Up'] = df['Upmove'].ewm(span=19).mean()
df['avg Down'] = df['Downmove'].ewm(span=19).mean()
df = df.dropna()
df['RS'] = df['avg Up'] / df['avg Down']
df['RSI'] = df['RS'].apply(lambda x: 100 - (100/(x+1)))

# find buying points
df.loc[(df['Adj Close'] > df["MA200"]) & (df['RSI'] < 30), 'Buy'] = 'Yes'
df.loc[(df['Adj Close'] < df["MA200"]) | (df['RSI'] > 30), 'Buy'] = 'No'

# calculate profit
PnL = []
for i in range(len(df)-12):
    if "Yes" in df['Buy'].iloc[i]:
        # print(df.iloc[i])
        print(f"Enter at {df['Open'].iloc[i+1]}")
        # count 10 days after buying to check if we should sell
        for j in range(1, 11):
            # sell if RSI is above 40
            if df['RSI'].iloc[i + j] > 40:
                # record the profit: selling price (next day's open) - buying price (is the next day's open)
                PnL.append(df['Open'].iloc[i+j+1] - df['Open'].iloc[i+1])
                print(f"Exit at {df['Open'].iloc[i+j+1]} with {PnL[-1]}")
                break
            # sell after 10 trading days
            if j == 10:
                # record the profit:
                # selling price (next day's open after 10 trading days) - buying price (is the next day's open)
                PnL.append(df['Open'].iloc[i+12] - df['Open'].iloc[i+1])
                print(f"Exit after {j} days at {df['Open'].iloc[i+12]} with {PnL[-1]}")
                break

# find the profitable/successful trades
successful = len([i for i in PnL if i > 0])

# all trades
all_trades = len(PnL)

# find the percentage of successful trades
print(f'Successful trades: {successful}/{all_trades} ({len([i for i in PnL if i > 0])/len(PnL)})%')
print(f'Profit: {sum(PnL)}')
