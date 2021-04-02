from flask import Flask, request, redirect, render_template
from database import create_conn, find_routes, optimal


app = Flask(__name__)


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/routes", methods=["POST", "GET"])
def routes():
    err = None
    if request.method == "GET":
        return render_template("input.html", err=err)
    else:
        conn = create_conn()
        b1 = request.form.get("BusStop1", None)
        b2 = request.form.get("BusStop2", None)
        if request.form.get("mode", None) in ["distance", "fare"]:
            mode = request.form.get("mode")
        else:
            err = "Invalid option."
            return render_template("input.html", err=err)
        if request.form.get("group", None) in  ["adult", "student", "senior", "workfare", "disabilities"]:
            group = request.form.get("group")
        else:
            err = "Invalid option."
            return render_template("input.html", err=err)
        if request.form.get("payment_mode", None) in ["cash", "card"]:
            payment_mode = request.form.get("payment_mode")
        else:
            err = "Invalid option."
            return render_template("input.html", err=err)
        entry = {"start": b1, "end": b2, "mode": mode, "group": group, "payment_mode": payment_mode}
        bus_routes = find_routes(conn, (b1, b2))
        if len(bus_routes) == 0:
            err = "No direct bus between these two stops."
            return render_template("input.html", err=err)
        temp = optimal(conn, mode, b1, b2, bus_routes, group, payment_mode)
        results = [tuple(x.values()) for x in temp]
        keys = list(temp[0].keys())
        conn.close()
        return render_template("routes.html", results=results, keys=keys, entry=entry)


app.run()
