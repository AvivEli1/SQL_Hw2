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


# Helper functions


def _map_row_to_customer(row: dict) -> Customer:
    return Customer(
        cust_id=row["cust_id"],
        full_name=row["full_name"],
        age=row["age"],
        phone=row["phone"],
    )


def _map_row_to_order(row: dict) -> Order:
    return Order(
        order_id=row["order_id"],
        date=row["date"],
        delivery_fee=row["delivery_fee"],
        delivery_address=row["delivery_address"],
        tip=row["tip"],
    )


def _map_row_to_dish(row: dict) -> Dish:
    return Dish(
        dish_id=row["dish_id"],
        name=row["name"],
        price=row["price"],
        is_active=row["is_active"],
    )


# ---------------------------------- CRUD API: ----------------------------------
# Basic database functions


def create_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()

        # 1. Base Tables (Parents)
        query_customers = """
                          CREATE TABLE Customers
                          (
                              cust_id INTEGER PRIMARY KEY CHECK (cust_id > 0),
                              full_name TEXT NOT NULL,
                              age INTEGER NOT NULL CHECK (age >= 18 AND age <= 120),
                              phone TEXT NOT NULL CHECK (LENGTH(phone) = 10)
                          );"""
        query_orders = """
                       CREATE TABLE Orders
                       (
                           order_id INTEGER PRIMARY KEY CHECK (order_id > 0),
                           date TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
                           delivery_fee DECIMAL NOT NULL CHECK (delivery_fee >= 0),
                           delivery_address TEXT NOT NULL CHECK (LENGTH(delivery_address) >= 5),
                           tip DECIMAL NOT NULL CHECK (tip >= 0)
                       );"""
        query_dishes = """
                       CREATE TABLE Dishes
                       (
                           dish_id INTEGER PRIMARY KEY CHECK (dish_id > 0),
                           name TEXT NOT NULL CHECK (LENGTH(name) >= 4),
                           price DECIMAL NOT NULL CHECK (price > 0),
                           is_active BOOLEAN NOT NULL
                       );"""

        # 2. Linking Tables (Children)
        query_customer_orders = """
                                CREATE TABLE CustomerOrders
                                (
                                    customer_id INTEGER NOT NULL REFERENCES Customers (cust_id) ON DELETE CASCADE,
                                    order_id INTEGER PRIMARY KEY REFERENCES Orders (order_id) ON DELETE CASCADE
                                );"""
        query_order_dishes = """
                             CREATE TABLE OrderDishes
                             (
                                 order_id INTEGER NOT NULL REFERENCES Orders (order_id) ON DELETE CASCADE,
                                 dish_id INTEGER NOT NULL REFERENCES Dishes (dish_id) ON DELETE CASCADE,
                                 amount INTEGER NOT NULL CHECK (amount > 0),
                                 price DECIMAL NOT NULL CHECK (price > 0),
                                 PRIMARY KEY (order_id, dish_id)
                             );"""
        query_dish_ratings = """
                             CREATE TABLE DishRatings
                             (
                                 cust_id INTEGER NOT NULL REFERENCES Customers (cust_id) ON DELETE CASCADE,
                                 dish_id INTEGER NOT NULL REFERENCES Dishes (dish_id) ON DELETE CASCADE,
                                 rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                                 PRIMARY KEY (cust_id, dish_id)
                             );"""
        # 3.Views
        query_view_order_customers = """
                                     CREATE VIEW vw_OrderCustomers AS
                                     SELECT co.order_id, c.cust_id, c.full_name, c.age, c.phone
                                     FROM CustomerOrders co
                                              INNER JOIN Customers c ON co.customer_id = c.cust_id;
                                     """

        # 1. Base Tables (Parents)
        conn.execute(query_customers)
        conn.execute(query_orders)
        conn.execute(query_dishes)

        # 2. Linking Tables (Children)
        conn.execute(query_customer_orders)
        conn.execute(query_order_dishes)
        conn.execute(query_dish_ratings)

        # 3.Views
        conn.execute(query_view_order_customers)

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def clear_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = """
                DELETE
                FROM DishRatings;
                DELETE
                FROM OrderDishes;
                DELETE
                FROM CustomerOrders;
                DELETE
                FROM Dishes;
                DELETE
                FROM Orders;
                DELETE
                FROM Customers;
                """
        conn.execute(query)

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def drop_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = """
                DROP VIEW IF EXISTS vw_OrderCustomers CASCADE;

                DROP TABLE IF EXISTS DishRatings, OrderDishes, CustomerOrders CASCADE;
                DROP TABLE IF EXISTS Dishes, Orders, Customers CASCADE; \
                """
        conn.execute(query)

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


# CRUD API


