import pandas as pd


df = pd.read_csv("../cache/simfin_fundamentals_narrow.csv", sep=';')
df = df[df['Ticker'] == 'AAPL']
df['publish date'] = pd.to_datetime(df['publish date'])
df = df.set_index('publish date')
df = df.pivot(columns='Ticker')
print(df.head())