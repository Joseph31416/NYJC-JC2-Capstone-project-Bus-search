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
