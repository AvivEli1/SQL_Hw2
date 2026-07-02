from typing import List, Tuple
from psycopg2 import sql
from datetime import date, datetime
import Utility.DBConnector as Connector
from Utility.ReturnValue import ReturnValue
from Utility.Exceptions import DatabaseException
from Business.Customer import Customer, BadCustomer
from Business.Order import Order, BadOrder
from Business.Dish import Dish, BadDish
from Business.OrderDish import OrderDish


# ---------------------------------- CRUD API: ----------------------------------
# Basic database functions


def create_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()
        query = "CREATE TABLE Customers (cust_id INTEGER PRIMARY KEY CHECK (cust_id > 0), full_name TEXT NOT NULL, age INTEGER NOT NULL CHECK (age >= 18 AND age <= 120), phone VARCHAR(10) NOT NULL CHECK (LENGTH(phone) = 10));"
        conn.execute(query)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def clear_tables() -> None:
    # TODO: implement
    pass


def drop_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()

        # Add all the tables your assignment requires here.
        # IF EXISTS prevents errors if the table was already dropped.
        # CASCADE forces the database to also drop any foreign key constraints tied to these tables.
        query = "DROP TABLE IF EXISTS Customers CASCADE"

        conn.execute(query)

    except Exception as e:
        print(f"Error dropping tables: {e}")

    finally:
        if conn is not None:
            conn.close()


# CRUD API


def add_customer(customer: Customer) -> ReturnValue:
    if customer is None:
        return ReturnValue.BAD_PARAMS

    cust_id = customer.get_cust_id()
    full_name = customer.get_full_name()
    age = customer.get_age()
    phone = customer.get_phone()

    # Check for None values (Constraint 5: not null)
    if cust_id is None or full_name is None or age is None or phone is None:
        return ReturnValue.BAD_PARAMS

    # Constraint 2: cust_id is positive (>0)
    if cust_id <= 0:
        return ReturnValue.BAD_PARAMS

    # Constraint 3: age should be between 18 and 120
    if not (18 <= age <= 120):
        return ReturnValue.BAD_PARAMS

    # Constraint 4: The phone number should contain exactly 10 characters
    if len(phone) != 10:
        return ReturnValue.BAD_PARAMS

    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "INSERT INTO Customers (cust_id, full_name, age, phone) VALUES ({id}, {name}, {age}, {phone})"
        ).format(
            id=sql.Literal(cust_id),
            name=sql.Literal(full_name),
            age=sql.Literal(age),
            phone=sql.Literal(phone),
        )

        conn.execute(query)
        return ReturnValue.OK

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        print(e)
        return ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION as e:
        print(e)
        return ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION as e:
        print(e)
        return ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        print(e)
        return ReturnValue.BAD_PARAMS
    except Exception as e:
        print(e)
        return ReturnValue.ERROR
    finally:
        if conn is not None:
            conn.close()


def get_customer(customer_id: int) -> Customer:
    conn = None
    customer = BadCustomer()

    try:
        conn = Connector.DBConnector()

        query = sql.SQL("SELECT * FROM Customers WHERE cust_id={id}").format(
            id=sql.Literal(customer_id)
        )

        # Execute the query and unpack the rows affected and the ResultSet
        rows_effected, result = conn.execute(query)

        # Check if the result set contains any rows
        if result.size() > 0:
            row = result[0]

            customer = Customer(
                cust_id=row["cust_id"],
                full_name=row["full_name"],
                age=row["age"],
                phone=row["phone"],
            )

    except DatabaseException.ConnectionInvalid as e:
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
        return customer


def delete_customer(customer_id: int) -> ReturnValue:
    conn = None
    result = ReturnValue.ERROR

    try:
        conn = Connector.DBConnector()

        query = sql.SQL("DELETE FROM Customers WHERE cust_id={id}").format(
            id=sql.Literal(customer_id)
        )

        # Execute the query and capture how many rows were deleted
        rows_effected, _ = conn.execute(query)

        # If rows_effected is > 0, the customer existed and was deleted
        if rows_effected > 0:
            result = ReturnValue.OK
        else:
            # If 0 rows were affected, the ID either doesn't exist or is illegal (like -5)
            result = ReturnValue.NOT_EXISTS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        result = ReturnValue.ERROR
    except Exception as e:
        print(e)
        result = ReturnValue.ERROR
    finally:
        if conn is not None:
            conn.close()
        return result


def add_order(order: Order) -> ReturnValue:
    # TODO: implement
    pass


def get_order(order_id: int) -> Order:
    # TODO: implement
    pass


def delete_order(order_id: int) -> ReturnValue:
    # TODO: implement
    pass


def add_dish(dish: Dish) -> ReturnValue:
    # TODO: implement
    pass


def get_dish(dish_id: int) -> Dish:
    # TODO: implement
    pass


def update_dish_price(dish_id: int, price: float) -> ReturnValue:
    # TODO: implement
    pass


def update_dish_active_status(dish_id: int, is_active: bool) -> ReturnValue:
    # TODO: implement
    pass


def customer_placed_order(customer_id: int, order_id: int) -> ReturnValue:
    # TODO: implement
    pass


def get_customer_that_placed_order(order_id: int) -> Customer:
    # TODO: implement
    pass


def order_contains_dish(order_id: int, dish_id: int, amount: int) -> ReturnValue:
    # TODO: implement
    pass


def order_does_not_contain_dish(order_id: int, dish_id: int) -> ReturnValue:
    # TODO: implement
    pass


def get_all_order_items(order_id: int) -> List[OrderDish]:
    # TODO: implement
    pass


def customer_rated_dish(cust_id: int, dish_id: int, rating: int) -> ReturnValue:
    # TODO: implement
    pass


def customer_deleted_rating_on_dish(cust_id: int, dish_id: int) -> ReturnValue:
    # TODO: implement
    pass


def get_all_customer_ratings(cust_id: int) -> List[Tuple[int, int]]:
    # TODO: implement
    pass


# ---------------------------------- BASIC API: ----------------------------------

# Basic API


def get_order_total_price(order_id: int) -> float:
    # TODO: implement
    pass


def get_customers_spent_max_avg_amount_money() -> List[int]:
    # TODO: implement
    pass


def get_most_profitable_dish_in_period(start: datetime, end: datetime) -> Dish:
    # TODO: implement
    pass


def did_customer_order_top_rated_dishes(cust_id: int) -> bool:
    # TODO: implement
    pass


# ---------------------------------- ADVANCED API: ----------------------------------

# Advanced API


def get_customers_rated_but_not_ordered() -> List[int]:
    # TODO: implement
    pass


def get_non_worth_price_increase() -> List[int]:
    # TODO: implement
    pass


def get_cumulative_profit_per_month(year: int) -> List[Tuple[int, float]]:
    # TODO: implement
    pass


def get_potential_dish_recommendations(cust_id: int) -> List[int]:
    # TODO: implement
    pass
