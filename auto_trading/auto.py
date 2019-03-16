import sys
import ta
from auto_trading import MACDAutoTrader, SVMAutoTrader, MLPAutoTrader, PerfectAutoTrader, KerasConvAutoTrader
from auto_trading.AutoTrader import calculate_profit

sys.path.append("..")
from utils.db.Db import Db
from sklearn.metrics import classification_report

db = Db("../cache")
df = db.get_symbols_as_dataframe(['AVGO'])
df = ta.add_all_ta_features(df, "open", "high", "low", "adjusted_close", "volume")

perf = PerfectAutoTrader(df, close="adjusted_close")
perfect_trades = perf.get_trades()

conv = KerasConvAutoTrader(df, close="adjusted_close")
conv_trades = conv.get_trades()

macd = MACDAutoTrader(df, close="adjusted_close")
macd_trades = macd.get_trades()

svm = SVMAutoTrader(df, close="adjusted_close")
svm_trades = svm.get_trades()

mlp = MLPAutoTrader(df, close="adjusted_close")
mlp_trades = mlp.get_trades()

y_true = perfect_trades['signal'].as_matrix()
macd_pred = macd_trades['signal'].as_matrix()
svm_pred = svm_trades['signal'].as_matrix()
mlp_pred = mlp_trades['signal'].as_matrix()

print("MACD:")
print(classification_report(y_true, macd_pred, target_names=["Hold", "Buy", "Sell"]))
print("SVM:")
print(classification_report(y_true, svm_pred, target_names=["Hold", "Buy", "Sell"]))
print("MLP:")
print(classification_report(y_true, mlp_pred, target_names=["Hold", "Buy", "Sell"]))

start_money = 1000.
close = 'close'
perfect_profits = calculate_profit(df, perfect_trades, close=close, start_money=start_money)
macd_profits = calculate_profit(df, macd_trades, close=close, start_money=start_money)
svm_profits = calculate_profit(df, svm_trades, close=close, start_money=start_money)
mlp_profits = calculate_profit(df, mlp_trades, close=close, start_money=start_money)

print("Start Money: $" + str(start_money))
print("Perfect Trading End Money: $" + str(perfect_profits[0]))
print("MACD End Money: $" + str(macd_profits[0]))
print("SVM End Money: $" + str(svm_profits[0]))
print("MLP End Money: $" + str(mlp_profits[0]))
print("Buy and Hold: $" + str(perfect_profits[1]))
pvbnh = perfect_profits[0] - perfect_profits[1]
print("Perfect vs Buy and Hold: " + "+"+str(pvbnh) if pvbnh > 0 else pvbnh )
macvbnh = macd_profits[0] - perfect_profits[1]
print("MACD vs Buy and Hold: " + "+"+str(macvbnh) if macvbnh > 0 else macvbnh )
svmvbnh = svm_profits[0] - perfect_profits[1]
print("SVM vs Buy and Hold: " + "+"+str(svmvbnh) if svmvbnh > 0 else svmvbnh )
mlpvbnh = mlp_profits[0] - perfect_profits[1]
print("MLP vs Buy and Hold: " + "+"+str(mlpvbnh) if mlpvbnh > 0 else mlpvbnh )


# print("Profit: " + (str(current_money - start_money)))
# print("Number of Trades: " + str(len(mins_dates) + len(maxes_dates)))
# print("Buy and Hold: $" + str(end_money))
