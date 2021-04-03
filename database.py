import sqlite3
import json
from calculation import quick_sort, find_max_min, insertion_sort, dist_range
import math
import csv
from fuzzywuzzy import fuzz


def create_conn():
    return sqlite3.connect("records.db")


def close_conn(conn):
    conn.close()


def data_retrieval(filename):
    with open(f"./bus_data/{filename}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def data_retrieval_fare(filename):
    with open(f"./fare_data/{filename}.csv") as f:
        reader = csv.reader(f)
        return [row for row in reader]


def insertion(conn):
    delete = """DELETE FROM "Bus_services" """
    cur = conn.cursor()
    cur.execute(delete)
    conn.commit()
    insert = """
            INSERT INTO "Bus_services" VALUES (?, ?, ?, ?, ?);
            """
    for entry in data_retrieval("bus_services"):
        print(entry)
        cur.execute(insert, (entry["ServiceNo"], entry["Category"],
                             entry["Direction"], entry["OriginCode"], entry["DestinationCode"]))
    conn.commit()


def get_bus_stop_code(conn, bus_desc):
    query = """
            SELECT "BusStopCode"
            FROM "Bus_stops"
            WHERE "Description"=?;
            """
    cur = conn.cursor()
    cur.execute(query, (bus_desc, ))
    return cur.fetchone()[0]


def sequence_check(conn, b1, b2, bus_route, direction):
    cur = conn.cursor()
    query = """
            SELECT "BusStopCode", "Direction", "StopSequence"
            FROM "bus_routes"
            WHERE "BusStopCode"=?
            AND "Direction"=?
            AND "ServiceNo"=?;
            """
    cur.execute(query, (b1, direction, bus_route))
    b1_list = cur.fetchall()
    cur.execute(query, (b2, direction, bus_route))
    b2_list = cur.fetchall()
    if find_max_min(b1_list, 2, "min") < find_max_min(b2_list, 2, "max"):
        return True
    else:
        return False


def find_routes(conn, bus_stops: tuple):
    cur = conn.cursor()
    query_1 = """
            SELECT DISTINCT "ServiceNo", "Direction"
            FROM "Bus_routes" 
            WHERE "BusStopCode"=?;
            """
    cur.execute(query_1, (bus_stops[0], ))
    route_set_1 = set(cur.fetchall())
    query_2 = """
            SELECT DISTINCT "ServiceNo", "Direction"
            FROM "Bus_routes" 
            WHERE "BusStopCode"=?;
            """
    cur.execute(query_2, (bus_stops[1], ))
    route_set_2 = set(cur.fetchall())
    working_result = list(route_set_1.intersection(route_set_2))
    result = []
    for data in working_result:
        if sequence_check(conn, bus_stops[0], bus_stops[1], data[0], data[1]):
            result.append(data)
    return result


def find_multiple_stops(conn):
    cur = conn.cursor()
    query = """
            SELECT DISTINCT BusStopCode
            FROM Bus_stops;
            """
    cur.execute(query)
    bus_stops_list = cur.fetchall()
    bus_stops_list = [x[0] for x in bus_stops_list]
    n = len(bus_stops_list)
    print(f"TOTAL: {n}")
    common = []
    for cnt1 in range(n):
        for cnt2 in range(n):
            if cnt1 != cnt2:
                if len(find_routes(conn, (bus_stops_list[cnt1], bus_stops_list[cnt2]))) > 3:
                    print(f"ADDED: {(bus_stops_list[cnt1], bus_stops_list[cnt2])}")
                    common.append((bus_stops_list[cnt1], bus_stops_list[cnt2]))
        if not cnt1 % 10:
            print(f"AT: {cnt1}")
    print(common)


def optimal(conn, mode: str, start, end,
            routes, group="adult", payment_mode="cash"):
        cur = conn.cursor()
        results = []
        group_payment = {
            ("adult", "cash"): "Adult_cash_fare",
            ("adult", "card"): "Adult_card_fare",
            ("senior", "cash"): "Senior_cash_fare",
            ("senior", "card"): "Senior_card_fare",
            ("student", "cash"): "Student_cash_fare",
            ("student", "card"): "Student_card_fare",
            ("workfare", "cash"): "Workfare_cash_fare",
            ("workfare", "card"): "Workfare_card_fare",
            ("disabilities", "cash"): "Disabilities_cash_fare",
            ("disabilities", "card"): "Disabilities_card_fare"
        }
        for route in routes:
            query = """
                    SELECT DISTINCT "Bus_routes"."BusStopCode", "Bus_routes"."Direction",
                     "Bus_routes"."StopSequence", "Bus_routes"."Distance", "Bus_services"."Category"
                    FROM "Bus_routes"
                    INNER JOIN "Bus_services"
                    ON ("Bus_routes"."ServiceNo"="Bus_services"."ServiceNo" AND 
                     "Bus_routes"."Direction"="Bus_services"."Direction")
                    WHERE "Bus_routes"."ServiceNo"=? 
                    AND "Bus_routes"."Direction"=?
                    AND ("Bus_routes"."BusStopCode"=? 
                    OR "Bus_routes"."BusStopCode"=?);
                    """
            cur.execute(query, (route[0], route[1], start, end))
            fetch = cur.fetchall()
            distance = round(math.fabs(fetch[0][3] - fetch[1][3]), 2)
            category = fetch[0][4]
            if category == "TRUNK":
                tb_name = "Fare_trunk"
                tb_dist = dist_range(distance)
                tb_col = group_payment[(group, payment_mode)]
                query = f"""
                        SELECT "{tb_col}"
                        FROM "{tb_name}"
                        WHERE "Distance"=?;
                        """
                cur.execute(query, (tb_dist, ))
                fare = cur.fetchone()[0]
            elif category == "FEEDER":
                tb_name = "Fare_feeder"
                tb_col = group_payment[(group, payment_mode)]
                query = f"""
                        SELECT "{tb_col}"
                        FROM "{tb_name}";
                        """
                cur.execute(query)
                fare = cur.fetchone()[0]
            else:
                tb_name = "Fare_express"
                tb_dist = dist_range(distance)
                if payment_mode == "cash":
                    tb_col = "Cash_fare"
                else:
                    tb_col = f"{group}_card_fare".title()
                query = f"""
                        SELECT "{tb_col}"
                        FROM "{tb_name}"
                        WHERE "Distance"=?;
                        """
                cur.execute(query, (tb_dist,))
                fare = cur.fetchone()[0]
            results.append(
                {
                    "route": route[0], "distance": distance, "fare": fare
                }
            )
            results = insertion_sort(results, "route", "asc")
            results = insertion_sort(results, mode, "asc")

        return results


def match(conn, bus_desc):
    cur = conn.cursor()
    query = """
            SELECT "Description"
            FROM "Bus_stops";
            """
    cur.execute(query)
    reference_list = [_[0] for _ in cur.fetchall()]
    suggestion = None
    m = None
    for reference in reference_list:
        score = fuzz.token_set_ratio(bus_desc, reference)
        if m is None:
            m = score
            suggestion = reference
        elif m < score:
            m = score
            suggestion = reference
    return suggestion


connection = create_conn()
# routes = find_routes(connection, ("01012", "01311"))
# find_multiple_stops(connection)
# print(optimal(connection, "fare", "01012", "01311", routes, "student", "card"))
close_conn(connection)