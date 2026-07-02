import unittest
import Solution as Solution
from Utility.ReturnValue import ReturnValue
from Tests.AbstractTest import AbstractTest
from Business.Customer import Customer, BadCustomer

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


# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
