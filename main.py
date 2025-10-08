import argparse
import sys
import logging
from decimal import Decimal
from data_parser import DataParser

def main():
    """
    Main function to run the command-line interface for the aggregate price parser.
    """
    parser = argparse.ArgumentParser(
        description="Find the cheapest aggregate product from a CSV file.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "file",
        type=str,
        help="Path to the aggregate pricing CSV file."
    )
    parser.add_argument(
        "--location-name",
        type=str,
        help="Filter products by a specific location name (e.g., 'Cherokee')."
    )
    parser.add_argument(
        "--location-number",
        type=str,
        help="Filter products by a specific location number (e.g., '594')."
    )
    parser.add_argument(
        "--account-holder",
        action="store_true",
        help="Calculate costs using account-holder pricing."
    )
    parser.add_argument(
        "--include-delivery",
        action="store_true",
        help="Include delivery costs in the total price calculation."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging output."
    )

    args = parser.parse_args()

    # --- Logging Setup ---
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # --- Main Logic ---
    data_parser = DataParser(surcharge=Decimal('0.10'))

    # 1. Parse all products from the CSV
    all_products = data_parser.parse_csv(args.file)
    if not all_products:
        print(f"Could not read any products from {args.file}. Exiting.", file=sys.stderr)
        sys.exit(1)

    # 2. Filter the products if location criteria are provided
    filtered_products = data_parser.filter_products(
        all_products,
        location_name=args.location_name,
        location_number=args.location_number
    )

    # 3. Find the cheapest product from the (potentially filtered) list
    result = data_parser.find_cheapest_product(
        filtered_products,
        tons=Decimal('25'),
        is_account_holder=args.account_holder,
        include_delivery=args.include_delivery
    )

    # 4. Print the results
    if result:
        product, cost = result
        print("\n--- Cheapest Option Found ---")
        print(f"  Product:      {product.product_name}")
        print(f"  Location:     {product.location_name} ({product.location_number})")
        print(f"  Address:      {product.address}")
        print(f"  Total Cost:   ${cost:.2f} for 25 tons")
    else:
        print("\n--- No suitable product found with the specified criteria. ---")

if __name__ == "__main__":
    main()