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
            "Should return OK when an active dish price is updated",
        )

        # Verify the price actually changed in the database
        res_updated_dish = Solution.get_dish(700)
        self.assertEqual(
            28.5,
            res_updated_dish.get_price(),
            "The price should be updated to 28.5 in the database",
        )

        # --- 2. UPDATE INACTIVE DISH ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_price(701, 20.0),
            "Should return NOT_EXISTS if trying to update an inactive dish",
        )

        # --- 3. UPDATE NON-EXISTENT / ILLEGAL ID ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_price(9999, 10.0),
            "Should return NOT_EXISTS for an ID that isn't in the database",
        )

        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_price(-5, 10.0),
            "Should return NOT_EXISTS for illegal negative ID",
        )

        # --- 4. BAD PARAMS: ILLEGAL PRICES ---
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.update_dish_price(700, -5.0),
            "Negative price should return BAD_PARAMS",
        )

        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.update_dish_price(700, 0.0),
            "Price of 0 should return BAD_PARAMS (Must be strictly > 0)",
        )

    def test_update_dish_active_status_edge_cases(self) -> None:
        # Setup: Create a single active dish
        d_status = Dish(800, "Status Burger", 30.0, True)
        Solution.add_dish(d_status)

        # --- 1. SUCCESSFUL UPDATE (Happy Path) ---
        # Update to False (Inactive)
        self.assertEqual(
            ReturnValue.OK,
            Solution.update_dish_active_status(800, False),
            "Should return OK when dish status is updated to False",
        )

        # Verify the status actually changed in the database
        res_dish_inactive = Solution.get_dish(800)
        self.assertEqual(
            False,
            res_dish_inactive.get_is_active(),
            "The dish should now be inactive in the database",
        )

        # Update back to True (Active)
        self.assertEqual(
            ReturnValue.OK,
            Solution.update_dish_active_status(800, True),
            "Should return OK when dish status is updated back to True",
        )

        # Verify it changed back
        res_dish_active = Solution.get_dish(800)
        self.assertEqual(
            True,
            res_dish_active.get_is_active(),
            "The dish should be active again in the database",
        )

        # --- 2. UPDATE NON-EXISTENT / ILLEGAL ID ---
        # ID 9999 does not exist
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_active_status(9999, False),
            "Should return NOT_EXISTS for an ID that isn't in the database",
        )

        # ID 0 is illegal per the schema constraints
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_active_status(0, True),
            "Should return NOT_EXISTS for illegal ID 0",
        )

        # Negative IDs are illegal
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.update_dish_active_status(-10, False),
            "Should return NOT_EXISTS for illegal negative ID",
        )

    def test_customer_placed_order_edge_cases(self) -> None:
        # --- SETUP: Create customers and orders ---
        c_link_1 = Customer(900, "Link Tester", 25, "0501112222")
        c_link_2 = Customer(903, "Other Tester", 30, "0503334444")
        Solution.add_customer(c_link_1)
        Solution.add_customer(c_link_2)

        o_link_1 = Order(901, datetime(2023, 1, 1, 10, 0, 0), 10.0, "Address 1", 2.0)
        o_link_2 = Order(902, datetime(2023, 1, 1, 10, 0, 0), 10.0, "Address 2", 2.0)
        Solution.add_order(o_link_1)
        Solution.add_order(o_link_2)

        # --- 1. SUCCESSFUL LINK (Happy Path) ---
        self.assertEqual(
            ReturnValue.OK,
            Solution.customer_placed_order(900, 901),
            "Should return OK when valid customer and order are linked",
        )

        # --- 2. ALREADY EXISTS (Order already belongs to someone) ---
        # Same customer trying again (Triggers UNIQUE_VIOLATION)
        self.assertEqual(
            ReturnValue.ALREADY_EXISTS,
            Solution.customer_placed_order(900, 901),
            "Should return ALREADY_EXISTS if order is already linked",
        )

        # Different customer trying to claim an already linked order (Triggers UNIQUE_VIOLATION)
        self.assertEqual(
            ReturnValue.ALREADY_EXISTS,
            Solution.customer_placed_order(903, 901),
            "Should return ALREADY_EXISTS even if a different customer tries to claim it",
        )

        # --- 3. NOT EXISTS: MISSING CUSTOMER OR ORDER (Triggers FOREIGN_KEY_VIOLATION) ---
        # Missing customer, valid order
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_placed_order(9999, 902),
            "Should return NOT_EXISTS for non-existent customer",
        )

        # Valid customer, missing order
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_placed_order(900, 9999),
            "Should return NOT_EXISTS for non-existent order",
        )

        # --- 4. NOT EXISTS: ILLEGAL IDs (Triggers FOREIGN_KEY_VIOLATION) ---
        # Since negative IDs aren't in the database, they will safely trigger NOT_EXISTS
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_placed_order(-5, 902),
            "Should return NOT_EXISTS for illegal negative customer_id",
        )

        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_placed_order(900, 0),
            "Should return NOT_EXISTS for illegal order_id of 0",
        )

    def test_get_customer_that_placed_order_edge_cases(self) -> None:
        # --- SETUP: Create customer, order, and link them ---
        c_buyer = Customer(1000, "View Tester", 22, "0509998888")
        o_purchased = Order(1001, datetime(2023, 5, 5, 12, 0, 0), 10.0, "View St", 5.0)

        Solution.add_customer(c_buyer)
        Solution.add_order(o_purchased)
        Solution.customer_placed_order(1000, 1001)

        # --- 1. SUCCESSFUL RETRIEVAL (Happy Path) ---
        res_customer = Solution.get_customer_that_placed_order(1001)

        self.assertEqual(
            c_buyer,
            res_customer,
            "Should use the view to return the exact customer who placed the order",
        )

        # --- 2. ORDER EXISTS, BUT NOT LINKED TO ANY CUSTOMER ---
        o_unlinked = Order(1002, datetime(2023, 5, 5, 12, 0, 0), 10.0, "Ghost St", 5.0)
        Solution.add_order(o_unlinked)

        res_ghost_customer = Solution.get_customer_that_placed_order(1002)
        self.assertEqual(
            BadCustomer(),
            res_ghost_customer,
            "Should return BadCustomer if the order exists but isn't linked to anyone",
        )

        # --- 3. ORDER DOES NOT EXIST / ILLEGAL ID ---
        self.assertEqual(
            BadCustomer(),
            Solution.get_customer_that_placed_order(9999),
            "Should return BadCustomer for an order ID that isn't in the database",
        )

        self.assertEqual(
            BadCustomer(),
            Solution.get_customer_that_placed_order(-5),
            "Should return BadCustomer for illegal negative order ID",
        )

    def test_order_contains_dish_edge_cases(self) -> None:
        # --- SETUP: Create Orders and Dishes ---
        o_target = Order(2000, datetime(2023, 6, 1, 10, 0, 0), 10.0, "Hungry St", 5.0)
        Solution.add_order(o_target)

        d_active = Dish(2001, "Active Fries", 15.0, True)
        d_inactive = Dish(2002, "Inactive Burger", 30.0, False)
        Solution.add_dish(d_active)
        Solution.add_dish(d_inactive)

        # --- 1. SUCCESSFUL ADDITION (Happy Path) ---
        self.assertEqual(
            ReturnValue.OK,
            Solution.order_contains_dish(2000, 2001, 2),
            "Should return OK when adding an active dish to a valid order",
        )

        # --- 2. ALREADY EXISTS (Dish already in this specific order) ---
        self.assertEqual(
            ReturnValue.ALREADY_EXISTS,
            Solution.order_contains_dish(2000, 2001, 1),
            "Should return ALREADY_EXISTS if dish is already in the order",
        )

        # --- 3. NOT EXISTS: INACTIVE DISH ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.order_contains_dish(2000, 2002, 1),
            "Should return NOT_EXISTS if the dish is inactive",
        )

        # --- 4. NOT EXISTS: MISSING IDS ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.order_contains_dish(9999, 2001, 1),
            "Should return NOT_EXISTS for non-existent order_id",
        )

        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.order_contains_dish(2000, 9999, 1),
            "Should return NOT_EXISTS for non-existent dish_id",
        )

        # --- 5. BAD PARAMS: AMOUNT ---
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.order_contains_dish(2000, 2001, -5),
            "Should return BAD_PARAMS for negative amount",
        )
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.order_contains_dish(2000, 2001, 0),
            "Should return BAD_PARAMS for amount of 0",
        )

    def test_order_does_not_contain_dish_edge_cases(self) -> None:
        # --- SETUP: Create Order, Dishes, and Link them ---
        o_remove = Order(3000, datetime(2023, 7, 1, 10, 0, 0), 10.0, "Remove St", 5.0)
        Solution.add_order(o_remove)

        d_keep = Dish(3001, "Keep Fries", 15.0, True)
        d_toss = Dish(3002, "Toss Burger", 30.0, True)
        d_never_added = Dish(3003, "Never Added Soup", 20.0, True)
        Solution.add_dish(d_keep)
        Solution.add_dish(d_toss)
        Solution.add_dish(d_never_added)

        # Add the dishes to the order
        Solution.order_contains_dish(3000, 3001, 2)
        Solution.order_contains_dish(3000, 3002, 1)

        # --- 1. SUCCESSFUL REMOVAL (Happy Path) ---
        self.assertEqual(
            ReturnValue.OK,
            Solution.order_does_not_contain_dish(3000, 3002),
            "Should return OK when successfully removing a dish from an order",
        )

        # --- 2. DOUBLE DELETION (Dish already removed) ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.order_does_not_contain_dish(3000, 3002),
            "Should return NOT_EXISTS if trying to remove a dish that is no longer in the order",
        )

        # --- 3. NOT EXISTS: DISH NEVER ADDED TO THIS ORDER ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.order_does_not_contain_dish(3000, 3003),
            "Should return NOT_EXISTS if the dish exists in the DB but is not in this specific order",
        )

        # --- 4. NOT EXISTS: MISSING IDS ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.order_does_not_contain_dish(9999, 3001),
            "Should return NOT_EXISTS for non-existent order_id",
        )

        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.order_does_not_contain_dish(3000, 9999),
            "Should return NOT_EXISTS for non-existent dish_id",
        )

        # --- 5. NOT EXISTS: ILLEGAL IDS ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.order_does_not_contain_dish(-5, 3001),
            "Should return NOT_EXISTS for illegal negative order_id",
        )

    def test_get_all_order_items_edge_cases(self) -> None:
        # --- SETUP: Create Order and Dishes ---
        o_list = Order(4000, datetime(2023, 8, 1, 10, 0, 0), 10.0, "List St", 5.0)
        Solution.add_order(o_list)

        # Create dishes out of order
        d_3 = Dish(4003, "Fries", 15.0, True)
        d_1 = Dish(4001, "Burger", 30.0, True)
        d_2 = Dish(4002, "Soda", 5.0, True)
        Solution.add_dish(d_3)
        Solution.add_dish(d_1)
        Solution.add_dish(d_2)

        # Add them to the order out of order
        Solution.order_contains_dish(4000, 4003, 2)
        Solution.order_contains_dish(4000, 4001, 1)
        Solution.order_contains_dish(4000, 4002, 3)

        # --- 1. SUCCESSFUL RETRIEVAL & SORTING (Happy Path) ---
        items = Solution.get_all_order_items(4000)

        self.assertEqual(3, len(items), "Should return exactly 3 items")

        # Verify the ASCENDING sort order (4001, then 4002, then 4003)
        self.assertEqual(4001, items[0].get_dish_id(), "First item should be dish 4001")
        self.assertEqual(
            4002, items[1].get_dish_id(), "Second item should be dish 4002"
        )
        self.assertEqual(4003, items[2].get_dish_id(), "Third item should be dish 4003")

        # Verify the data was mapped correctly
        self.assertEqual(1, items[0].get_amount(), "Amount for dish 4001 should be 1")
        self.assertEqual(
            30.0, items[0].get_price(), "Price for dish 4001 should be 30.0"
        )

        # --- 2. EMPTY ORDER ---
        o_empty = Order(4005, datetime(2023, 8, 1, 10, 0, 0), 10.0, "Empty St", 5.0)
        Solution.add_order(o_empty)

        res_empty = Solution.get_all_order_items(4005)
        self.assertEqual(
            [], res_empty, "Should return an empty list for an order with no dishes"
        )

        # --- 3. NOT EXISTS: MISSING / ILLEGAL ORDER ID ---
        res_missing = Solution.get_all_order_items(9999)
        self.assertEqual(
            [], res_missing, "Should return an empty list for a non-existent order"
        )

        res_illegal = Solution.get_all_order_items(-5)
        self.assertEqual(
            [],
            res_illegal,
            "Should return an empty list for an illegal negative order ID",
        )

    def test_customer_rated_dish_edge_cases(self) -> None:
        # --- SETUP: Create Customer and Dishes ---
        c_rater = Customer(5000, "Food Critic", 45, "0505556666")
        Solution.add_customer(c_rater)

        d_pasta = Dish(5001, "Pasta", 40.0, True)
        d_pizza = Dish(5002, "Pizza", 50.0, True)
        Solution.add_dish(d_pasta)
        Solution.add_dish(d_pizza)

        # --- 1. SUCCESSFUL RATING (Happy Path) ---
        self.assertEqual(
            ReturnValue.OK,
            Solution.customer_rated_dish(5000, 5001, 5),
            "Should return OK when a valid customer rates a valid dish",
        )

        self.assertEqual(
            ReturnValue.OK,
            Solution.customer_rated_dish(5000, 5002, 4),
            "Should return OK when the SAME customer rates a DIFFERENT dish",
        )

        # --- 2. ALREADY EXISTS (Rating the same dish twice) ---
        self.assertEqual(
            ReturnValue.ALREADY_EXISTS,
            Solution.customer_rated_dish(5000, 5001, 3),
            "Should return ALREADY_EXISTS if the customer tries to rate the same dish again",
        )

        # --- 3. BAD PARAMS: INVALID RATINGS ---
        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.customer_rated_dish(5000, 5001, 6),
            "Should return BAD_PARAMS for a rating > 5",
        )

        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.customer_rated_dish(5000, 5001, 0),
            "Should return BAD_PARAMS for a rating < 1",
        )

        self.assertEqual(
            ReturnValue.BAD_PARAMS,
            Solution.customer_rated_dish(5000, 5001, -2),
            "Should return BAD_PARAMS for a negative rating",
        )

        # --- 4. NOT EXISTS: MISSING IDS ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_rated_dish(9999, 5001, 5),
            "Should return NOT_EXISTS for a non-existent customer_id",
        )

        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_rated_dish(5000, 9999, 5),
            "Should return NOT_EXISTS for a non-existent dish_id",
        )

        # --- 5. NOT EXISTS: ILLEGAL IDS ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_rated_dish(-5, 5001, 5),
            "Should return NOT_EXISTS for an illegal negative customer_id",
        )

    def test_customer_deleted_rating_on_dish_edge_cases(self) -> None:
        # --- SETUP: Create Customer, Dishes, and Ratings ---
        c_deleter = Customer(6000, "Change Mind", 30, "0504443333")
        Solution.add_customer(c_deleter)

        d_salad = Dish(6001, "Salad", 25.0, True)
        d_soup = Dish(6002, "Soup", 20.0, True)
        Solution.add_dish(d_salad)
        Solution.add_dish(d_soup)

        # Customer rates the salad
        Solution.customer_rated_dish(6000, 6001, 4)

        # --- 1. SUCCESSFUL DELETION (Happy Path) ---
        self.assertEqual(
            ReturnValue.OK,
            Solution.customer_deleted_rating_on_dish(6000, 6001),
            "Should return OK when successfully deleting an existing rating",
        )

        # --- 2. DOUBLE DELETION (Rating no longer exists) ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_deleted_rating_on_dish(6000, 6001),
            "Should return NOT_EXISTS if trying to delete a rating that was already removed",
        )

        # --- 3. NOT EXISTS: NEVER RATED IN THE FIRST PLACE ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_deleted_rating_on_dish(6000, 6002),
            "Should return NOT_EXISTS if the customer never rated this dish",
        )

        # --- 4. NOT EXISTS: MISSING IDS ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_deleted_rating_on_dish(9999, 6001),
            "Should return NOT_EXISTS for non-existent customer_id",
        )

        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_deleted_rating_on_dish(6000, 9999),
            "Should return NOT_EXISTS for non-existent dish_id",
        )

        # --- 5. NOT EXISTS: ILLEGAL IDS ---
        self.assertEqual(
            ReturnValue.NOT_EXISTS,
            Solution.customer_deleted_rating_on_dish(-5, 6001),
            "Should return NOT_EXISTS for illegal negative customer_id",
        )

    def test_get_all_customer_ratings_edge_cases(self) -> None:
        # --- SETUP: Create Customer, Dishes, and Ratings ---
        c_reviewer = Customer(7000, "Foodie Tester", 28, "0507778888")
        Solution.add_customer(c_reviewer)

        # Create dishes out of order
        d_z = Dish(7003, "Zucchini", 15.0, True)
        d_x = Dish(7001, "Xtra Burger", 30.0, True)
        d_y = Dish(7002, "Yam Soup", 10.0, True)
        Solution.add_dish(d_z)
        Solution.add_dish(d_x)
        Solution.add_dish(d_y)

        # Add ratings out of order
        Solution.customer_rated_dish(7000, 7003, 4)
        Solution.customer_rated_dish(7000, 7001, 5)
        Solution.customer_rated_dish(7000, 7002, 3)

        # --- 1. SUCCESSFUL RETRIEVAL & SORTING (Happy Path) ---
        ratings = Solution.get_all_customer_ratings(7000)

        self.assertEqual(3, len(ratings), "Should return exactly 3 rating tuples")

        # Verify the ASCENDING sort order and tuple structure: (dish_id, rating)
        self.assertEqual(
            (7001, 5), ratings[0], "First tuple should be dish 7001 with rating 5"
        )
        self.assertEqual(
            (7002, 3), ratings[1], "Second tuple should be dish 7002 with rating 3"
        )
        self.assertEqual(
            (7003, 4), ratings[2], "Third tuple should be dish 7003 with rating 4"
        )

        # --- 2. EMPTY RATINGS ---
        c_quiet = Customer(7005, "Quiet Diner", 40, "0509991111")
        Solution.add_customer(c_quiet)

        res_empty = Solution.get_all_customer_ratings(7005)
        self.assertEqual(
            [], res_empty, "Should return an empty list for a customer with no ratings"
        )

        # --- 3. NOT EXISTS: MISSING / ILLEGAL CUSTOMER ID ---
        res_missing = Solution.get_all_customer_ratings(9999)
        self.assertEqual(
            [], res_missing, "Should return an empty list for a non-existent customer"
        )

        res_illegal = Solution.get_all_customer_ratings(-5)
        self.assertEqual(
            [],
            res_illegal,
            "Should return an empty list for an illegal negative customer ID",
        )


# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
