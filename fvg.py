from flask import Flask, request, jsonify
import yfinance as yf
import datetime

app = Flask(__name__)

def is_fvg_up(index, open_price, close_price, low_price, high_price):
    if (
        open_price[index] > close_price[index]
        and open_price[index-1] > close_price[index-1]
        and open_price[index-2] > close_price[index-2]
        and low_price[index-2] > high_price[index]
        and low_price[index - 1] <= high_price[index]
        and high_price[index - 1] >= low_price[index-2]
    ):
        return {
            'Opening Prices': [open_price[index-2], open_price[index-1], open_price[index]],
            'Closing Prices': [close_price[index-2], close_price[index-1], close_price[index]],
            'High Prices': [high_price[index-2], high_price[index-1], high_price[index]],
            'Low Prices': [low_price[index-2], low_price[index-1], low_price[index]]
        }
    else:
        return None

def is_fvg_down(index, open_price, close_price, low_price, high_price):
    if (
        open_price[index] < close_price[index]
        and open_price[index-1] < close_price[index-1]
        and open_price[index-2] < close_price[index-2]
        and low_price[index] > high_price[index-2]
        and low_price[index - 1] <= high_price[index]
        and high_price[index - 1] >= low_price[index]
    ):
        return {
            'Opening Prices': [open_price[index-2], open_price[index-1], open_price[index]],
            'Closing Prices': [close_price[index-2], close_price[index-1], close_price[index]],
            'High Prices': [high_price[index-2], high_price[index-1], high_price[index]],
            'Low Prices': [low_price[index-2], low_price[index-1], low_price[index]]
        }
    else:
        return None

@app.route('/fetch_and_store', methods=['POST'])
def fetch_and_store_data():
    try:
        data = request.json  # Expected JSON data with 'start_date' and 'end_date'

        # Extract user-defined start_date and end_date from JSON data
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        # Convert user-defined date strings to datetime objects
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

        print("Received JSON data - Start Date:", start_date, "End Date:", end_date)

        # Fetch the historical data using yfinance
        nifty_data = yf.download('^NSEI', start=start_date, end=end_date, interval="1d")

        # Extract the relevant columns from the fetched data
        open_price = nifty_data['Open']
        close_price = nifty_data['Close']
        low_price = nifty_data['Low']
        high_price = nifty_data['High']

        # Initialize a list to store results
        results = []

        # Iterate over the data to find "FVG UP" and "FVG DOWN" patterns
        for index in range(2, len(open_price)-2):
            fvg_up_result = is_fvg_up(index, open_price, close_price, low_price, high_price)
            if fvg_up_result:
                results.append({'FVG_UP': fvg_up_result})
            fvg_down_result = is_fvg_down(index, open_price, close_price, low_price, high_price)
            if fvg_down_result:
                results.append({'FVG_DOWN': fvg_down_result})

        # Return the results as JSON
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5010)