def add_customer(customer: Customer) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "INSERT INTO Customers (cust_id, full_name, age, phone) VALUES ({id}, {name}, {age}, {phone})"
        ).format(
            id=sql.Literal(customer.get_cust_id()),
            name=sql.Literal(customer.get_full_name()),
            age=sql.Literal(customer.get_age()),
            phone=sql.Literal(customer.get_phone()),
        )

        conn.execute(query)
        return ReturnValue.OK

    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS

    except (
        DatabaseException.NOT_NULL_VIOLATION,
        DatabaseException.CHECK_VIOLATION,
        DatabaseException.FOREIGN_KEY_VIOLATION,
    ) as e:
        print(e)
        return ReturnValue.BAD_PARAMS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

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

        rows_effected, result = conn.execute(query)

        if rows_effected > 0:
            row = result[0]
            customer = _map_row_to_customer(row)

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

    try:
        conn = Connector.DBConnector()

        query = sql.SQL("DELETE FROM Customers WHERE cust_id={id}").format(
            id=sql.Literal(customer_id)
        )

        rows_effected, _ = conn.execute(query)

        if rows_effected > 0:
            return ReturnValue.OK
        else:
            return ReturnValue.NOT_EXISTS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR
    except Exception as e:
        print(e)
        return ReturnValue.ERROR
    finally:
        if conn is not None:
            conn.close()


def add_order(order: Order) -> ReturnValue:
    conn = None

    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "INSERT INTO Orders (order_id, date, delivery_fee, delivery_address, tip) "
            "VALUES ({id}, {date}, {fee}, {address}, {tip})"
        ).format(
            id=sql.Literal(order.get_order_id()),
            date=sql.Literal(order.get_datetime()),
            fee=sql.Literal(order.get_delivery_fee()),
            address=sql.Literal(order.get_delivery_address()),
            tip=sql.Literal(order.get_tip()),
        )

        conn.execute(query)
        return ReturnValue.OK

    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS

    except (DatabaseException.NOT_NULL_VIOLATION, DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def get_order(order_id: int) -> Order:
    conn = None
    order = BadOrder()

    try:
        conn = Connector.DBConnector()

        query = sql.SQL("SELECT * FROM Orders WHERE order_id={id}").format(
            id=sql.Literal(order_id)
        )

        rows_effected, result = conn.execute(query)

        if rows_effected > 0:
            row = result[0]

            order = _map_row_to_order(row)

    except DatabaseException.ConnectionInvalid as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
        return order


def delete_order(order_id: int) -> ReturnValue:
    conn = None

    try:
        conn = Connector.DBConnector()

        query = sql.SQL("DELETE FROM Orders WHERE order_id={id}").format(
            id=sql.Literal(order_id)
        )

        rows_effected, _ = conn.execute(query)

        if rows_effected > 0:
            return ReturnValue.OK
        else:
            return ReturnValue.NOT_EXISTS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR
    except Exception as e:
        print(e)
        return ReturnValue.ERROR
    finally:
        if conn is not None:
            conn.close()


def add_dish(dish: Dish) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "INSERT INTO Dishes (dish_id, name, price, is_active) VALUES ({id}, {name}, {price}, {is_active})"
        ).format(
            id=sql.Literal(dish.get_dish_id()),
            name=sql.Literal(dish.get_name()),
            price=sql.Literal(dish.get_price()),
            is_active=sql.Literal(dish.get_is_active()),
        )

        conn.execute(query)
        return ReturnValue.OK

    except DatabaseException.UNIQUE_VIOLATION as e:
        print(e)
        return ReturnValue.ALREADY_EXISTS

    except (
        DatabaseException.NOT_NULL_VIOLATION,
        DatabaseException.CHECK_VIOLATION,
        DatabaseException.FOREIGN_KEY_VIOLATION,
    ) as e:
        print(e)
        return ReturnValue.BAD_PARAMS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def get_dish(dish_id: int) -> Dish:
    conn = None
    dish = BadDish()

    try:
        conn = Connector.DBConnector()

        query = sql.SQL("SELECT * FROM Dishes WHERE dish_id={id}").format(
            id=sql.Literal(dish_id)
        )

        rows_effected, result = conn.execute(query)

        if rows_effected > 0:
            row = result[0]

            dish = _map_row_to_dish(row)

    except DatabaseException.ConnectionInvalid as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
        return dish


