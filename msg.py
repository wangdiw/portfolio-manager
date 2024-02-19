import requests
import time
import json
import random

def read_json(path):
    """ Reads json file and returns a dict of it """
    with open(path, "r") as file_object:
        json_raw = file_object.read()
        json_dict = json.loads(json_raw)
    return json_dict

def random_number_generator(lowest, highest):
    return random.randint(lowest, highest)

TOKENS = read_json("tokens.json")
WALLET = read_json("wallet.json")
PROXY = read_json("proxy.json")
HEADER_REQUESTS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
}

def fetch_prices(tokens, wallet, proxies):
    results = {}
    for index, (token, data) in enumerate(wallet.items(), start=1):
        current_price = get_token_price(tokens[token],index, proxies)
        if current_price is not None:
            entry_value = data['total'] * data['entry']
            current_value = data['total'] * current_price
            profit_usdt = current_value - entry_value
            profit_percentage = (current_value / entry_value - 1) * 100 if entry_value != 0 else 0
            multiplication = current_value / entry_value if entry_value != 0 else 0
            results[token] = {
                "INVESTED": entry_value,
                "WORTH_NOW": current_value,
                "PROFIT_USDT": profit_usdt,
                "PROFIT_PERCENTAGE": profit_percentage
            }
        else:
            print(f'Failed to fetch price for {token}')
    return results

def get_token_price(token_address, number_token, proxies=None, base_currency='usd', max_retries=1000):
    retry_count = 0
    wait_time = 2
    while retry_count < max_retries:
        url = f'https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={token_address}&vs_currencies={base_currency}'
        # proxy = proxies[random_number_generator(0, len(proxies) - 1)]
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(str(number_token) + "/" + str(len(TOKENS)))
                return data.get(token_address.lower(), {}).get(base_currency)
            else:
                retry_count += 1
                # print(f"Failed to fetch price for {token_address}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)  # Exponential backoff
        except requests.exceptions.RequestException as e:
            # print(f"An error occurred while fetching data: {e}")
            retry_count += 1
            # print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)  # Exponential backoff
    print(f"Failed to fetch price for {token_address} after {max_retries} retries.")
    return None


def calculate_totals(results):
    # Initialize variables for total investment, total worth, total profit in USDT, and total profit percentage
    total_investment = 0
    total_worth = 0
    total_profit_usdt = 0

    # Iterate through the results dictionary to calculate total investment, total worth, and total profit
    for token, data in results.items():
        total_investment += data['INVESTED']
        total_worth += data['WORTH_NOW']
        total_profit_usdt += data['PROFIT_USDT']

    # Calculate total profit percentage
    total_profit_percentage = ((total_worth / total_investment) - 1) * 100 if total_investment != 0 else 0

    # Round all numerical values to two decimal places
    total_investment = round(total_investment, 2)
    total_worth = round(total_worth, 2)
    total_profit_usdt = round(total_profit_usdt, 2)
    total_profit_percentage = round(total_profit_percentage, 2)

    return {
        "Total Investment": total_investment,
        "Total Worth": total_worth,
        "Total Profit (USDT)": total_profit_usdt,
        "Total Profit (%)": total_profit_percentage
    }

# Fetch token prices and store data in a dictionary
results = fetch_prices(TOKENS, WALLET, PROXY)
# Calculate totals
totals = calculate_totals(results)


