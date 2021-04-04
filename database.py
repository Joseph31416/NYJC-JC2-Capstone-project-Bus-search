import sqlite3
from calculation import find_max_min, insertion_sort, dist_range
import math
from fuzzywuzzy import fuzz
from config import Config


class SqlOperations:
    config = Config()

    def __init__(self):
        self.conn = sqlite3.connect(self.config.DB_PATH, check_same_thread=False)
        self.cur = self.conn.cursor()

    def get_bus_stop_code(self, bus_desc):
        query = """
                SELECT "BusStopCode"
                FROM "Bus_stops"
                WHERE "Description"=?;
                """
        self.cur.execute(query, (bus_desc,))
        return self.cur.fetchone()[0]

    def sequence_check(self, b1, b2, bus_route, direction):
        query = """
                SELECT "BusStopCode", "Direction", "StopSequence"
                FROM "bus_routes"
                WHERE "BusStopCode"=?
                AND "Direction"=?
                AND "ServiceNo"=?;
                """
        self.cur.execute(query, (b1, direction, bus_route))
        b1_list = self.cur.fetchall()
        self.cur.execute(query, (b2, direction, bus_route))
        b2_list = self.cur.fetchall()
        if find_max_min(b1_list, 2, "min") < find_max_min(b2_list, 2, "max"):
            return True
        else:
            return False

    def find_routes(self, bus_stops: tuple):
        query_1 = """
                SELECT DISTINCT "ServiceNo", "Direction"
                FROM "Bus_routes" 
                WHERE "BusStopCode"=?;
                """
        self.cur.execute(query_1, (bus_stops[0], ))
        route_set_1 = set(self.cur.fetchall())
        query_2 = """
                SELECT DISTINCT "ServiceNo", "Direction"
                FROM "Bus_routes" 
                WHERE "BusStopCode"=?;
                """
        self.cur.execute(query_2, (bus_stops[1], ))
        route_set_2 = set(self.cur.fetchall())
        working_result = list(route_set_1.intersection(route_set_2))
        result = []
        for data in working_result:
            if self.sequence_check(bus_stops[0], bus_stops[1], data[0], data[1]):
                result.append(data)
        return result

    def find_multiple_stops(self):
        query = """
                SELECT DISTINCT BusStopCode
                FROM Bus_stops;
                """
        self.cur.execute(query)
        bus_stops_list = self.cur.fetchall()
        bus_stops_list = [x[0] for x in bus_stops_list]
        n = len(bus_stops_list)
        print(f"TOTAL: {n}")
        common = []
        for cnt1 in range(n):
            for cnt2 in range(n):
                if cnt1 != cnt2:
                    if len(self.find_routes((bus_stops_list[cnt1], bus_stops_list[cnt2]))) > 10:
                        print(f"ADDED: {(bus_stops_list[cnt1], bus_stops_list[cnt2])}")
                        common.append((bus_stops_list[cnt1], bus_stops_list[cnt2]))
            if not cnt1 % 10:
                print(f"AT: {cnt1}")
        print(common)

    def optimal(self, mode: str, start, end, routes, group="adult", payment_mode="cash"):
        results = []
        group_payment = self.config.GROUP_PAYMENT
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
            self.cur.execute(query, (route[0], route[1], start, end))
            fetch = self.cur.fetchall()
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
                self.cur.execute(query, (tb_dist, ))
                fare = self.cur.fetchone()[0]
            elif category == "FEEDER":
                tb_name = "Fare_feeder"
                tb_col = group_payment[(group, payment_mode)]
                query = f"""
                        SELECT "{tb_col}"
                        FROM "{tb_name}";
                        """
                self.cur.execute(query)
                fare = self.cur.fetchone()[0]
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
                self.cur.execute(query, (tb_dist,))
                fare = self.cur.fetchone()[0]
            results.append(
                {
                    "route": route[0], "distance": distance, "fare": fare
                }
            )
            results = insertion_sort(results, "route", "asc")
            results = insertion_sort(results, mode, "asc")

        return results

    def match(self, bus_desc):
        query = """
                SELECT "Description"
                FROM "Bus_stops";
                """
        self.cur.execute(query)
        reference_list = [_[0] for _ in self.cur.fetchall()]
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


#connection = create_conn()
# routes = find_routes(connection, ("01039", "01029"))
#Bugis Cube, Opp Natl Lib
# find_multiple_stops(connection)
# close_conn(connection)