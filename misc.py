import json
import csv


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


def find_examples(cur, find_routes):
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
                if len(find_routes((bus_stops_list[cnt1], bus_stops_list[cnt2]))) > 10:
                    print(f"ADDED: {(bus_stops_list[cnt1], bus_stops_list[cnt2])}")
                    common.append((bus_stops_list[cnt1], bus_stops_list[cnt2]))
        if not cnt1 % 10:
            print(f"AT: {cnt1}")
    print(common)