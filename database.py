import sqlite3
from calculation import find_max_min, insertion_sort, dist_range
import math


class SqlOperations:
    """
    Methods: get_all_bus_stops, get_bus_stop_code, sequence_check, find_routes, optimal
    Attributes: config, conn, cur
    """

    def __init__(self, config):
        self.config = config
        self.conn = sqlite3.connect(self.config.DB_PATH, check_same_thread=False)
        self.cur = self.conn.cursor()

    def get_all_bus_stops(self):
        """
        Returns a python list of bus stop descriptions and road names, concatenated by a comma.
        E.g: 112 Katong and Joo Chiat Rd is concatenated to form 112 Katong, Joo Chiat Rd
        """
        query = """
                SELECT DISTINCT "Description", "RoadName"
                FROM "Bus_stops"
                ORDER BY "Description";
                """
        self.cur.execute(query)
        results = [", ".join(_) for _ in self.cur.fetchall()]
        return results

    def get_bus_stop_code(self, bus_desc, bus_road_name):
        """
        :param bus_desc: Bus stop description
        :param bus_road_name: Bus stop road name
        :return: Returns a unique bus stop code when given the bus stop description and road name
        """
        query = """
                SELECT "BusStopCode"
                FROM "Bus_stops"
                WHERE "Description"=?
                AND "RoadName"=?;
                """
        self.cur.execute(query, (bus_desc, bus_road_name))
        return self.cur.fetchone()[0]

    def sequence_check(self, b1, b2, bus_route, direction):
        """
        :param b1: bus stop code of starting point
        :param b2: bus stop code of destination
        :param bus_route: a list of potential bus routes that contain both bus stops
        :param direction: the direction of the bus route
        :return: checks for the order of the bus stops on the bus routes and ensures that the bus stop of the starting
        point comes after the bus stop of the destination on the bus route
        """
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
        """
        :param bus_stops: takes in a tuple containing the starting and ending bus stop codes
        :return: return a list of routes containing both bus stops
        """
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

    def optimal(self, mode: str, start, end, routes, group="adult", payment_mode="cash"):
        """
        :param mode: mode for sorting
        :param start: bus stop code of starting point
        :param end: bus stop code of destination
        :param routes: list of all routes containing both bus stops
        :param group: citizen group that the user falls under, e.g. student, senior etc
        :param payment_mode: user's mode of payment
        :return:
        """
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
                    "route": route[0], "distance": distance, "fare": int(fare)
                }
            )
        results = insertion_sort(results, "route")
        if mode == "distance":
            results = insertion_sort(results, "fare")
            results = insertion_sort(results, "distance")
        else:
            results = insertion_sort(results, "distance")
            results = insertion_sort(results, "fare")
        return results
