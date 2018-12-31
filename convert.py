import gzip, json, os, sqlite3
from utils import Db, AlphaVantage
import datetime

files = filter(lambda x: ".json" in x, os.listdir("cache"))



db = Db()

def combine(data, symbol):
    combined = {}
    for download_date in data[symbol]:
        if AlphaVantage.error_text in data[symbol][download_date]: continue
        for date in data[symbol][download_date][AlphaVantage.time_series_key]:
            if date in combined: continue
            combined[date] = data[symbol][download_date][AlphaVantage.time_series_key][date]
    record = []
    for date in combined:
        record.append([
            symbol,
            datetime.datetime.strptime(date, '%Y-%m-%d').timestamp(),
            float(combined[date]['3. low']),
            float(combined[date]['7. dividend amount']),
            float(combined[date]['5. adjusted close']),
            float(combined[date]['1. open']),
            float(combined[date]['8. split coefficient']),
            float(combined[date]['4. close']),
            float(combined[date]['2. high']),
            float(combined[date]['6. volume'])
        ])
    return record

for filename in files:
    with open("cache/" + filename, 'r') as file:
        data = json.loads(file.read())
        symbol = filename.replace(".json", "")
        combined = combine(data, symbol)
        db.insert_alpha_vantage_records(combined)

        for download_date in data[symbol]:
            date = int(datetime.datetime.strptime(download_date, '%Y-%m-%d').timestamp())
            db.insert_alpha_vantage_api_request(date, filename.replace(".json", ""))




