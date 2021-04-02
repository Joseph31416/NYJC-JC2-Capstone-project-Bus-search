import sqlite3
import json
from calculation import quick_sort, find_max_min, insertion_sort
import math


def create_conn():
    return sqlite3.connect("records.db")


def create_cur(conn):
    return conn.cursor()


def close_conn(conn):
    conn.close()


def data_retrieval(filename):
    with open(f"./bus_data/{filename}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def insertion(conn, cur):
    delete = """DELETE FROM "Bus_routes" """
    cur.execute(delete)
    conn.commit()
    insert = """
            INSERT INTO "Bus_routes" VALUES (?, ?, ?, ?, ?);
            """
    for entry in data_retrieval("bus_routes"):
        print(entry)
        cur.execute(insert, (entry["ServiceNo"], entry["Direction"],
                             entry["StopSequence"], entry["BusStopCode"], entry["Distance"]))
    conn.commit()


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


def optimal(conn, mode: str, start, end, routes):
        cur = create_cur(conn)
        results = []
        if mode == "distance":
            for route in routes:
                query = """
                        SELECT DISTINCT "BusStopCode", "Direction", "StopSequence", "Distance"
                        FROM "Bus_routes"
                        WHERE "ServiceNo"=? 
                        AND "Direction"=?
                        AND ("BusStopCode"=? 
                        OR "BusStopCode"=?);
                        """
                cur.execute(query, (route[0], route[1], start, end))
                fetch = cur.fetchall()
                results.append(
                    {
                        "route": route[0], "distance": round(math.fabs(fetch[0][3] - fetch[1][3]), 4)
                    }
                )
        results = insertion_sort(results, "route", "asc")
        results = insertion_sort(results, "distance", "asc")
        return results



connection = create_conn()
routes = find_routes(connection, ("01012", "01311"))
print(f"routes: {routes}")
# find_multiple_stops(connection)
print(optimal(connection, "distance", "01012", "01311", routes))
close_conn(connection)