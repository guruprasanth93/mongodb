from flask import Flask, request, jsonify
import yfinance as yf
import pymongo
import datetime

app = Flask(__name__)

# Increase the maximum allowed message size to 100 MB (adjust as needed)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Define the MongoDB connection settings
mongo_client = pymongo.MongoClient("mongodb://127.0.0.1:27018/")  # Update with your MongoDB connection URL
db = mongo_client["roi_data"]  # Choose or create a database
collection = db["remo_data"]  # Choose or create a collection

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

        # Convert the DataFrame to a list of dictionaries for MongoDB insertion
        data_to_insert = nifty_data.reset_index().to_dict(orient='records')

        # Insert the data into MongoDB
        collection.insert_many(data_to_insert)

        return jsonify({"message": "Data has been fetched and stored in MongoDB."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
