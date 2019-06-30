import pandas as pd


df = pd.DataFrame([
    [19.6],
    [19.25],
    [0.0],
    [19.75],
    [19.98]
])

change = df.pct_change()

print(change)