import unittest
import os
import logging
import csv
from decimal import Decimal
from data_parser import DataParser, Product

class TestDataParser(unittest.TestCase):

    def setUp(self):
        """Set up a test CSV file and the parser instance."""
        self.parser = DataParser(surcharge=Decimal('0.10'))
        self.test_csv_path = "test_data.csv"
        with open(self.test_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Plant,or,Quarry Name/Type/Location Number", "Address", "Product", "Non-Account Holder Price Per Ton", "Account Holder Price Per Ton", "Delivery Cost Per Ton Added in If We Are Hauling"])
            writer.writerow(["Cherokee/Rock Quarry/594", "40 Sutton Hill Rd, Cherokee, AL 35616", "#89 Stone", "$20.00", "$19.00", "$2.50"])
            writer.writerow(["Lacey's Spring/Rock Quarry/71501", "105 Vaughn Rd, Laceys Spring, AL 35754", "Fill Dirt", "$50.00 per load", "$50.00 per load", "CALL"])
            writer.writerow(["Cherokee/Rock Quarry/594", "40 Sutton Hill Rd, Cherokee, AL 35616", "8910s", "CALL", "CALL", "3.00"])
            writer.writerow(["Monteagle/Sand Quarry/71087", "15878 Sewanee Hwy, TN 37375", "1 1/2\"", "24.00", "$23.00", "N/A"])
            writer.writerow(["Incomplete/Location", "Some Address", "Cheap Stone", "$10.00", "$9.00", "$15.00"])
            writer.writerow([]) # Empty line
            writer.writerow(["Lacey's Spring/Rock Quarry/71501", "105 Vaughn Rd, Laceys Spring, AL 35754", "", "", "", ""]) # Malformed/empty data row

    def tearDown(self):
        """Clean up the test CSV file."""
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)

    def test_parse_csv_file_not_found(self):
        """Test that an error is logged when the CSV file is not found."""
        # Use assertLogs to capture and check log output
        with self.assertLogs('data_parser', level='ERROR') as cm:
            result = self.parser.parse_csv("non_existent_file.csv")
            self.assertEqual(result, [])
            self.assertIn("File not found", cm.output[0])

    def test_parse_csv_successful(self):
        """Test successful parsing of a valid CSV file."""
        results = self.parser.parse_csv(self.test_csv_path)
        self.assertEqual(len(results), 5) # Should skip the empty and malformed lines

    def test_location_parsing(self):
        """Test that the location/name/type/number column is parsed correctly."""
        results = self.parser.parse_csv(self.test_csv_path)
        
        # Test a full location string
        self.assertEqual(results[0].location_name, 'Cherokee')
        self.assertEqual(results[0].location_type, 'Rock Quarry')
        self.assertEqual(results[0].location_number, '594')

        # Test an incomplete location string
        self.assertEqual(results[4].location_name, 'Incomplete')
        self.assertEqual(results[4].location_type, 'Location')
        self.assertIsNone(results[4].location_number)

    def test_price_cleaning(self):
        """Test that various price formats are cleaned and converted to Decimal."""
        results = self.parser.parse_csv(self.test_csv_path)

        # Standard price: "$20.00"
        self.assertEqual(results[0].price_non_account, Decimal('20.10'))
        self.assertEqual(results[0].price_account, Decimal('19.10'))

        # Price with "per load": "$50.00 per load" should become 50.10
        self.assertEqual(results[1].price_non_account, Decimal('50.10'))

        # "CALL" price
        self.assertIsNone(results[2].price_non_account)
        self.assertIsNone(results[2].price_account)

        # Price without dollar sign: "24.00"
        self.assertEqual(results[3].price_non_account, Decimal('24.10'))

    def test_data_mapping(self):
        """Test that the data is correctly mapped to the new keys."""
        results = self.parser.parse_csv(self.test_csv_path)
        first_result = results[0]

        self.assertEqual(first_result.address, "40 Sutton Hill Rd, Cherokee, AL 35616")
        self.assertEqual(first_result.product_name, "#89 Stone")
        self.assertEqual(first_result.delivery_cost_per_ton, Decimal("2.50"))
    
    def test_delivery_cost_parsing(self):
        """Test that the delivery cost column is parsed correctly."""
        results = self.parser.parse_csv(self.test_csv_path)

        # Standard delivery cost: "$2.50"
        self.assertEqual(results[0].delivery_cost_per_ton, Decimal('2.50'))
        # "CALL" delivery cost
        self.assertIsNone(results[1].delivery_cost_per_ton)
        # "N/A" delivery cost
        self.assertIsNone(results[3].delivery_cost_per_ton)
        # Blank delivery cost
        self.assertEqual(results[4].delivery_cost_per_ton, Decimal('15.00'))

    def test_calculate_total_cost(self):
        """Test the total cost calculation logic."""
        results = self.parser.parse_csv(self.test_csv_path)
        product1 = results[0] # Non-Acct: $20, Acct: $19, Delivery: $2.50
        product2 = results[1] # Non-Acct: $50, Acct: $50, Delivery: CALL
        product3 = results[2] # Base price is CALL

        tons = Decimal('10')

        # Case 1: Non-account holder, no delivery
        cost1 = self.parser.calculate_total_cost(product1, tons, is_account_holder=False, include_delivery=False)
        self.assertEqual(cost1, Decimal('201.00')) # 10 tons * $20.10/ton

        # Case 2: Account holder, no delivery
        cost2 = self.parser.calculate_total_cost(product1, tons, is_account_holder=True, include_delivery=False)
        self.assertEqual(cost2, Decimal('191.00')) # 10 tons * $19.10/ton

        # Case 3: Account holder, with delivery
        cost3 = self.parser.calculate_total_cost(product1, tons, is_account_holder=True, include_delivery=True)
        self.assertEqual(cost3, Decimal('216.00')) # 10 * ($19.10 + $2.50)

        # Case 4: With delivery, but delivery cost is "CALL" (None)
        cost4 = self.parser.calculate_total_cost(product2, tons, is_account_holder=False, include_delivery=True)
        self.assertEqual(cost4, Decimal('500.00')) # 10 * $50, delivery is ignored

        # Case 5: Base price is "CALL" (None)
        cost5 = self.parser.calculate_total_cost(product3, tons)
        self.assertIsNone(cost5)

    def test_find_cheapest_product(self):
        """Test the logic for finding the cheapest product in a list."""
        products = self.parser.parse_csv(self.test_csv_path)
        tons = Decimal('10')

        # Scenario 1: Non-account holder, NO delivery
        # Cheap Stone ($10/ton) should be cheapest
        cheapest_no_delivery = self.parser.find_cheapest_product(products, tons, is_account_holder=False, include_delivery=False)
        self.assertIsNotNone(cheapest_no_delivery)
        cheapest_product, cost = cheapest_no_delivery
        self.assertEqual(cheapest_product.product_name, "Cheap Stone") # price is now $10.10
        self.assertEqual(cost, Decimal('101.00')) # 10 tons * $10.10/ton

        # Scenario 2: Account holder, WITH delivery
        # #89 Stone ($19.10 + $2.50 = $21.60/ton) should be cheaper than
        # Cheap Stone ($9.10 + $15.00 = $24.10/ton)
        cheapest_with_delivery = self.parser.find_cheapest_product(products, tons, is_account_holder=True, include_delivery=True)
        self.assertIsNotNone(cheapest_with_delivery)
        cheapest_product, cost = cheapest_with_delivery
        self.assertEqual(cheapest_product.product_name, "#89 Stone")
        self.assertEqual(cost, Decimal('216.00')) # 10 tons * ($19.10 + $2.50)/ton

        # Scenario 3: No products with valid prices
        # Create a product list where all prices are None
        invalid_products = [p for p in products if p.product_name == '8910s']
        cheapest_invalid = self.parser.find_cheapest_product(invalid_products, tons)
        self.assertIsNone(cheapest_invalid)

    def test_filter_products(self):
        """Test filtering products by location name and number."""
        all_products = self.parser.parse_csv(self.test_csv_path)

        # Scenario 1: Filter by location name (case-insensitive)
        cherokee_products = self.parser.filter_products(all_products, location_name="cherokee")
        self.assertEqual(len(cherokee_products), 2)
        self.assertEqual(cherokee_products[0].location_name, "Cherokee")

        # Scenario 2: Filter by location number
        laceys_spring_products = self.parser.filter_products(all_products, location_number="71501")
        self.assertEqual(len(laceys_spring_products), 1)
        self.assertEqual(laceys_spring_products[0].location_name, "Lacey's Spring")

        # Scenario 3: Filter by both name and number (matching)
        cherokee_594 = self.parser.filter_products(all_products, location_name="Cherokee", location_number="594")
        self.assertEqual(len(cherokee_594), 2)

        # Scenario 4: Filter by both name and number (mismatch)
        no_match = self.parser.filter_products(all_products, location_name="Cherokee", location_number="71501")
        self.assertEqual(len(no_match), 0)

        # Scenario 5: Filter with no criteria (should return original list)
        no_filters = self.parser.filter_products(all_products)
        self.assertEqual(len(no_filters), len(all_products))

    def test_logging_on_bad_price(self):
        """Test that a warning is logged for unparseable price strings."""
        with self.assertLogs('data_parser', level='WARNING') as cm:
            # The _clean_price method is internal, so we test it via the public parse_csv
            self.parser._clean_price("Invalid Price")
            self.assertIn("Could not parse price string to Decimal: 'Invalid Price'", cm.output[0])

    def test_parsing_without_surcharge(self):
        """Test that prices are not modified when no surcharge is provided."""
        # Create a new parser instance with no surcharge
        parser_no_surcharge = DataParser(surcharge=None)
        results = parser_no_surcharge.parse_csv(self.test_csv_path)

        # The price should be the original value from the file, not with $0.10 added
        self.assertEqual(results[0].price_non_account, Decimal('20.00'))
        self.assertEqual(results[0].price_account, Decimal('19.00'))

if __name__ == '__main__':
    unittest.main()