def update_dish_price(dish_id: int, price: float) -> ReturnValue:
    conn = None

    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "UPDATE Dishes SET price={price} WHERE dish_id={id} AND is_active=TRUE"
        ).format(price=sql.Literal(price), id=sql.Literal(dish_id))

        rows_effected, _ = conn.execute(query)

        if rows_effected > 0:
            return ReturnValue.OK
        else:
            return ReturnValue.NOT_EXISTS

    except (DatabaseException.NOT_NULL_VIOLATION, DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def update_dish_active_status(dish_id: int, is_active: bool) -> ReturnValue:
    conn = None

    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "UPDATE Dishes SET is_active={is_active} WHERE dish_id={id}"
        ).format(is_active=sql.Literal(is_active), id=sql.Literal(dish_id))

        rows_effected, _ = conn.execute(query)

        if rows_effected > 0:
            return ReturnValue.OK
        else:
            return ReturnValue.NOT_EXISTS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def customer_placed_order(customer_id: int, order_id: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "INSERT INTO CustomerOrders (customer_id, order_id) VALUES ({c_id}, {o_id})"
        ).format(c_id=sql.Literal(customer_id), o_id=sql.Literal(order_id))

        conn.execute(query)
        return ReturnValue.OK

    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS

    except DatabaseException.FOREIGN_KEY_VIOLATION:
        return ReturnValue.NOT_EXISTS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def get_customer_that_placed_order(order_id: int) -> Customer:
    conn = None
    customer = BadCustomer()

    try:
        conn = Connector.DBConnector()

        query = sql.SQL("SELECT * FROM vw_OrderCustomers WHERE order_id={id}").format(
            id=sql.Literal(order_id)
        )

        rows_effected, result = conn.execute(query)

        if rows_effected > 0:
            row = result[0]
            customer = _map_row_to_customer(row)

    except DatabaseException.ConnectionInvalid as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
        return customer


def order_contains_dish(order_id: int, dish_id: int, amount: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            """
                        INSERT INTO OrderDishes (order_id, dish_id, amount, price)
                        SELECT {o_id}, {d_id}, {amount}, price
                        FROM Dishes
                        WHERE dish_id = {d_id} AND is_active = TRUE
                        """
        ).format(
            o_id=sql.Literal(order_id),
            d_id=sql.Literal(dish_id),
            amount=sql.Literal(amount),
        )

        rows_effected, _ = conn.execute(query)

        if rows_effected > 0:
            return ReturnValue.OK
        else:
            return ReturnValue.NOT_EXISTS

    except DatabaseException.CHECK_VIOLATION:
        return ReturnValue.BAD_PARAMS

    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS

    except DatabaseException.FOREIGN_KEY_VIOLATION:
        return ReturnValue.NOT_EXISTS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def order_does_not_contain_dish(order_id: int, dish_id: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "DELETE FROM OrderDishes WHERE order_id = {o_id} AND dish_id = {d_id}"
        ).format(o_id=sql.Literal(order_id), d_id=sql.Literal(dish_id))

        rows_effected, _ = conn.execute(query)

        if rows_effected > 0:
            return ReturnValue.OK
        else:
            return ReturnValue.NOT_EXISTS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def get_all_order_items(order_id: int) -> List[OrderDish]:
    conn = None
    items: List[OrderDish] = []

    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "SELECT dish_id, amount, price FROM OrderDishes WHERE order_id = {o_id} ORDER BY dish_id ASC"
        ).format(o_id=sql.Literal(order_id))

        rows_effected, result = conn.execute(query)

        if rows_effected > 0:
            for row in result:
                item = OrderDish(
                    dish_id=row["dish_id"], amount=row["amount"], price=row["price"]
                )
                items.append(item)

    except DatabaseException.ConnectionInvalid as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
        return items


def customer_rated_dish(cust_id: int, dish_id: int, rating: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "INSERT INTO DishRatings (cust_id, dish_id, rating) VALUES ({c_id}, {d_id}, {rate})"
        ).format(
            c_id=sql.Literal(cust_id),
            d_id=sql.Literal(dish_id),
            rate=sql.Literal(rating),
        )

        conn.execute(query)
        return ReturnValue.OK

    except DatabaseException.UNIQUE_VIOLATION:
        return ReturnValue.ALREADY_EXISTS

    except DatabaseException.FOREIGN_KEY_VIOLATION:
        return ReturnValue.NOT_EXISTS

    except (DatabaseException.NOT_NULL_VIOLATION, DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def customer_deleted_rating_on_dish(cust_id: int, dish_id: int) -> ReturnValue:
    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "DELETE FROM DishRatings WHERE cust_id = {c_id} AND dish_id = {d_id}"
        ).format(c_id=sql.Literal(cust_id), d_id=sql.Literal(dish_id))

        rows_effected, _ = conn.execute(query)

        if rows_effected > 0:
            return ReturnValue.OK
        else:
            return ReturnValue.NOT_EXISTS

    except DatabaseException.ConnectionInvalid as e:
        print(e)
        return ReturnValue.ERROR

    except Exception as e:
        print(e)
        return ReturnValue.ERROR

    finally:
        if conn is not None:
            conn.close()


def get_all_customer_ratings(cust_id: int) -> List[Tuple[int, int]]:
    conn = None
    ratings: List[Tuple[int, int]] = []

    try:
        conn = Connector.DBConnector()

        query = sql.SQL(
            "SELECT dish_id, rating FROM DishRatings WHERE cust_id = {c_id} ORDER BY dish_id ASC"
        ).format(c_id=sql.Literal(cust_id))

        rows_effected, result = conn.execute(query)

        if rows_effected > 0:
            for row in result:
                ratings.append((row["dish_id"], row["rating"]))

    except DatabaseException.ConnectionInvalid as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
        return ratings


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
