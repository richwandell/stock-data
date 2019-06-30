import requests

if __name__ == "__main__":

    ENDPOINT = "https://api.tdameritrade.com/v1/marketdata/AAPL/pricehistory"

    r = requests.get(
        url=ENDPOINT,
        params={
            'apikey': "RICHWANDELL1",
            "periodType": "year",
            "frequencyType": "daily",
            "period": 10
        },
        headers={
            'Accept': 'application/json'
        }
    )
    try:
        data = r.json()
    except Exception as e:
        print(e)

    print(data)
