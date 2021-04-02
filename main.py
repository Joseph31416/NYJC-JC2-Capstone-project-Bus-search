import sqlite3
from flask import Flask, request, redirect, render_template
from database import create_conn, create_cur, find_routes, optimal


app = Flask(__name__)


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/routes", methods=["POST", "GET"])
def routes():
    if request.method == "GET":
        return render_template("input.html")
    else:
        conn = create_conn()
        b1 = request.form.get("BusStop1", None)
        b2 = request.form.get("BusStop2", None)
        if request.form.get("Distance", None):
            mode = "distance"
        else:
            mode = "fare"
        routes = find_routes(conn, (b1, b2))
        temp = optimal(conn, mode, b1, b2, routes)
        results = [
            tuple(x.values()) for x in temp
        ]
        keys = list(temp[0].keys())
        conn.close()
        return render_template("routes.html", results=results, keys=keys)



app.run()