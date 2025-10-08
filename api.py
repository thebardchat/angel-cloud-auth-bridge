import logging
from dataclasses import asdict
from decimal import Decimal

from flask import Flask, jsonify
from flask_cors import CORS, request

from data_parser import DataParser

# --- Configuration ---

# IMPORTANT: Update this to the actual path of your CSV file.
CSV_FILE_PATH = "Aggregate Price by Location as of 10_06_2025.csv"

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for the app

# Override Flask's default JSON encoder to handle Decimal objects
class CustomJSONEncoder(Flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(CustomJSONEncoder, self).default(obj)
app.json_encoder = CustomJSONEncoder

logging.basicConfig(level=logging.INFO)

# --- API Endpoints ---

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Parses the CSV and returns all products as a JSON list.
    """
    try:
        # Read filter parameters from the request query string
        location_name = request.args.get('location_name', type=str)
        location_number = request.args.get('location_number', type=str)

        # Instantiate the parser with the business-logic surcharge
        parser = DataParser(surcharge=Decimal('0.10'))
        all_products = parser.parse_csv(CSV_FILE_PATH)
        if not all_products:
            logging.warning("No products found or file could not be read from: %s", CSV_FILE_PATH)
            return jsonify({"error": "No products found or file is empty."}), 404

        # Filter the products based on query parameters
        filtered_products = parser.filter_products(
            all_products, location_name=location_name, location_number=location_number
        )

        # Convert list of Product objects to a list of dictionaries
        product_dicts = [asdict(p) for p in filtered_products]
        return jsonify(product_dicts)

    except Exception as e:
        logging.exception("An error occurred while fetching products.")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/api/quote', methods=['GET'])
def get_quote():
    """
    Calculates the optimal quote based on delivery time and location filters.
    """
    try:
        # --- Get Parameters ---
        delivery_minutes = request.args.get('delivery_minutes', type=int)
        if delivery_minutes is None:
            return jsonify({"error": "delivery_minutes parameter is required."}), 400

        location_name = request.args.get('location_name', type=str)
        # For now, we assume account holder pricing for quotes, as in the dashboard
        is_account_holder = True

        # --- Logic ---
        parser = DataParser(surcharge=Decimal('0.10'))
        all_products = parser.parse_csv(CSV_FILE_PATH)
        if not all_products:
            return jsonify({"error": "No products found or file is empty."}), 404

        filtered_products = parser.filter_products(all_products, location_name=location_name)

        # --- Find Optimal Quote ---
        optimal_quote = None
        for product in filtered_products:
            current_quote = parser.calculate_full_quote(
                product,
                delivery_minutes=delivery_minutes,
                is_account_holder=is_account_holder
            )
            if current_quote:
                if optimal_quote is None or current_quote['total_cost'] < optimal_quote['total_cost']:
                    optimal_quote = current_quote

        if not optimal_quote:
            return jsonify({"error": "No products with valid prices found for the given criteria."}), 404

        # Convert the Product object within the quote to a dictionary for JSON response
        optimal_quote['product'] = asdict(optimal_quote['product'])
        return jsonify(optimal_quote)

    except Exception as e:
        logging.exception("An error occurred while generating the quote.")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    # Runs the Flask development server
    app.run(debug=True, port=5001)