import unittest
import Solution as Solution
from Utility.ReturnValue import ReturnValue
from Tests.AbstractTest import AbstractTest
from Business.Customer import Customer, BadCustomer
from Business.Order import Order, BadOrder
from Business.Dish import Dish, BadDish
from datetime import datetime

"""
    Simple test, create one of your own
    make sure the tests' names start with test
"""


class Test(AbstractTest):
    def test_customer(self) -> None:
        c1 = Customer(1, "name", 21, "0123456789")
        self.assertEqual(ReturnValue.OK, Solution.add_customer(c1), "regular customer")
        c2 = Customer(2, None, 21, "Haifa")
        self.assertEqual(
            ReturnValue.BAD_PARAMS, Solution.add_customer(c2), "0123456789"
        )

    def test_customer_edge_cases(self) -> None:
        # --- 1. ALREADY_EXISTS TEST ---
        # Insert a valid customer, then try to insert a different customer with the SAME ID.
        c_base = Customer(100, "Alexander Veksler", 25, "0501234567")
        self.assertEqual(
            ReturnValue.OK, Solution.add_customer(c_base), "valid initial insertion"
        )

        c_duplicate_id = Customer(100, "Technion Student", 28, "0549876543")
        self.assertEqual(
            ReturnValue.ALREADY_EXISTS,
            Solution.add_customer(c_duplicate_id),
            "ID 100 already exists",
        )

        # --- 2. BAD_PARAMS: ID CONSTRAINTS ---
        # ID must be > 0
        c_id_zero = Customer(0, "Valid Name", 30, "0501234567")
        self.assertEqual(
            ReturnValue.BAD_PARAMS, Solution.add_customer(c_id_zero), "ID is exactly 0"
        )

        c_id_negative = Customer(-5, "Valid Name", 30, "0501234567")
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_customer(c_id_negative),
            "ID is negative",
        )

        # --- 3. BAD_PARAMS: AGE BOUNDARIES ---
        # Age must be strictly between 18 and 120
        c_age_under = Customer(101, "Valid Name", 17, "0501234567")
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_customer(c_age_under),
            "Age is 17 (too young)",
        )

        c_age_over = Customer(102, "Valid Name", 121, "0501234567")
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_customer(c_age_over),
            "Age is 121 (too old)",
        )

        # Testing exact acceptable boundaries (These should pass!)
        c_age_18 = Customer(103, "Valid Name", 18, "0501234567")
        self.assertEqual(
            ReturnValue.OK, Solution.add_customer(c_age_18), "Age is exactly 18"
        )

        c_age_120 = Customer(104, "Valid Name", 120, "0501234567")
        self.assertEqual(
            ReturnValue.OK, Solution.add_customer(c_age_120), "Age is exactly 120"
        )

        # --- 4. BAD_PARAMS: PHONE LENGTH ---
        # Phone must be EXACTLY 10 characters
        c_phone_short = Customer(105, "Valid Name", 30, "123456789")
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_customer(c_phone_short),
            "Phone is 9 characters",
        )

        c_phone_long = Customer(106, "Valid Name", 30, "01234567890")
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_customer(c_phone_long),
            "Phone is 11 characters",
        )

        # --- 5. BAD_PARAMS: NULL VALUES ---
        # None of the fields can be optional
        c_none_name = Customer(107, None, 30, "0501234567")
        self.assertEqual(
            ReturnValue.BAD_PARAMS, Solution.add_customer(c_none_name), "Name is None"
        )

        c_none_phone = Customer(108, "Valid Name", 30, None)
        self.assertEqual(
            ReturnValue.BAD_PARAMS, Solution.add_customer(c_none_phone), "Phone is None"
        )

        c_none_age = Customer(109, "Valid Name", None, "0501234567")
        self.assertEqual(
            ReturnValue.BAD_PARAMS, Solution.add_customer(c_none_age), "Age is None"
        )

    def test_get_customer_edge_cases(self) -> None:
        # --- 1. GET EXISTING CUSTOMER (Happy Path) ---
        c_valid = Customer(200, "Jane Doe", 30, "0521234567")
        Solution.add_customer(c_valid)

        # Fetch the customer we just added
        res_customer = Solution.get_customer(200)

        self.assertEqual(
            c_valid, res_customer, "Should return the exact matched customer object"
        )

        # --- 2. GET NON-EXISTENT CUSTOMER ---
        # ID 9999 hasn't been added
        res_missing = Solution.get_customer(9999)
        self.assertEqual(
            BadCustomer(),
            res_missing,
            "Should return BadCustomer when ID is not found in DB",
        )

        # --- 3. GET WITH INVALID ID BOUNDARIES ---
        # The schema requires cust_id > 0
        res_zero = Solution.get_customer(0)
        self.assertEqual(BadCustomer(), res_zero, "Should return BadCustomer for ID 0")

        res_negative = Solution.get_customer(-10)
        self.assertEqual(
            BadCustomer(), res_negative, "Should return BadCustomer for negative ID"
        )

    def test_delete_customer_edge_cases(self) -> None:
        # --- 1. SUCCESSFUL DELETION (Happy Path) ---
        c_to_delete = Customer(400, "Mark Delete", 55, "0541112222")
        Solution.add_customer(c_to_delete)

        # Delete the customer
        self.assertEqual(
            ReturnValue.OK,
            Solution.delete_customer(400),
            "Should return OK when an existing customer is deleted",
        )

        # Verify they are actually gone using your get_customer function
        self.assertEqual(
            BadCustomer(),
            Solution.get_customer(400),
            "Deleted customer should no longer be retrievable (should return BadCustomer)",
        )

        # --- 2. DELETING NON-EXISTENT CUSTOMER ---
        # ID 9999 was never added
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.delete_customer(9999),
            "Should return NOT_EXISTS for an ID that isn't in the database",
        )

        # --- 3. ILLEGAL IDs ---
        # 0 and negative numbers are illegal per your schema, so they definitely don't exist
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.delete_customer(0),
            "Should return NOT_EXISTS for ID 0",
        )
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.delete_customer(-5),
            "Should return NOT_EXISTS for negative ID",
        )

        # --- 4. DOUBLE DELETE ---
        c_double_delete = Customer(401, "Erase Me", 22, "0505554444")
        Solution.add_customer(c_double_delete)

        # First delete works
        self.assertEqual(
            ReturnValue.OK,
            Solution.delete_customer(401),
            "First deletion should succeed",
        )

        # Second delete should fail because they are already gone
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.delete_customer(401),
            "Deleting the same customer twice should return NOT_EXISTS the second time",
        )

    def test_add_order_edge_cases(self) -> None:
        # --- 1. HAPPY PATH & MICROSECONDS TEST ---
        # The assignment requires that a datetime with microseconds is successfully added.
        # datetime(year, month, day, hour, minute, second, microsecond)
        dt_with_microseconds = datetime(2023, 10, 25, 14, 30, 45, 123456)
        o_valid = Order(1, dt_with_microseconds, 15.5, "Technion City, Haifa", 5.0)

        self.assertEqual(
            ReturnValue.OK,
            Solution.add_order(o_valid),
            "Valid order (even with microseconds) should return OK",
        )

        # --- 2. ALREADY EXISTS (Duplicate ID) ---
        o_duplicate = Order(1, datetime.now(), 12.0, "Haifa University", 2.5)
        self.assertEqual(
            ReturnValue.ALREADY_EXISTS,
            Solution.add_order(o_duplicate),
            "Inserting an order with an existing ID (1) should return ALREADY_EXISTS",
        )

        # --- 3. BAD PARAMS: ID CONSTRAINTS (Must be > 0) ---
        o_id_zero = Order(0, datetime.now(), 10.0, "Valid Address", 2.0)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_order(o_id_zero),
            "Order ID 0 is illegal",
        )

        o_id_negative = Order(-5, datetime.now(), 10.0, "Valid Address", 2.0)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_order(o_id_negative),
            "Negative Order ID is illegal",
        )

        # --- 4. BAD PARAMS: DELIVERY FEE CONSTRAINTS (Must be >= 0) ---
        o_fee_negative = Order(2, datetime.now(), -1.5, "Valid Address", 2.0)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_order(o_fee_negative),
            "Negative delivery fee is illegal",
        )

        # Zero fee is valid (Free delivery!)
        o_fee_zero = Order(3, datetime.now(), 0.0, "Valid Address", 2.0)
        self.assertEqual(
            ReturnValue.OK,
            Solution.add_order(o_fee_zero),
            "Delivery fee of 0.0 should be OK",
        )

        # --- 5. BAD PARAMS: TIP CONSTRAINTS (Must be >= 0) ---
        o_tip_negative = Order(4, datetime.now(), 10.0, "Valid Address", -5.0)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_order(o_tip_negative),
            "Negative tip is illegal",
        )

        # Zero tip is valid (Bad customer, but valid data)
        o_tip_zero = Order(5, datetime.now(), 10.0, "Valid Address", 0.0)
        self.assertEqual(
            ReturnValue.OK, Solution.add_order(o_tip_zero), "Tip of 0.0 should be OK"
        )

        # --- 6. BAD PARAMS: DELIVERY ADDRESS CONSTRAINTS (Length >= 5) ---
        o_address_short = Order(6, datetime.now(), 10.0, "1234", 2.0)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_order(o_address_short),
            "Address with 4 characters is too short",
        )

        o_address_empty = Order(7, datetime.now(), 10.0, "", 2.0)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_order(o_address_empty),
            "Empty address is illegal",
        )

        # Address with exactly 5 characters should pass
        o_address_five = Order(8, datetime.now(), 10.0, "12345", 2.0)
        self.assertEqual(
            ReturnValue.OK,
            Solution.add_order(o_address_five),
            "Address with exactly 5 characters should be OK",
        )

        # --- 7. BAD PARAMS: NULL VALUES ---
        # Checking that your code correctly catches missing parameters
        o_null_address = Order(9, datetime.now(), 10.0, None, 2.0)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_order(o_null_address),
            "Address cannot be None",
        )

        o_null_date = Order(10, None, 10.0, "Valid Address", 2.0)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_order(o_null_date),
            "Date cannot be None",
        )

    def test_get_order_edge_cases(self) -> None:
        # --- 1. GET EXISTING ORDER (Happy Path) ---
        # Create and add a standard order
        dt_valid = datetime(2023, 11, 1, 14, 0, 0)
        o_valid = Order(200, dt_valid, 15.0, "Technion Campus", 10.0)
        Solution.add_order(o_valid)

        # Fetch the order we just added
        res_order = Solution.get_order(200)

        self.assertEqual(
            o_valid, res_order, "Should return the exact matched order object"
        )

        # --- 2. GET NON-EXISTENT ORDER ---
        # ID 9999 hasn't been added to the database
        res_missing = Solution.get_order(9999)
        self.assertEqual(
            BadOrder(),
            res_missing,
            "Should return BadOrder when order ID is not found in DB",
        )

        # --- 3. GET WITH INVALID ID BOUNDARIES ---
        # The schema strictly requires order_id > 0
        res_zero = Solution.get_order(0)
        self.assertEqual(BadOrder(), res_zero, "Should return BadOrder for ID 0")

        res_negative = Solution.get_order(-50)
        self.assertEqual(
            BadOrder(), res_negative, "Should return BadOrder for negative ID"
        )

    def test_delete_order_edge_cases(self) -> None:
        # --- 1. SUCCESSFUL DELETION (Happy Path) ---
        o_to_delete = Order(
            300, datetime(2023, 12, 1, 10, 0, 0), 12.0, "Delete St, Haifa", 5.0
        )
        Solution.add_order(o_to_delete)

        # Delete the order
        self.assertEqual(
            ReturnValue.OK,
            Solution.delete_order(300),
            "Should return OK when an existing order is deleted",
        )

        # Verify it is actually gone using your get_order function
        self.assertEqual(
            BadOrder(),
            Solution.get_order(300),
            "Deleted order should no longer be retrievable (should return BadOrder)",
        )

        # --- 2. DELETING NON-EXISTENT ORDER ---
        # ID 9999 was never added
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.delete_order(9999),
            "Should return NOT_EXISTS for an ID that isn't in the database",
        )

        # --- 3. ILLEGAL IDs ---
        # 0 and negative numbers are illegal, so they definitely don't exist
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.delete_order(0),
            "Should return NOT_EXISTS for ID 0",
        )
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.delete_order(-20),
            "Should return NOT_EXISTS for negative ID",
        )

        # --- 4. DOUBLE DELETE ---
        o_double_delete = Order(
            301, datetime(2023, 12, 1, 10, 0, 0), 12.0, "Delete St, Haifa", 5.0
        )
        Solution.add_order(o_double_delete)

        # First delete works
        self.assertEqual(
            ReturnValue.OK, Solution.delete_order(301), "First deletion should succeed"
        )

        # Second delete should fail because it is already gone
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.delete_order(301),
            "Deleting the same order twice should return NOT_EXISTS the second time",
        )

    def test_add_dish_edge_cases(self) -> None:
        # --- 1. ADD DISH: HAPPY PATH ---
        d_valid = Dish(500, "Spaghetti", 45.5, True)
        self.assertEqual(
            ReturnValue.OK, Solution.add_dish(d_valid), "Valid dish should return OK"
        )

        # --- 2. ADD DISH: ALREADY EXISTS ---
        # Same ID (500), completely different dish details
        d_duplicate = Dish(500, "Pizza Margherita", 50.0, False)
        self.assertEqual(
            ReturnValue.ALREADY_EXISTS,
            Solution.add_dish(d_duplicate),
            "Duplicate dish_id should return ALREADY_EXISTS",
        )

        # --- 3. BAD PARAMS: ID CONSTRAINTS (Must be > 0) ---
        d_id_zero = Dish(0, "Valid Name", 30.0, True)
        self.assertEqual(
            ReturnValue.BAD_PARAMS, Solution.add_dish(d_id_zero), "ID 0 is illegal"
        )

        d_id_negative = Dish(-10, "Valid Name", 30.0, True)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_dish(d_id_negative),
            "Negative ID is illegal",
        )

        # --- 4. BAD PARAMS: PRICE CONSTRAINTS (Must be > 0) ---
        # Note: Unlike delivery fee, price cannot be 0.
        d_price_zero = Dish(501, "Valid Name", 0.0, True)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_dish(d_price_zero),
            "Price of 0 is illegal (must be strictly > 0)",
        )

        d_price_negative = Dish(502, "Valid Name", -15.0, True)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_dish(d_price_negative),
            "Negative price is illegal",
        )

        # --- 5. BAD PARAMS: NAME CONSTRAINTS (Length >= 4) ---
        d_name_short = Dish(503, "Pie", 20.0, True)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_dish(d_name_short),
            "Name with 3 characters is too short",
        )

        d_name_empty = Dish(504, "", 20.0, True)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_dish(d_name_empty),
            "Empty name is illegal",
        )

        # Exactly 4 characters should successfully pass!
        d_name_exact = Dish(505, "Soup", 15.0, True)
        self.assertEqual(
            ReturnValue.OK,
            Solution.add_dish(d_name_exact),
            "Name with exactly 4 characters should be OK",
        )

        # --- 6. BAD PARAMS: NULL VALUES ---
        d_null_name = Dish(506, None, 20.0, True)
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.add_dish(d_null_name),
            "Name cannot be None",
        )

    def test_get_dish_edge_cases(self) -> None:
        # --- 1. GET EXISTING DISH (Happy Path) ---
        d_to_get = Dish(600, "Cheeseburger", 55.0, True)
        Solution.add_dish(d_to_get)

        res_dish = Solution.get_dish(600)

        # This triggers the __eq__ method you wrote in Dish.py!
        self.assertEqual(
            d_to_get, res_dish, "Should return the exact matched dish object"
        )

        # --- 2. GET NON-EXISTENT DISH ---
        res_missing = Solution.get_dish(9999)
        self.assertEqual(
            BadDish(), res_missing, "Should return BadDish when ID is not found in DB"
        )

        # --- 3. GET WITH INVALID ID BOUNDARIES ---
        res_zero = Solution.get_dish(0)
        self.assertEqual(BadDish(), res_zero, "Should return BadDish for ID 0")

        res_negative = Solution.get_dish(-15)
        self.assertEqual(
            BadDish(), res_negative, "Should return BadDish for negative ID"
        )

    def test_update_dish_price_edge_cases(self) -> None:
        # Setup: Create one active dish and one inactive dish
        d_active = Dish(700, "Active Salad", 25.0, True)
        d_inactive = Dish(701, "Old Soup", 15.0, False)
        Solution.add_dish(d_active)
        Solution.add_dish(d_inactive)

        # --- 1. SUCCESSFUL UPDATE (Happy Path) ---
        self.assertEqual(
            ReturnValue.OK,
            Solution.update_dish_price(700, 28.5),
            "Should return OK when an active dish price is updated"
        )

        # Verify the price actually changed in the database
        res_updated_dish = Solution.get_dish(700)
        self.assertEqual(
            28.5,
            res_updated_dish.get_price(),
            "The price should be updated to 28.5 in the database"
        )

        # --- 2. UPDATE INACTIVE DISH ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_price(701, 20.0),
            "Should return NOT_EXISTS if trying to update an inactive dish"
        )

        # --- 3. UPDATE NON-EXISTENT / ILLEGAL ID ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_price(9999, 10.0),
            "Should return NOT_EXISTS for an ID that isn't in the database"
        )

        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_price(-5, 10.0),
            "Should return NOT_EXISTS for illegal negative ID"
        )

        # --- 4. BAD PARAMS: ILLEGAL PRICES ---
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.update_dish_price(700, -5.0),
            "Negative price should return BAD_PARAMS"
        )

        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.update_dish_price(700, 0.0),
            "Price of 0 should return BAD_PARAMS (Must be strictly > 0)"
        )

# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
