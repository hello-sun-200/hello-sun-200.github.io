import sys
import requests
try:
    n = float(sys.argv[1])
except ValueError:
    sys.exit("Wrong Input!")
try:
    response = requests.get(
        "https://rest.coincap.io/v3/assets/bitcoin?apiKey=d4548f0830c2c2503dc668c37639405045d6dcff5ae848e87d5f8aaa86b9c310"
    )
    amount=float(response.json()['data']['priceUsd'])*n
    print(f"${amount:,.4f}")
except requests.RequestException:
    pass

