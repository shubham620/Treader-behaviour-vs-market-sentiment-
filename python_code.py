import pandas as pd
trades = pd.read_csv("historical_data.csv")
trades.columns = trades.columns.str.strip().str.lower()
print(trades.columns)
print(trades[['timestamp', 'timestamp ist']].head())
trades['time'] = pd.to_datetime(trades['timestamp'], unit='ms')
trades['date'] = trades['time'].dt.date
trades = trades[['account', 'size usd', 'side', 'closed pnl', 'date']]
trades = trades.rename(columns={
    'size usd': 'size_usd',
    'closed pnl': 'closed_pnl'
})
trades['closed_pnl'] = pd.to_numeric(trades['closed_pnl'], errors='coerce')
trades = trades.dropna(subset=['closed_pnl', 'date'])
print(trades.head())
print(trades.info())
sentiment = pd.read_csv("fear_greed_index.csv")
sentiment.columns = sentiment.columns.str.strip().str.lower()
print(sentiment.columns)
sentiment['date'] = pd.to_datetime(sentiment['date']).dt.date
merged = pd.merge(trades, sentiment, on='date', how='inner')
merged.groupby('classification')['closed_pnl'].mean()
merged.groupby('classification')['closed_pnl'].sum()
merged['classification'].value_counts()
merged.groupby('classification')['size_usd'].mean()
merged['profit_flag'] = merged['closed_pnl'] > 0
merged.groupby('classification')['profit_flag'].mean()

import matplotlib.pyplot as plt

profit_data = merged.groupby('classification')['closed_pnl'].mean()

profit_data.plot(kind='bar')
plt.title("Average Profit by Sentiment")
plt.xlabel("Sentiment")
plt.ylabel("Average Profit")
plt.show()

fear_profit = profit_data.get('Fear', 0)
greed_profit = profit_data.get('Greed', 0)

if greed_profit > fear_profit:
    print("Insight: Traders are more profitable during Greed periods.")
else:
    print("Insight: Traders perform better during Fear periods.")
activity = merged['classification'].value_counts()

activity.plot(kind='bar')
plt.title("Trading Activity by Sentiment")
plt.show()

if activity['Fear'] > activity['Greed']:
    print("Insight: More trades happen during Fear → panic trading.")
else:
    print("Insight: More trades happen during Greed → hype trading.")

size_data = merged.groupby('classification')['size_usd'].mean()

size_data.plot(kind='bar')
plt.title("Average Trade Size")
plt.show()

if size_data['Greed'] > size_data['Fear']:
    print("Insight: Traders invest more during Greed (high confidence).")
else:
    print("Insight: Traders invest more during Fear (risk-taking behavior).")


merged['profit_flag'] = merged['closed_pnl'] > 0

win_rate = merged.groupby('classification')['profit_flag'].mean()

win_rate.plot(kind='bar')
plt.title("Win Rate by Sentiment")
plt.show()

if win_rate['Greed'] > win_rate['Fear']:
    print("Insight: Higher win rate during Greed.")
else:
    print("Insight: Higher win rate during Fear.")

# Create insights dictionary
insights = {}

fear_profit = profit_data.get('fear', 0)
greed_profit = profit_data.get('greed', 0)

activity_fear = activity.get('fear', 0)
activity_greed = activity.get('greed', 0)

size_fear = size_data.get('fear', 0)
size_greed = size_data.get('greed', 0)

win_fear = win_rate.get('fear', 0)
win_greed = win_rate.get('greed', 0)

# Fill insights
insights['profit'] = "Greed more profitable" if greed_profit > fear_profit else "Fear more profitable"
insights['activity'] = "More trading in Fear" if activity_fear > activity_greed else "More trading in Greed"
insights['size'] = "Larger trades in Greed" if size_greed > size_fear else "Larger trades in Fear"
insights['win_rate'] = "Higher win rate in Greed" if win_greed > win_fear else "Higher win rate in Fear"

import json

with open("insights.json", "w") as f:
    json.dump(insights, f, indent=4)
